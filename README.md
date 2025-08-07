# MCP Claude Config Sync Tool

A Python CLI tool to manage MCP (Model Context Protocol) server configurations between `mcpServers.json` and `~/.claude.json`.

## Setup

### 1. Install Dependencies

This project uses `uv` for dependency management. Make sure you have `uv` installed, then run:

```bash
uv sync
```

### 2. Configure MCP Servers

Copy the example configuration and customize it with your MCP servers:

```bash
cp mcpServers.json.example mcpServers.json
```

Edit `mcpServers.json` with your actual MCP server configurations. This file is gitignored to protect sensitive information like API keys and database credentials.

## Usage

### Basic Usage (Global MCP Servers)

To sync MCP servers globally:

```bash
uv run python main.py
```

### Project-Specific MCP Servers

To sync MCP servers for a specific project:

```bash
uv run python main.py --project /path/to/your/project
```

### Custom File Paths

You can specify custom paths for the configuration files:

```bash
uv run python main.py --mcp-file /path/to/mcpServers.json --claude-config /path/to/.claude.json
```

## Features

- Interactive checkbox selection using arrow keys
- Shows current status (enabled/disabled) for each server
- Syncs by server name (e.g., mem0, mcp-postgres-production-phoenix)
- Creates automatic backup of `.claude.json` before modifications
- Supports both global and project-specific mcpServers configurations
- Preserves all other settings in `.claude.json`

## How it Works

1. Loads available MCP servers from `mcpServers.json`
2. Reads current configuration from `~/.claude.json`
3. Presents an interactive checklist showing all available servers
4. Updates the configuration based on your selections
5. Creates a timestamped backup before saving changes

## Command Line Options

- `--project, -p`: Project path to update (defaults to global mcpServers)
- `--mcp-file, -m`: Path to mcpServers.json file (default: `mcpServers.json`)
- `--claude-config, -c`: Path to .claude.json file (default: `~/.claude.json`)
- `--help, -h`: Show help message

## Security Note

The `mcpServers.json` file is gitignored because it may contain sensitive information such as:
- API keys
- Database credentials
- Internal URLs
- Authentication tokens

Always use `mcpServers.json.example` as a template and keep your actual configuration local.

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