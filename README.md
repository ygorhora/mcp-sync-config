# MCP Claude Config Sync Tool

🚀 **Streamline your Claude Desktop MCP server management with a powerful, interactive CLI tool**

## Overview

MCP Claude Config Sync Tool is a sophisticated command-line utility designed to simplify the management of Model Context Protocol (MCP) servers in Claude Desktop. Whether you're managing database connections, API integrations, or custom MCP servers, this tool provides an elegant solution for synchronizing configurations across projects.

### Key Capabilities

- **Interactive Server Management**: Toggle MCP servers on/off with an intuitive checkbox interface
- **Multi-Project Support**: Manage global configurations or project-specific settings
- **Remote Configuration Loading**: Fetch MCP configurations from URLs for team standardization
- **Live Configuration Editing**: Edit your MCP servers directly from the CLI with your preferred editor
- **Automatic Backups**: Never lose your configurations with automatic timestamped backups
- **Smart Sync**: Intelligently merges configurations while preserving existing settings

### Perfect For

- **Developers** managing multiple database connections across projects
- **Teams** standardizing MCP server configurations
- **DevOps Engineers** automating Claude Desktop setups
- **Power Users** who prefer CLI over GUI for configuration management

## Why Use This Tool?

Managing MCP servers in Claude Desktop manually can be tedious and error-prone. This tool solves common pain points:

- ❌ **Without this tool**: Manually edit JSON files, risk syntax errors, no backup system
- ✅ **With this tool**: Interactive UI, validation, automatic backups

- ❌ **Without this tool**: Copy configurations between projects manually
- ✅ **With this tool**: Single command to sync configurations across projects

- ❌ **Without this tool**: Share configurations via chat/email with team members
- ✅ **With this tool**: Share a URL to standardized configurations

## System Requirements

- **Operating System**: Linux or Windows with WSL2
- **Python**: 3.8 or higher
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (required for dependency management)
- **Claude Desktop**: Installed with `.claude.json` configuration file

## Prerequisites

### Install uv (Python Package Manager)

This tool requires `uv` for dependency management. Install it using one of these methods:

```bash
# Using curl (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Using pip
pip install uv

# On macOS with Homebrew
brew install uv
```

## Installation

### Quick Install (Recommended)

Once you have `uv` installed, setting up `mcp-sync` is straightforward:

```bash
# Clone the repository
git clone <repository-url>
cd mcp-claude-config

# Install for current user (installs to ~/.local/bin)
make install

# Or install system-wide (requires sudo)
make install-system

# Update existing installation
make update
```

After installation, you can run `mcp-sync` from any directory!

### Manual Setup

If you prefer to run without installing:

1. **Install Dependencies**

   This project uses `uv` for dependency management. Make sure you have `uv` installed, then run:

   ```bash
   uv sync
   ```

2. **Configure MCP Servers**

   Copy the example configuration and customize it with your MCP servers:

   ```bash
   cp mcpServers.json.example mcpServers.json
   ```

   Edit `mcpServers.json` with your actual MCP server configurations. This file is gitignored to protect sensitive information like API keys and database credentials.

## Usage

### After Installation

If you've installed using `make install`:

```bash
# Sync global MCP servers
mcp-sync

# Sync for a specific project
mcp-sync --project /path/to/your/project

# Load MCP servers from a URL
mcp-sync --url https://example.com/mcpServers.json

# Edit mcpServers.json before syncing
mcp-sync --edit

# Show help
mcp-sync --help
```

### Manual Usage (without installation)

If running directly from the project directory:

```bash
# Sync global MCP servers
uv run python main.py

# Sync for a specific project
uv run python main.py --project /path/to/your/project

# Load MCP servers from a URL
uv run python main.py --url https://example.com/mcpServers.json

# Edit mcpServers.json before syncing
uv run python main.py --edit

# Custom file paths
uv run python main.py --mcp-file /path/to/mcpServers.json --claude-config /path/to/.claude.json
```

## Quick Start Guide

### 1. First Time Setup

