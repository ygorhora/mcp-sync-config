"""Shared pytest fixtures and configuration."""

import json
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_mcp_servers():
    """Sample MCP servers configuration."""
    return {
        "test-server-1": {"type": "sse", "url": "http://localhost:8001/mcp/sse"},
        "test-server-2": {"type": "sse", "url": "http://localhost:8002/mcp/sse"},
        "test-postgres": {
            "command": "docker",
            "args": ["run", "--name", "test-postgres", "-i", "--rm", "postgres-mcp"],
            "env": {"DATABASE_URI": "postgresql://test:test@localhost:5432/testdb"},
        },
    }


@pytest.fixture
def sample_claude_config():
    """Sample Claude configuration."""
    return {
        "mcpServers": {"test-server-1": {"type": "sse", "url": "http://localhost:8001/mcp/sse"}},
        "projects": {
            "/home/test/project1": {
                "allowedTools": [],
                "history": [],
                "mcpContextUris": [],
                "mcpServers": {
                    "test-postgres": {
                        "command": "docker",
                        "args": ["run", "--name", "test-postgres", "-i", "--rm", "postgres-mcp"],
                        "env": {"DATABASE_URI": "postgresql://test:test@localhost:5432/testdb"},
                    }
                },
                "enabledMcpjsonServers": [],
                "disabledMcpjsonServers": [],
                "hasTrustDialogAccepted": False,
                "projectOnboardingSeenCount": 0,
                "hasClaudeMdExternalIncludesApproved": False,
                "hasClaudeMdExternalIncludesWarningShown": False,
            }
        },
        "otherSettings": "preserved",
    }


@pytest.fixture
def empty_claude_config():
    """Empty Claude configuration."""
    return {"mcpServers": {}, "projects": {}}


@pytest.fixture
def mcp_servers_file(temp_dir, sample_mcp_servers):
    """Create a temporary mcpServers.json file."""
    filepath = temp_dir / "mcpServers.json"
    with open(filepath, "w") as f:
        json.dump(sample_mcp_servers, f, indent=2)
    return filepath


@pytest.fixture
def claude_config_file(temp_dir, sample_claude_config):
    """Create a temporary claude.json file."""
    filepath = temp_dir / "claude.json"
    with open(filepath, "w") as f:
        json.dump(sample_claude_config, f, indent=2)
    return filepath


@pytest.fixture
def mock_args():
    """Mock command line arguments."""

    class Args:
        project = None
        mcp_file = "mcpServers.json"
        url = None
        edit = False
        binding = False
        claude_config = "~/.claude.json"

    return Args()
