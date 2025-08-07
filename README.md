# MCP Claude Config Sync Tool

A Python CLI tool to manage MCP (Model Context Protocol) server configurations between `mcpServers.json` and `~/.claude.json`.

## Installation

### Quick Install (Recommended)

The easiest way to install `mcp-sync` is using the provided Makefile:

```bash
# Clone the repository
git clone <repository-url>
cd mcp-claude-config

# Install for current user (installs to ~/.local/bin)
make install

# Or install system-wide (requires sudo)
make install-system
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

## Features

- Interactive checkbox selection using arrow keys
- Press Ctrl+C at any time to cancel the operation
- Shows current status (enabled/disabled) for each server
- Syncs by server name (e.g., mem0, mcp-postgres-production-phoenix)
- Load MCP server configurations from a URL
- Edit mcpServers.json directly from the CLI
- Creates automatic backup of `.claude.json` before modifications
- Supports both global and project-specific mcpServers configurations
- Preserves all other settings in `.claude.json`

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