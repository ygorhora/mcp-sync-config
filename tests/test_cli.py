"""Tests for CLI and argument parsing."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import argparse
import sys

# Import functions from main module
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import main, run_sync


class TestArgumentParsing:
    """Test command line argument parsing."""
    
    def test_default_arguments(self):
        """Test default argument values."""
        with patch('sys.argv', ['main.py']):
            with patch('main.run_sync') as mock_run:
                try:
                    main()
                except SystemExit:
                    pass
                
                args = mock_run.call_args[0][0]
                assert args.project is None
                assert args.mcp_file == 'mcpServers.json'
                assert args.url is None
                assert args.edit is False
                assert args.claude_config == '~/.claude.json'
    
    def test_project_argument(self):
        """Test --project argument."""
        with patch('sys.argv', ['main.py', '--project', '/test/project']):
            with patch('main.run_sync') as mock_run:
                try:
                    main()
                except SystemExit:
                    pass
                
                args = mock_run.call_args[0][0]
                assert args.project == '/test/project'
    
    def test_url_argument(self):
        """Test --url argument."""
        with patch('sys.argv', ['main.py', '--url', 'http://example.com/mcp.json']):
            with patch('main.run_sync') as mock_run:
                try:
                    main()
                except SystemExit:
                    pass
                
                args = mock_run.call_args[0][0]
                assert args.url == 'http://example.com/mcp.json'
    
    def test_edit_argument(self):
        """Test --edit argument."""
        with patch('sys.argv', ['main.py', '--edit']):
            with patch('main.run_sync') as mock_run:
                try:
                    main()
                except SystemExit:
                    pass
                
                args = mock_run.call_args[0][0]
                assert args.edit is True
    
    def test_edit_with_url_error(self, capsys):
        """Test that --edit with --url causes error."""
        with patch('sys.argv', ['main.py', '--edit', '--url', 'http://example.com']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
            
            captured = capsys.readouterr()
            assert "Error: --edit option cannot be used with --url" in captured.out
    


class TestRunSync:
    """Test run_sync function flow."""
    
    @patch('main.load_json_file')
    @patch('main.load_json_from_url')
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
    
    @patch('main.load_json_file')
    @patch('main.load_json_from_url')
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
    
    @patch('main.edit_json_file')
    @patch('main.load_json_file')
    def test_edit_mode_file_modified(self, mock_load, mock_edit, mock_args, capsys):
        """Test edit mode when file is modified."""
        mock_args.edit = True
        mock_args.url = None
        mock_edit.return_value = True  # File was modified
        mock_load.return_value = {"server": {}}
        
        # Mock questionary to avoid interactive prompts
        with patch('questionary.checkbox') as mock_checkbox:
            mock_checkbox.return_value.unsafe_ask.return_value = []
            
            run_sync(mock_args)
        
        captured = capsys.readouterr()
        assert "Opening" in captured.out
        assert "File modified. Proceeding with sync" in captured.out
        assert mock_edit.called
    
    @patch('main.edit_json_file')
    @patch('main.load_json_file')
    def test_edit_mode_file_not_modified(self, mock_load, mock_edit, mock_args, capsys):
        """Test edit mode when file is not modified."""
        mock_args.edit = True
        mock_args.url = None
        mock_edit.return_value = False  # File was not modified
        mock_load.return_value = {"server": {}}
        
        # Mock questionary to avoid interactive prompts
        with patch('questionary.checkbox') as mock_checkbox:
            mock_checkbox.return_value.unsafe_ask.return_value = []
            
            run_sync(mock_args)
        
        captured = capsys.readouterr()
        assert "No changes detected or edit cancelled" in captured.out
    
    @patch('main.load_json_file')
    @patch('questionary.checkbox')
    def test_no_changes_to_make(self, mock_checkbox, mock_load, mock_args, capsys):
        """Test when no changes are needed."""
        mock_args.url = None
        mock_load.side_effect = [
            {"server1": {}},  # MCP servers
            {"mcpServers": {"server1": {}}}  # Claude config with same server
        ]
        
        # User selects same server that's already enabled
        mock_checkbox.return_value.unsafe_ask.return_value = ["server1"]
        
        run_sync(mock_args)
        
        captured = capsys.readouterr()
        assert "No changes to make" in captured.out
    
    @patch('main.load_json_file')
    @patch('main.save_json_file')
    @patch('questionary.checkbox')
    @patch('questionary.confirm')
    def test_successful_sync(self, mock_confirm, mock_checkbox, mock_save, mock_load, mock_args, capsys):
        """Test successful sync operation."""
        mock_args.url = None
        mock_args.project = None
        
        # Setup file loading
        mock_load.side_effect = [
            {"server1": {"type": "sse"}, "server2": {"type": "sse"}},  # MCP servers
            {"mcpServers": {"server1": {}}}  # Claude config
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
    
    @patch('main.load_json_file')
    @patch('questionary.checkbox')
    def test_user_cancels_selection(self, mock_checkbox, mock_load, mock_args, capsys):
        """Test when user cancels during selection."""
        mock_args.url = None
        mock_load.side_effect = [
            {"server1": {}},  # MCP servers
            {"mcpServers": {}}  # Claude config
        ]
        
        # User cancels (returns None)
        mock_checkbox.return_value.unsafe_ask.return_value = None
        
        with pytest.raises(SystemExit) as exc_info:
            run_sync(mock_args)
        
        assert exc_info.value.code == 0
        
        captured = capsys.readouterr()
        assert "Operation cancelled" in captured.out