"""Tests for CLI and argument parsing."""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Import functions from main module
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import main, run_sync


class TestArgumentParsing:
    """Test command line argument parsing."""

    def test_default_arguments(self):
        """Test default argument values."""
        with patch("sys.argv", ["main.py"]):
            with patch("main.run_sync") as mock_run:
                try:
                    main()
                except SystemExit:
                    pass

                args = mock_run.call_args[0][0]
                assert args.project is None
                assert args.mcp_file == "mcpServers.json"
                assert args.url is None
                assert args.edit is False
                assert args.binding is False
                assert args.claude_config == "~/.claude.json"
                assert args.clean is False

    def test_clean_argument(self):
        """Test --clean argument."""
        with patch("sys.argv", ["main.py", "--clean"]):
            with patch("main.run_sync") as mock_run:
                try:
                    main()
                except SystemExit:
                    pass

                args = mock_run.call_args[0][0]
                assert args.clean is True

    def test_project_argument(self):
        """Test --project argument."""
        with patch("sys.argv", ["main.py", "--project", "/test/project"]):
            with patch("main.run_sync") as mock_run:
                try:
                    main()
                except SystemExit:
                    pass

                args = mock_run.call_args[0][0]
                assert args.project == "/test/project"

    def test_url_argument(self):
        """Test --url argument."""
        with patch("sys.argv", ["main.py", "--url", "http://example.com/mcp.json"]):
            with patch("main.run_sync") as mock_run:
                try:
                    main()
                except SystemExit:
                    pass

                args = mock_run.call_args[0][0]
                assert args.url == "http://example.com/mcp.json"

    def test_edit_argument(self):
        """Test --edit argument."""
        with patch("sys.argv", ["main.py", "--edit"]):
            with patch("main.run_sync") as mock_run:
                try:
                    main()
                except SystemExit:
                    pass

                args = mock_run.call_args[0][0]
                assert args.edit is True

    def test_edit_with_url_error(self, capsys):
        """Test that --edit with --url causes error."""
        with patch("sys.argv", ["main.py", "--edit", "--url", "http://example.com"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

            captured = capsys.readouterr()
            assert "Error: --edit option cannot be used with --url" in captured.out

    def test_binding_argument(self):
        """Test --binding argument."""
        with patch("sys.argv", ["main.py", "--binding"]):
            with patch("main.run_sync") as mock_run:
                try:
                    main()
                except SystemExit:
                    pass

                args = mock_run.call_args[0][0]
                assert args.binding is True

    def test_binding_with_url_error(self, capsys):
        """Test that --binding with --url causes error."""
        with patch("sys.argv", ["main.py", "--binding", "--url", "http://example.com"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

            captured = capsys.readouterr()
            assert "Error: --binding option cannot be used with --url" in captured.out


class TestRunSync:
    """Test run_sync function flow."""

    @patch("main.load_json_file")
    @patch("main.load_json_from_url")
    def test_empty_mcp_servers_from_file(self, mock_load_url, mock_load_file, mock_args, capsys):
        """Test handling of empty MCP servers from file."""
        mock_args.url = None
        mock_load_file.return_value = {}

        with pytest.raises(SystemExit) as exc_info:
            run_sync(mock_args)

        assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert "No MCP servers found" in captured.out
        assert "mcpServers.json.example" in captured.out

    @patch("main.load_json_file")
    @patch("main.load_json_from_url")
    def test_empty_mcp_servers_from_url(self, mock_load_url, mock_load_file, mock_args, capsys):
        """Test handling of empty MCP servers from URL."""
        mock_args.url = "http://example.com/empty.json"
        mock_load_url.return_value = {}

        with pytest.raises(SystemExit) as exc_info:
            run_sync(mock_args)

        assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert "No MCP servers found at URL" in captured.out
        assert mock_args.url in captured.out

    @patch("main.edit_json_file")
    @patch("main.load_json_file")
    def test_edit_mode_file_modified(self, mock_load, mock_edit, mock_args, capsys):
        """Test edit mode when file is modified."""
        mock_args.edit = True
        mock_args.url = None
        mock_edit.return_value = True  # File was modified
        mock_load.return_value = {"server": {}}

        # Mock questionary to avoid interactive prompts
        with patch("questionary.checkbox") as mock_checkbox:
            mock_checkbox.return_value.unsafe_ask.return_value = []

            run_sync(mock_args)

        captured = capsys.readouterr()
        assert "Opening" in captured.out
        assert "File modified. Proceeding with sync" in captured.out
        assert mock_edit.called

    @patch("main.edit_json_file")
    @patch("main.load_json_file")
    def test_edit_mode_file_not_modified(self, mock_load, mock_edit, mock_args, capsys):
        """Test edit mode when file is not modified."""
        mock_args.edit = True
        mock_args.url = None
        mock_edit.return_value = False  # File was not modified
        mock_load.return_value = {"server": {}}

        # Mock questionary to avoid interactive prompts
        with patch("questionary.checkbox") as mock_checkbox:
            mock_checkbox.return_value.unsafe_ask.return_value = []

            run_sync(mock_args)

        captured = capsys.readouterr()
        assert "No changes detected or edit cancelled" in captured.out

    @patch("main.load_json_file")
    @patch("questionary.checkbox")
    def test_no_changes_to_make(self, mock_checkbox, mock_load, mock_args, capsys):
        """Test when no changes are needed."""
        mock_args.url = None
        mock_load.side_effect = [
            {"server1": {}},  # MCP servers
            {"mcpServers": {"server1": {}}},  # Claude config with same server
        ]

        # User selects same server that's already enabled
        mock_checkbox.return_value.unsafe_ask.return_value = ["server1"]

        run_sync(mock_args)

        captured = capsys.readouterr()
        assert "No changes to make" in captured.out

    @patch("main.load_json_file")
    @patch("main.save_json_file")
    @patch("questionary.checkbox")
    @patch("questionary.confirm")
    def test_successful_sync(self, mock_confirm, mock_checkbox, mock_save, mock_load, mock_args, capsys):
        """Test successful sync operation."""
        mock_args.url = None
        mock_args.project = None

        # Setup file loading
        mock_load.side_effect = [
            {"server1": {"type": "sse"}, "server2": {"type": "sse"}},  # MCP servers
            {"mcpServers": {"server1": {}}},  # Claude config
        ]

        # User enables server2
        mock_checkbox.return_value.unsafe_ask.return_value = ["server1", "server2"]
        mock_confirm.return_value.unsafe_ask.return_value = True

        run_sync(mock_args)

        captured = capsys.readouterr()
        assert "Syncing global MCP servers" in captured.out
        assert "Enabling servers: server2" in captured.out
        assert "Sync completed successfully!" in captured.out
        assert mock_save.called

    @patch("main.load_json_file")
    @patch("questionary.checkbox")
    def test_user_cancels_selection(self, mock_checkbox, mock_load, mock_args, capsys):
        """Test when user cancels during selection."""
        mock_args.url = None
        mock_load.side_effect = [
            {"server1": {}},  # MCP servers
            {"mcpServers": {}},  # Claude config
        ]

        # User cancels (returns None)
        mock_checkbox.return_value.unsafe_ask.return_value = None

        with pytest.raises(SystemExit) as exc_info:
            run_sync(mock_args)

        assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert "Operation cancelled" in captured.out

    def test_binding_mode_with_new_servers(self, capsys, mock_args, temp_dir):
        """Test binding mode when there are new servers in .claude.json."""
        mock_args.binding = True
        mock_args.mcp_file = str(temp_dir / "mcpServers.json")
        mock_args.claude_config = str(temp_dir / "claude.json")

        # Create files with different servers
        mcp_servers = {"server1": {"type": "sse", "url": "http://test1"}}
        claude_config = {
            "mcpServers": {
                "server1": {"type": "sse", "url": "http://test1"},
                "server2": {"type": "sse", "url": "http://test2"},  # New server
            }
        }

        with open(mock_args.mcp_file, "w") as f:
            json.dump(mcp_servers, f)
        with open(mock_args.claude_config, "w") as f:
            json.dump(claude_config, f)

        with patch("questionary.checkbox") as mock_checkbox:
            mock_checkbox.return_value.unsafe_ask.return_value = ["server1", "server2"]

            with patch("questionary.confirm") as mock_confirm:
                mock_confirm.return_value.unsafe_ask.return_value = True

                run_sync(mock_args)

        # Check that mcpServers.json was updated
        with open(mock_args.mcp_file) as f:
            updated_mcp = json.load(f)

        assert "server2" in updated_mcp
        assert updated_mcp["server2"]["url"] == "http://test2"

        captured = capsys.readouterr()
        assert "Found 1 server(s) in .claude.json not in mcpServers.json" in captured.out
        assert "server2" in captured.out
        assert "Added 1 server(s) to mcpServers.json" in captured.out

    def test_binding_mode_no_new_servers(self, capsys, mock_args, temp_dir):
        """Test binding mode when there are no new servers."""
        mock_args.binding = True
        mock_args.mcp_file = str(temp_dir / "mcpServers.json")
        mock_args.claude_config = str(temp_dir / "claude.json")

        # Create files with same servers
        servers = {"server1": {"type": "sse", "url": "http://test1"}}

        with open(mock_args.mcp_file, "w") as f:
            json.dump(servers, f)
        with open(mock_args.claude_config, "w") as f:
            json.dump({"mcpServers": servers}, f)

        with patch("questionary.checkbox") as mock_checkbox:
            mock_checkbox.return_value.unsafe_ask.return_value = ["server1"]

            with patch("questionary.confirm") as mock_confirm:
                mock_confirm.return_value.unsafe_ask.return_value = True

                run_sync(mock_args)

        captured = capsys.readouterr()
        assert "No new servers found in .claude.json to add to mcpServers.json" in captured.out

    def test_clean_mode_with_backups(self, capsys, mock_args, temp_dir):
        """Test clean mode when backup files exist."""
        mock_args.clean = True
        mock_args.claude_config = str(temp_dir / ".claude.json")
        
        # Create some backup files
        backup1 = temp_dir / ".claude.backup.20240101_120000.json"
        backup2 = temp_dir / ".claude.backup.20240102_130000.json"
        
        backup1.write_text('{"test": "backup1"}')
        backup2.write_text('{"test": "backup2"}')
        
        # Mock questionary to confirm deletion
        with patch("questionary.confirm") as mock_confirm:
            mock_confirm.return_value.ask.return_value = True
            
            run_sync(mock_args)
        
        # Check that backup files were deleted
        assert not backup1.exists()
        assert not backup2.exists()
        
        captured = capsys.readouterr()
        assert "Found 2 backup file(s):" in captured.out
        assert ".claude.backup.20240101_120000.json" in captured.out
        assert ".claude.backup.20240102_130000.json" in captured.out
        assert "✓ Deleted 2 backup file(s)" in captured.out

    def test_clean_mode_no_backups(self, capsys, mock_args, temp_dir):
        """Test clean mode when no backup files exist."""
        mock_args.clean = True
        mock_args.claude_config = str(temp_dir / ".claude.json")
        
        run_sync(mock_args)
        
        captured = capsys.readouterr()
        assert "No backup files found." in captured.out

    def test_clean_mode_cancelled(self, capsys, mock_args, temp_dir):
        """Test clean mode when user cancels deletion."""
        mock_args.clean = True
        mock_args.claude_config = str(temp_dir / ".claude.json")
        
        # Create a backup file
        backup = temp_dir / ".claude.backup.20240101_120000.json"
        backup.write_text('{"test": "backup"}')
        
        # Mock questionary to cancel deletion
        with patch("questionary.confirm") as mock_confirm:
            mock_confirm.return_value.ask.return_value = False
            
            run_sync(mock_args)
        
        # Check that backup file still exists
        assert backup.exists()
        
        captured = capsys.readouterr()
        assert "Cancelled. No files deleted." in captured.out
