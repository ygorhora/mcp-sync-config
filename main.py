#!/usr/bin/env python3
"""
MCP Server Configuration Sync Tool
Syncs MCP servers between mcpServers.json and ~/.claude.json
"""

import json
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import questionary
from questionary import Choice


def load_json_file(filepath: Path, create_if_missing: bool = False) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        if create_if_missing:
            print(f"File not found: {filepath}")
            print(f"Creating empty {filepath.name}...")
            with open(filepath, 'w') as f:
                json.dump({}, f, indent=2)
            print(f"Created {filepath}")
            print("\nNote: The file is empty. Please add your MCP server configurations to this file.")
            print("See mcpServers.json.example for reference.")
            return {}
        else:
            print(f"Error: File not found: {filepath}")
            sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {filepath}: {e}")
        sys.exit(1)


def save_json_file(filepath: Path, data: Dict[str, Any], create_backup: bool = True) -> None:
    """Save data to a JSON file, optionally creating a backup."""
    if create_backup and filepath.exists():
        backup_path = filepath.with_suffix(f'.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
        with open(backup_path, 'w') as f:
            json.dump(load_json_file(filepath), f, indent=2)
        print(f"Created backup: {backup_path}")
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Updated: {filepath}")


def get_current_mcp_servers(claude_config: Dict[str, Any], project_path: Optional[str] = None) -> Dict[str, Any]:
    """Get current MCP servers configuration for global or specific project."""
    if project_path:
        projects = claude_config.get('projects', {})
        if project_path in projects:
            return projects[project_path].get('mcpServers', {})
        else:
            # Create project entry if it doesn't exist
            return {}
    else:
        return claude_config.get('mcpServers', {})


def set_mcp_servers(claude_config: Dict[str, Any], mcp_servers: Dict[str, Any], project_path: Optional[str] = None) -> None:
    """Set MCP servers configuration for global or specific project."""
    if project_path:
        if 'projects' not in claude_config:
            claude_config['projects'] = {}
        if project_path not in claude_config['projects']:
            claude_config['projects'][project_path] = {
                'allowedTools': [],
                'history': [],
                'mcpContextUris': [],
                'mcpServers': {},
                'enabledMcpjsonServers': [],
                'disabledMcpjsonServers': [],
                'hasTrustDialogAccepted': False,
                'projectOnboardingSeenCount': 0,
                'hasClaudeMdExternalIncludesApproved': False,
                'hasClaudeMdExternalIncludesWarningShown': False
            }
        claude_config['projects'][project_path]['mcpServers'] = mcp_servers
    else:
        claude_config['mcpServers'] = mcp_servers


def create_server_choices(available_servers: Dict[str, Any], current_servers: Dict[str, Any]) -> List[Choice]:
    """Create questionary choices for server selection."""
    choices = []
    for server_name, server_config in available_servers.items():
        # Check if server is currently enabled
        is_enabled = server_name in current_servers
        
        # Create a descriptive label
        if 'type' in server_config and server_config['type'] == 'sse':
            label = f"{server_name} (SSE: {server_config.get('url', 'N/A')})"
        elif 'command' in server_config:
            label = f"{server_name} (Command: {server_config.get('command', 'N/A')})"
        else:
            label = server_name
        
        choices.append(Choice(
            title=label,
            value=server_name,
            checked=is_enabled
        ))
    
    return sorted(choices, key=lambda x: x.title)


def sync_mcp_servers(available_servers: Dict[str, Any], selected_names: List[str]) -> Dict[str, Any]:
    """Create new MCP servers configuration based on selection."""
    new_servers = {}
    for name in selected_names:
        if name in available_servers:
            new_servers[name] = available_servers[name]
    return new_servers


def main():
    parser = argparse.ArgumentParser(description='Sync MCP servers between mcpServers.json and ~/.claude.json')
    parser.add_argument('--project', '-p', type=str, help='Project path to update (defaults to global mcpServers)')
    parser.add_argument('--mcp-file', '-m', type=str, default='mcpServers.json', help='Path to mcpServers.json file')
    parser.add_argument('--claude-config', '-c', type=str, default='~/.claude.json', help='Path to .claude.json file')
    args = parser.parse_args()
    
    # Resolve paths
    mcp_file_path = Path(args.mcp_file).resolve()
    claude_config_path = Path(args.claude_config).expanduser().resolve()
    
    # Load configurations
    available_servers = load_json_file(mcp_file_path, create_if_missing=True)
    claude_config = load_json_file(claude_config_path)
    
    # Check if no MCP servers are available
    if not available_servers:
        print("\nNo MCP servers found in mcpServers.json!")
        print("Please add your MCP server configurations to the file.")
        print("You can use mcpServers.json.example as a reference.")
        print("\nExample configuration:")
        print('  "server-name": {')
        print('    "type": "sse",')
        print('    "url": "http://localhost:8765/mcp/claude/sse"')
        print('  }')
        sys.exit(0)
    
    # Get current MCP servers
    current_servers = get_current_mcp_servers(claude_config, args.project)
    
    # Display target information
    if args.project:
        print(f"Syncing MCP servers for project: {args.project}")
    else:
        print("Syncing global MCP servers")
    
    print(f"Available servers: {len(available_servers)}")
    print(f"Currently enabled: {len(current_servers)}")
    print()
    
    # Create interactive selection
    choices = create_server_choices(available_servers, current_servers)
    
    selected = questionary.checkbox(
        "Select MCP servers to enable (use arrow keys to navigate, space to select/deselect, enter to confirm):",
        choices=choices
    ).ask()
    
    if selected is None:
        print("Operation cancelled.")
        return
    
    # Create new configuration
    new_servers = sync_mcp_servers(available_servers, selected)
    
    # Show changes
    enabled_before = set(current_servers.keys())
    enabled_after = set(new_servers.keys())
    
    newly_enabled = enabled_after - enabled_before
    newly_disabled = enabled_before - enabled_after
    
    if newly_enabled:
        print(f"\nEnabling servers: {', '.join(sorted(newly_enabled))}")
    if newly_disabled:
        print(f"Disabling servers: {', '.join(sorted(newly_disabled))}")
    
    if not newly_enabled and not newly_disabled:
        print("\nNo changes to make.")
        return
    
    # Confirm changes
    if not questionary.confirm("Apply these changes?").ask():
        print("Operation cancelled.")
        return
    
    # Update configuration
    set_mcp_servers(claude_config, new_servers, args.project)
    
    # Save updated configuration
    save_json_file(claude_config_path, claude_config)
    
    print("\nSync completed successfully!")


if __name__ == "__main__":
    main()