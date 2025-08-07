"""Tests for file editing operations."""

import subprocess

# Import functions from main module
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))
from main import edit_json_file


class TestEditJsonFile:
    """Test edit_json_file function."""

    def test_edit_file_modified(self, temp_dir):
        """Test editing a file that gets modified."""
        test_file = temp_dir / "test.json"
        test_file.write_text('{"old": "content"}')

        # Get original mtime
        test_file.stat().st_mtime

        with patch("subprocess.run") as mock_run:
            # Simulate successful editor run
            mock_run.return_value = MagicMock(returncode=0)

            # Mock the file modification by actually touching the file
            def mock_editor_run(cmd, check=True):
                # Simulate editor modifying the file
                import time

                time.sleep(0.01)  # Small delay to ensure different mtime
                test_file.touch()
                return MagicMock(returncode=0)

            mock_run.side_effect = mock_editor_run
            result = edit_json_file(test_file)

        assert result is True
        mock_run.assert_called_once_with(["vi", str(test_file)], check=True)

    def test_edit_file_not_modified(self, temp_dir):
        """Test editing a file that doesn't get modified."""
        test_file = temp_dir / "test.json"
        test_file.write_text('{"old": "content"}')

        with patch("subprocess.run") as mock_run:
            # Simulate successful editor run
            mock_run.return_value = MagicMock(returncode=0)

            # File mtime doesn't change
            result = edit_json_file(test_file)

        assert result is False
        mock_run.assert_called_once()

    def test_edit_nonexistent_file(self, temp_dir):
        """Test editing a file that doesn't exist."""
        test_file = temp_dir / "nonexistent.json"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            # File doesn't exist, so mtime is 0
            result = edit_json_file(test_file)

        assert result is False
        mock_run.assert_called_once_with(["vi", str(test_file)], check=True)

    def test_edit_with_custom_editor(self, temp_dir, monkeypatch):
        """Test using custom editor from environment."""
        test_file = temp_dir / "test.json"
        test_file.write_text("{}")

        # Set custom editor
        monkeypatch.setenv("EDITOR", "nano")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            edit_json_file(test_file)

        mock_run.assert_called_once_with(["nano", str(test_file)], check=True)

    def test_edit_editor_fails(self, temp_dir, capsys):
        """Test when editor command fails."""
        test_file = temp_dir / "test.json"
        test_file.write_text("{}")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "vi")

            result = edit_json_file(test_file)

        assert result is False

        captured = capsys.readouterr()
        assert "Error: Failed to open editor" in captured.out

    def test_edit_general_exception(self, temp_dir, capsys):
        """Test when general exception occurs."""
        test_file = temp_dir / "test.json"
        test_file.write_text("{}")

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Something went wrong")

            result = edit_json_file(test_file)

        assert result is False

        captured = capsys.readouterr()
        assert "Error editing file:" in captured.out
        assert "Something went wrong" in captured.out

    def test_edit_file_created(self, temp_dir):
        """Test editing creates a new file."""
        test_file = temp_dir / "new.json"
        assert not test_file.exists()

        with patch("subprocess.run") as mock_run:
            # Simulate file creation during edit
            def mock_editor_create(cmd, check=True):
                test_file.write_text('{"new": "file"}')
                return MagicMock(returncode=0)

            mock_run.side_effect = mock_editor_create
            result = edit_json_file(test_file)

        assert result is True


class TestEditorIntegration:
    """Test editor integration scenarios."""

    def test_editor_with_spaces_in_path(self, temp_dir):
        """Test editing file with spaces in path."""
        test_dir = temp_dir / "dir with spaces"
        test_dir.mkdir()
        test_file = test_dir / "file with spaces.json"
        test_file.write_text("{}")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            edit_json_file(test_file)

        # Verify the full path is passed correctly
        mock_run.assert_called_once_with(["vi", str(test_file)], check=True)
        assert "dir with spaces" in mock_run.call_args[0][0][1]
        assert "file with spaces.json" in mock_run.call_args[0][0][1]
