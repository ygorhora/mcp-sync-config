"""Tests for JSON file operations."""

import json

# Import functions from main module
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
from main import load_json_file, save_json_file


class TestLoadJsonFile:
    """Test load_json_file function."""

    def test_load_valid_json_file(self, temp_dir):
        """Test loading a valid JSON file."""
        # Create test file
        test_file = temp_dir / "test.json"
        test_data = {"key": "value", "number": 42}
        with open(test_file, "w") as f:
            json.dump(test_data, f)

        # Load and verify
        result = load_json_file(test_file)
        assert result == test_data

    def test_load_missing_file_without_create(self, temp_dir):
        """Test loading a missing file without create_if_missing."""
        test_file = temp_dir / "missing.json"

        with pytest.raises(SystemExit) as exc_info:
            load_json_file(test_file, create_if_missing=False)
        assert exc_info.value.code == 1

    def test_load_missing_file_with_create(self, temp_dir, capsys):
        """Test loading a missing file with create_if_missing."""
        test_file = temp_dir / "missing.json"

        result = load_json_file(test_file, create_if_missing=True)

        # Check empty dict returned
        assert result == {}

        # Check file was created
        assert test_file.exists()
        with open(test_file) as f:
            assert json.load(f) == {}

        # Check output messages
        captured = capsys.readouterr()
        assert "File not found" in captured.out
        assert "Creating empty" in captured.out
        assert "mcpServers.json.example" in captured.out

    def test_load_invalid_json(self, temp_dir):
        """Test loading a file with invalid JSON."""
        test_file = temp_dir / "invalid.json"
        with open(test_file, "w") as f:
            f.write("{ invalid json }")

        with pytest.raises(SystemExit) as exc_info:
            load_json_file(test_file)
        assert exc_info.value.code == 1


class TestSaveJsonFile:
    """Test save_json_file function."""

    def test_save_json_file_new(self, temp_dir, capsys):
        """Test saving to a new file."""
        test_file = temp_dir / "new.json"
        test_data = {"key": "value"}

        save_json_file(test_file, test_data)

        # Verify file contents
        with open(test_file) as f:
            assert json.load(f) == test_data

        # Check output
        captured = capsys.readouterr()
        assert f"Updated: {test_file}" in captured.out

    def test_save_json_file_with_backup(self, temp_dir, capsys):
        """Test saving with backup creation."""
        test_file = temp_dir / "existing.json"
        original_data = {"old": "data"}
        new_data = {"new": "data"}

        # Create original file
        with open(test_file, "w") as f:
            json.dump(original_data, f)

        # Save with backup
        save_json_file(test_file, new_data, create_backup=True)

        # Verify new file contents
        with open(test_file) as f:
            assert json.load(f) == new_data

        # Check backup was created
        backup_files = list(temp_dir.glob("*.backup.*.json"))
        assert len(backup_files) == 1

        # Verify backup contents
        with open(backup_files[0]) as f:
            assert json.load(f) == original_data

        # Check output
        captured = capsys.readouterr()
        assert "Created backup" in captured.out
        assert f"Updated: {test_file}" in captured.out

    def test_save_json_file_without_backup(self, temp_dir, capsys):
        """Test saving without backup creation."""
        test_file = temp_dir / "existing.json"
        original_data = {"old": "data"}
        new_data = {"new": "data"}

        # Create original file
        with open(test_file, "w") as f:
            json.dump(original_data, f)

        # Save without backup
        save_json_file(test_file, new_data, create_backup=False)

        # Verify new file contents
        with open(test_file) as f:
            assert json.load(f) == new_data

        # Check no backup was created
        backup_files = list(temp_dir.glob("*.backup.*.json"))
        assert len(backup_files) == 0

        # Check output
        captured = capsys.readouterr()
        assert "Created backup" not in captured.out
        assert f"Updated: {test_file}" in captured.out
