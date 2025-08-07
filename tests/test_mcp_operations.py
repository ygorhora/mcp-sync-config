"""Tests for MCP server operations."""

import pytest
from pathlib import Path
from questionary import Choice

# Import functions from main module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import (
    get_current_mcp_servers,
    set_mcp_servers,
    create_server_choices,
    sync_mcp_servers
)


class TestGetCurrentMcpServers:
    """Test get_current_mcp_servers function."""
    
    def test_get_global_mcp_servers(self, sample_claude_config):
        """Test getting global MCP servers."""
        result = get_current_mcp_servers(sample_claude_config, project_path=None)
        
        assert result == {
            "test-server-1": {
                "type": "sse",
                "url": "http://localhost:8001/mcp/sse"
            }
        }
    
    def test_get_project_mcp_servers(self, sample_claude_config):
        """Test getting project-specific MCP servers."""
        result = get_current_mcp_servers(
            sample_claude_config, 
            project_path="/home/test/project1"
        )
        
        assert "test-postgres" in result
        assert result["test-postgres"]["command"] == "docker"
    
    def test_get_mcp_servers_missing_project(self, sample_claude_config):
        """Test getting MCP servers for non-existent project."""
        result = get_current_mcp_servers(
            sample_claude_config,
            project_path="/home/test/missing"
        )
        
        assert result == {}
    
    def test_get_mcp_servers_empty_config(self, empty_claude_config):
        """Test getting MCP servers from empty config."""
        result = get_current_mcp_servers(empty_claude_config, project_path=None)
        assert result == {}


class TestSetMcpServers:
    """Test set_mcp_servers function."""
    
    def test_set_global_mcp_servers(self, sample_claude_config):
        """Test setting global MCP servers."""
        new_servers = {"new-server": {"type": "sse", "url": "http://new"}}
        
        set_mcp_servers(sample_claude_config, new_servers, project_path=None)
        
        assert sample_claude_config["mcpServers"] == new_servers
        # Ensure other settings preserved
        assert sample_claude_config["otherSettings"] == "preserved"
    
    def test_set_project_mcp_servers_existing(self, sample_claude_config):
        """Test setting MCP servers for existing project."""
        new_servers = {"new-server": {"type": "sse", "url": "http://new"}}
        project_path = "/home/test/project1"
        
        set_mcp_servers(sample_claude_config, new_servers, project_path=project_path)
        
        assert sample_claude_config["projects"][project_path]["mcpServers"] == new_servers
        # Ensure other project settings preserved
        assert sample_claude_config["projects"][project_path]["allowedTools"] == []
    
    def test_set_project_mcp_servers_new(self, sample_claude_config):
        """Test setting MCP servers for new project."""
        new_servers = {"new-server": {"type": "sse", "url": "http://new"}}
        project_path = "/home/test/new-project"
        
        set_mcp_servers(sample_claude_config, new_servers, project_path=project_path)
        
        assert project_path in sample_claude_config["projects"]
        assert sample_claude_config["projects"][project_path]["mcpServers"] == new_servers
        
        # Check default project settings
        project_config = sample_claude_config["projects"][project_path]
        assert project_config["allowedTools"] == []
        assert project_config["history"] == []
        assert project_config["hasTrustDialogAccepted"] is False
    
    def test_set_mcp_servers_empty_config(self):
        """Test setting MCP servers in empty config."""
        config = {}
        new_servers = {"server": {"type": "sse", "url": "http://test"}}
        
        set_mcp_servers(config, new_servers, project_path=None)
        
        assert config["mcpServers"] == new_servers


class TestCreateServerChoices:
    """Test create_server_choices function."""
    
    def test_create_choices_with_mixed_servers(self, sample_mcp_servers):
        """Test creating choices with SSE and command servers."""
        current_servers = {"test-server-1": {}}
        
        choices = create_server_choices(sample_mcp_servers, current_servers)
        
        # Check number of choices
        assert len(choices) == 3
        
        # Check choices are sorted by title
        titles = [c.title for c in choices]
        assert titles == sorted(titles)
        
        # Check server types in labels
        server1_choice = next(c for c in choices if c.value == "test-server-1")
        assert "SSE:" in server1_choice.title
        assert server1_choice.checked is True
        
        postgres_choice = next(c for c in choices if c.value == "test-postgres")
        assert "Command:" in postgres_choice.title
        assert postgres_choice.checked is False
    
    def test_create_choices_all_enabled(self, sample_mcp_servers):
        """Test creating choices when all servers are enabled."""
        choices = create_server_choices(sample_mcp_servers, sample_mcp_servers)
        
        for choice in choices:
            assert choice.checked is True
    
    def test_create_choices_none_enabled(self, sample_mcp_servers):
        """Test creating choices when no servers are enabled."""
        choices = create_server_choices(sample_mcp_servers, {})
        
        for choice in choices:
            assert choice.checked is False
    
    def test_create_choices_unknown_server_type(self):
        """Test creating choices with unknown server type."""
        servers = {"unknown": {"something": "else"}}
        choices = create_server_choices(servers, {})
        
        assert len(choices) == 1
        assert choices[0].title == "unknown"
        assert choices[0].value == "unknown"


class TestSyncMcpServers:
    """Test sync_mcp_servers function."""
    
    def test_sync_selected_servers(self, sample_mcp_servers):
        """Test syncing selected servers."""
        selected = ["test-server-1", "test-postgres"]
        
        result = sync_mcp_servers(sample_mcp_servers, selected)
        
        assert len(result) == 2
        assert "test-server-1" in result
        assert "test-postgres" in result
        assert "test-server-2" not in result
        
        # Verify full server configs are copied
        assert result["test-server-1"] == sample_mcp_servers["test-server-1"]
        assert result["test-postgres"] == sample_mcp_servers["test-postgres"]
    
    def test_sync_no_servers_selected(self, sample_mcp_servers):
        """Test syncing with no servers selected."""
        result = sync_mcp_servers(sample_mcp_servers, [])
        assert result == {}
    
    def test_sync_nonexistent_server(self, sample_mcp_servers):
        """Test syncing with non-existent server in selection."""
        selected = ["test-server-1", "non-existent"]
        
        result = sync_mcp_servers(sample_mcp_servers, selected)
        
        assert len(result) == 1
        assert "test-server-1" in result
        assert "non-existent" not in result
    
    def test_sync_all_servers(self, sample_mcp_servers):
        """Test syncing all available servers."""
        selected = list(sample_mcp_servers.keys())
        
        result = sync_mcp_servers(sample_mcp_servers, selected)
        
        assert result == sample_mcp_servers