```bash
# Copy the example configuration
cp mcpServers.json.example mcpServers.json

# Edit your MCP servers
mcp-sync --edit

# Or manually edit the file
nano mcpServers.json
```

### 2. Common Workflows

**Enable/Disable MCP Servers:**
```bash
mcp-sync
# Use ↑↓ to navigate, Space to toggle, Enter to confirm
```

**Sync for a Specific Project:**
```bash
mcp-sync --project /home/user/my-project
```

**Use Team Configuration:**
```bash
mcp-sync --url https://company.com/team-mcp-config.json
```

## Features

### 🎯 Core Features

- **Interactive Interface**: Navigate with arrow keys, toggle with spacebar
- **Smart Selection**: See current status of each server at a glance
- **Project Isolation**: Manage global or project-specific configurations
- **Live Editing**: Press `--edit` to modify configurations on the fly

### 🛡️ Safety Features

- **Automatic Backups**: Creates timestamped backups before any changes
- **Validation**: Ensures JSON integrity before saving
- **Graceful Cancellation**: Press Ctrl+C anytime to exit safely
- **Preserve Settings**: Never loses your existing Claude configuration

### 🚀 Advanced Features

- **URL Support**: Load configurations from remote servers
- **Custom Paths**: Override default file locations
- **Environment Variables**: Respects `$EDITOR` for file editing
- **Batch Operations**: Enable/disable multiple servers at once

## How it Works

1. Loads available MCP servers from `mcpServers.json` or a URL
2. Reads current configuration from `~/.claude.json`
3. Presents an interactive checklist showing all available servers
4. Updates the configuration based on your selections
5. Creates a timestamped backup before saving changes

## Command Line Options

- `--project, -p`: Project path to update (defaults to global mcpServers)
- `--mcp-file, -m`: Path to mcpServers.json file (default: `mcpServers.json`)
- `--url, -u`: URL to fetch mcpServers.json from (overrides --mcp-file)
- `--edit, -e`: Edit mcpServers.json before syncing (not available with --url)
- `--claude-config, -c`: Path to .claude.json file (default: `~/.claude.json`)
- `--help, -h`: Show help message

## Security Note

The `mcpServers.json` file is gitignored because it may contain sensitive information such as:
- API keys
- Database credentials
- Internal URLs
- Authentication tokens

Always use `mcpServers.json.example` as a template and keep your actual configuration local.

## Makefile Commands

- `make help` - Show all available commands
- `make install` - Install for current user (default)
- `make update` - Update installation (uninstall then install)
- `make install-user` - Install to ~/.local/bin
- `make install-system` - Install to /usr/local/bin (requires sudo)
- `make uninstall` - Remove installed script
- `make clean` - Clean generated files

## Troubleshooting

### Common Issues

**"uv: command not found"**
- Solution: Install uv following the [Prerequisites](#prerequisites) section

**"Error: File not found: ~/.claude.json"**
- Solution: Make sure Claude Desktop is installed and has been run at least once

**Editor doesn't open with --edit**
- Solution: Set your preferred editor: `export EDITOR=nano` (or vim, emacs, etc.)

**Permission denied when installing**
- Solution: Use `make install-user` instead of `make install-system`

### Platform-Specific Notes

**Windows Users:**
- This tool requires WSL2 (Windows Subsystem for Linux)
- Run all commands inside your WSL2 terminal
- Claude Desktop config is accessible at `/mnt/c/Users/YourName/AppData/Roaming/Claude/claude.json`

**Linux Users:**
- Works out of the box on all major distributions
- Ensure ~/.local/bin is in your PATH for user installation

## Example mcpServers.json

```json
{
  "mem0": {
    "type": "sse",
    "url": "http://localhost:8765/mcp/claude/sse/root"
  },
  "mcp-postgres-production": {
    "command": "docker",
    "args": ["run", "--name", "mcp-postgres", "-i", "--rm", "postgres-mcp"],
    "env": {
      "DATABASE_URI": "postgresql://user:pass@host:5432/db"
    }
  }
}
```

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve this tool.

## License

[Add your license here]