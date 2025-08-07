#!/usr/bin/env python3
"""
MCP Server Configuration Sync Tool
Syncs MCP servers between mcpServers.json and ~/.claude.json
"""

import json
import os
import sys
import signal
import argparse
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import urllib.request
import urllib.error
import questionary
from questionary import Choice
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.keys import Keys


def signal_handler(sig, frame):
    """Handle Ctrl+C and other signals gracefully."""
    print("\nOperation cancelled.")
    sys.exit(0)


# Register signal handler
signal.signal(signal.SIGINT, signal_handler)


def load_json_from_url(url: str) -> Dict[str, Any]:
    """Load and parse JSON from a URL."""
    try:
        print(f"Fetching MCP servers from URL: {url}")
        with urllib.request.urlopen(url, timeout=10) as response:
            data = response.read()
            return json.loads(data.decode('utf-8'))
    except urllib.error.URLError as e:
        print(f"Error fetching URL: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON from URL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading from URL: {e}")
        sys.exit(1)


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


def edit_json_file(filepath: Path) -> bool:
    """Open JSON file in editor and return True if file was modified."""
    # Get the editor from environment or use vi as default
    editor = os.environ.get('EDITOR', 'vi')
    
    # Get initial modification time
    initial_mtime = filepath.stat().st_mtime if filepath.exists() else 0
    
    try:
        # Open the file in the editor
        subprocess.run([editor, str(filepath)], check=True)
        
        # Check if file was modified
        final_mtime = filepath.stat().st_mtime if filepath.exists() else 0
        return final_mtime != initial_mtime
    except subprocess.CalledProcessError:
        print(f"Error: Failed to open editor '{editor}'")
        return False
    except Exception as e:
        print(f"Error editing file: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Sync MCP servers between mcpServers.json and ~/.claude.json')
    parser.add_argument('--project', '-p', type=str, help='Project path to update (defaults to global mcpServers)')
    parser.add_argument('--mcp-file', '-m', type=str, default='mcpServers.json', help='Path to mcpServers.json file')
    parser.add_argument('--url', '-u', type=str, help='URL to fetch mcpServers.json from (overrides --mcp-file)')
    parser.add_argument('--edit', '-e', action='store_true', help='Edit mcpServers.json before syncing (not available with --url)')
    parser.add_argument('--binding', '-b', action='store_true', help='Update mcpServers.json with servers from .claude.json (not available with --url)')
    parser.add_argument('--claude-config', '-c', type=str, default='~/.claude.json', help='Path to .claude.json file')
    args = parser.parse_args()
    
    # Validate that --edit is not used with --url
    if args.edit and args.url:
        print("Error: --edit option cannot be used with --url")
        sys.exit(1)
    
    # Validate that --binding is not used with --url
    if args.binding and args.url:
        print("Error: --binding option cannot be used with --url")
        sys.exit(1)
    
    try:
        run_sync(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(0)
    except EOFError:
        print("\nOperation cancelled.")
        sys.exit(0)


def run_sync(args):
    
    # Resolve paths
    claude_config_path = Path(args.claude_config).expanduser().resolve()
    
    # Determine if we're using URL or local file
    using_url = bool(args.url)
    mcp_file_path = None if using_url else Path(args.mcp_file).resolve()
    
    # Handle edit mode if requested
    if args.edit and not using_url:
        print(f"Opening {mcp_file_path} in editor...")
        print("Make your changes and save the file to continue.")
        if edit_json_file(mcp_file_path):
            print("\nFile modified. Proceeding with sync...\n")
        else:
            print("\nNo changes detected or edit cancelled.")
    
    # Load MCP servers from URL or file
    if using_url:
        available_servers = load_json_from_url(args.url)
    else:
        available_servers = load_json_file(mcp_file_path, create_if_missing=True)
    
    # Load Claude configuration
    claude_config = load_json_file(claude_config_path)
    
    # Get current MCP servers from Claude config
    current_servers = get_current_mcp_servers(claude_config, args.project)
    
    # Handle binding mode - update mcpServers.json with servers from .claude.json
    if args.binding and not using_url:
        servers_to_add = {}
        for server_name, server_config in current_servers.items():
            if server_name not in available_servers:
                servers_to_add[server_name] = server_config
        
        if servers_to_add:
            print(f"Found {len(servers_to_add)} server(s) in .claude.json not in mcpServers.json:")
            for name in servers_to_add:
                print(f"  - {name}")
            print()
            
            # Update available servers
            available_servers.update(servers_to_add)
            
            # Save updated mcpServers.json
            save_json_file(mcp_file_path, available_servers, create_backup=True)
            print(f"\nAdded {len(servers_to_add)} server(s) to mcpServers.json")
            print("Proceeding with sync...\n")
        else:
            print("No new servers found in .claude.json to add to mcpServers.json")
            print("Proceeding with sync...\n")
    
    # Check if no MCP servers are available
    if not available_servers:
        if args.url:
            print(f"\nNo MCP servers found at URL: {args.url}")
            print("Please ensure the URL returns a valid JSON with MCP server configurations.")
        else:
            print("\nNo MCP servers found in mcpServers.json!")
            print("Please add your MCP server configurations to the file.")
            print("You can use mcpServers.json.example as a reference.")
            print("\nExample configuration:")
            print('  "server-name": {')
            print('    "type": "sse",')
            print('    "url": "http://localhost:8765/mcp/claude/sse"')
            print('  }')
        sys.exit(0)
    
    # Display target information
    if args.project:
        print(f"Syncing MCP servers for project: {args.project}")
    else:
        print("Syncing global MCP servers")
    
    print(f"Available servers: {len(available_servers)}")
    print(f"Currently enabled: {len(current_servers)}")
    print()
    
    # Main selection loop
    while True:
        # Create interactive selection
        choices = create_server_choices(available_servers, current_servers)
        
        # Build prompt message
        prompt_message = "Select MCP servers to enable"
        
        # Build instruction text with keyboard shortcuts
        if using_url:
            instruction_text = "(Use arrow keys to move, <space> to select, <a> to toggle, <i> to invert)"
        else:
            instruction_text = "(Use arrow keys to move, <space> to select, <e> to edit, <a> to toggle, <i> to invert)"
        
        # Create checkbox prompt
        question = questionary.checkbox(
            prompt_message,
            choices=choices,
            instruction=instruction_text
        )
        
        # Flag to track if edit was requested
        edit_requested = False
        
        # Create custom key bindings
        kb = KeyBindings()
        
        @kb.add('e', eager=True)
        def _(event):
            nonlocal edit_requested
            edit_requested = True
            event.app.exit(result=[])
        
        # Add our custom key bindings to the question's application
        if not using_url:
            # Merge our key bindings with the existing ones
            question.application.key_bindings = merge_key_bindings([kb, question.application.key_bindings])
        
        try:
            selected = question.unsafe_ask()
            
            # Check if edit was requested
            if edit_requested and not using_url:
                print("\nOpening mcpServers.json in editor...")
                if edit_json_file(mcp_file_path):
                    print("File modified. Reloading configurations...\n")
                    # Reload the modified file
                    available_servers = load_json_file(mcp_file_path)
                    if not available_servers:
                        print("\nNo MCP servers found after edit!")
                        print("Please add server configurations to the file.")
                        sys.exit(0)
                else:
                    print("No changes made to the file.\n")
                continue  # Go back to selection
                
        except (KeyboardInterrupt, EOFError, Exception) as e:
            print("\nOperation cancelled.")
            sys.exit(0)
        
        if selected is None:
            print("\nOperation cancelled.")
            sys.exit(0)
        
        # Exit the loop if not editing
        break
    
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
    try:
        confirm = questionary.confirm("Apply these changes?").unsafe_ask()
    except (KeyboardInterrupt, EOFError, Exception):
        print("\nOperation cancelled.")
        sys.exit(0)
    
    if confirm is None or not confirm:
        print("Operation cancelled.")
        sys.exit(0)
    
    # Update configuration
    set_mcp_servers(claude_config, new_servers, args.project)
    
    # Save updated configuration
    save_json_file(claude_config_path, claude_config)
    
    print("\nSync completed successfully!")


if __name__ == "__main__":
    main()