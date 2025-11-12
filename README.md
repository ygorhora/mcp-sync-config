# MCP Claude Config Sync Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Linux](https://img.shields.io/badge/platform-linux-lightgrey.svg)](https://www.linux.org/)
[![WSL2](https://img.shields.io/badge/platform-wsl2-lightgrey.svg)](https://docs.microsoft.com/en-us/windows/wsl/)

🚀 **Streamline your Claude Code MCP server management with a powerful, interactive CLI tool**

<p align="center">
  <img src="https://github.com/ygorhora/mcp-sync-config/assets/demo.gif" alt="Demo" width="600">
</p>

## 📖 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Overview

MCP Claude Config Sync Tool is a sophisticated command-line utility designed to simplify the management of Model Context Protocol (MCP) servers in Claude Code. Whether you're managing database connections, API integrations, or custom MCP servers, this tool provides an elegant solution for synchronizing configurations across projects.

## 🎯 Features

### Core Features
- ✨ **Interactive Server Management** - Toggle MCP servers on/off with an intuitive checkbox interface
- 🎨 **Multi-Project Support** - Manage global configurations or project-specific settings
- 🌐 **Remote Configuration Loading** - Fetch MCP configurations from URLs for team standardization
- ✏️ **Live Configuration Editing** - Edit your MCP servers directly from the CLI with your preferred editor
- ⌨️ **Quick Edit Shortcut** - Press 'e' during selection to instantly edit mcpServers.json
- 💾 **Automatic Backups** - Never lose your configurations with automatic timestamped backups
- 🔄 **Smart Sync** - Intelligently merges configurations while preserving existing settings

### Why Choose MCP Claude Config?

| Without This Tool | With MCP Claude Config |
|-------------------|------------------------|
| ❌ Manually edit JSON files | ✅ Interactive checkbox UI |
| ❌ Risk syntax errors | ✅ Automatic validation |
| ❌ No backup system | ✅ Timestamped backups |
| ❌ Copy configs manually | ✅ One-command sync |
| ❌ Share via chat/email | ✅ Share URL configs |

## 💻 System Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Linux, macOS, or Windows (WSL2) |
| **Python** | 3.13 or higher |
| **Package Manager** | [uv](https://github.com/astral-sh/uv) |
| **Claude Code** | Latest version installed |

## 🛠️ Prerequisites

Before installing MCP Claude Config, ensure you have:

### 1. Python 3.13 or higher
```bash
python --version  # Should show 3.13.x or higher
```

### 2. uv Package Manager

Install `uv` using one of these methods:

```bash
# Using curl (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Using pip
pip install uv

# On macOS with Homebrew
brew install uv
```

### 3. Claude Code
Ensure Claude Code is installed and has been run at least once to create the configuration file.

## 📦 Installation

### Option 1: Quick Install (Recommended)

```bash
# Clone the repository
git clone https://github.com/ygorhora/mcp-sync-config.git
cd mcp-sync-config

# Install for current user (recommended)
make install

# Or install system-wide (requires sudo)
make install-system
```

✅ **Success!** You can now run `mcp-sync` from any directory!

### Option 2: Install from Release

```bash
# Download the latest release
wget https://github.com/ygorhora/mcp-sync-config/releases/latest/download/mcp-sync-config.tar.gz
tar -xzf mcp-sync-config.tar.gz
cd mcp-sync-config

# Install
make install
```

### Updating

To update to the latest version:

```bash
cd mcp-sync-config
git pull
make update
```

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

# Clean up .claude.json backup files
mcp-sync --clean

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

### Creating a Custom Alias

If you want to create a shorter command that always uses a specific `mcpServers.json` file, you can set up a shell alias using the Makefile:

```bash
# Setup 'ms' alias that points to your custom mcpServers.json
make setup-alias path=$(pwd)/mcpServers.json

# Or with an absolute path
make setup-alias path=/path/to/your/mcpServers.json

# Or in your home directory
make setup-alias path=~/mcpServers.json
```

This will:
- Detect your shell (bash/zsh) automatically
- Add the alias to your shell configuration file (.zshrc/.bashrc)
- Create the `ms` command that runs `mcp-sync --mcp-file /your/path`

**After setup, restart your terminal**

**Now use the `ms` shortcut:**
```bash
ms              # Sync with your custom path
ms --edit       # Edit before syncing
ms --binding    # Update from .claude.json
ms --project /path/to/project  # Project-specific sync
```

**Remove the alias when no longer needed:**
```bash
make uninstall-alias
```

This is useful when:
- You have multiple `mcpServers.json` files for different contexts
- You want a shorter command than typing the full path every time
- You're working on a specific project and want quick access to its MCP configuration

## 🚀 Quick Start

### Step 1: Initial Setup

```bash
# Copy the example configuration
cp mcpServers.json.example mcpServers.json

# Edit your MCP servers (opens in your default editor)
mcp-sync --edit
```

### Step 2: Sync Your Servers

```bash
# Run the interactive sync
mcp-sync
```

You'll see an interactive checklist:
```
Syncing global MCP servers
Available servers: 3
Currently enabled: 1

Select MCP servers to enable: (Use arrow keys to move, <space> to select, <e> to edit, <a> to toggle, <i> to invert)
❯ ◉ mem0 (SSE: http://localhost:8765/mcp/claude/sse/root)
  ◯ postgres-dev (Command: docker)
  ◯ my-custom-api (SSE: https://api.example.com/mcp)
```

### Step 3: Confirm Changes

```
Enabling servers: postgres-dev
Disabling servers: my-custom-api

Apply these changes? (y/N)
```

## 📚 Documentation

### Common Use Cases

#### Managing Development vs Production Servers

```bash
# Development environment
mcp-sync --project ~/dev/my-app

# Production environment  
mcp-sync --project ~/prod/my-app
```

#### Team Configuration Sharing

```bash
# Load team's standard MCP configuration
mcp-sync --url https://your-team.com/mcp-config.json

# Or from a GitHub gist
mcp-sync --url https://gist.githubusercontent.com/user/id/raw/mcpServers.json
```

#### Capture Servers from Claude Code

```bash
# If you've added servers directly in Claude Code,
# capture them back to your mcpServers.json
mcp-sync --binding

# This will add any servers that exist in .claude.json
# but not in mcpServers.json, then proceed with normal sync
```

#### Backup and Restore

```bash
# Backups are created automatically with timestamps
# List all backup files
make list-backups

# Clean up old backup files (with confirmation)
make clean-backups

# Or use the mcp-sync command directly
mcp-sync --clean

# Manual backup
cp ~/.claude.json ~/.claude.json.manual-backup

# Restore from backup
cp ~/.claude.backup.20240101_120000.json ~/.claude.json
```

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
- `--binding, -b`: Update mcpServers.json with servers from .claude.json (not available with --url)
- `--claude-config, -c`: Path to .claude.json file (default: `~/.claude.json`)
- `--clean`: Clean up .claude.json backup files
- `--help, -h`: Show help message

## Security Note

The `mcpServers.json` file is gitignored because it may contain sensitive information such as:
- API keys
- Database credentials
- Internal URLs
- Authentication tokens

Always use `mcpServers.json.example` as a template and keep your actual configuration local.

## Makefile Commands

### Installation & Management
- `make help` - Show all available commands
- `make install` - Install for current user (default)
- `make update` - Update installation (uninstall then install)
- `make install-user` - Install to ~/.local/bin
- `make install-system` - Install to /usr/local/bin (requires sudo)
- `make uninstall` - Remove installed script

### Code Quality
- `make lint` - Run linting with Ruff
- `make format` - Format code with Ruff
- `make lint-fix` - Fix linting issues automatically
- `make check` - Run both linting and tests

### Testing
- `make test` - Run all tests
- `make test-coverage` - Run tests with coverage report
- `make test-watch` - Run tests in watch mode

### Maintenance
- `make clean` - Clean generated files
- `make list-backups` - List all .claude.json backup files
- `make clean-backups` - Clean .claude.json backup files (with confirmation)

## Troubleshooting

### Common Issues

**"uv: command not found"**
- Solution: Install uv following the [Prerequisites](#prerequisites) section

**"Error: File not found: ~/.claude.json"**
- Solution: Make sure Claude Code is installed and has been run at least once

**Editor doesn't open with --edit**
- Solution: Set your preferred editor: `export EDITOR=nano` (or vim, emacs, etc.)

**Permission denied when installing**
- Solution: Use `make install-user` instead of `make install-system`

### Platform-Specific Notes

**Windows Users:**
- This tool requires WSL2 (Windows Subsystem for Linux)
- Run all commands inside your WSL2 terminal
- Claude Code config is accessible at `/mnt/c/Users/YourName/AppData/Roaming/Claude/claude.json`

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

## 🧪 Development

### Running Tests

```bash
# Run all tests
make test

# Run with coverage report
make test-coverage

# Run in watch mode during development
make test-watch
```

### Code Quality with Ruff

This project uses [Ruff](https://github.com/astral-sh/ruff) for linting and code formatting. Ruff is configured to enforce consistent code style and catch common errors.

```bash
# Run linting checks
make lint

# Format code automatically
make format

# Fix linting issues automatically
make lint-fix

# Run both linting and tests
make check
```

#### Ruff Configuration

The project's Ruff configuration can be found in:
- `pyproject.toml` - Main configuration with enabled rules
- `.ruff.toml` - Additional per-file ignores

Key settings:
- Line length: 120 characters
- Target Python version: 3.13
- Enabled rule sets: pycodestyle, pyflakes, isort, pep8-naming, and more
- Automatic import sorting and formatting

### Project Structure

```
mcp-sync-config/
├── main.py              # Main application logic
├── Makefile            # Build and install automation
├── pyproject.toml      # Project configuration
├── tests/              # Test suite
│   ├── test_*.py      # Test modules
│   └── fixtures/      # Test data
├── mcpServers.json.example  # Example configuration
└── README.md           # This file
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Guide

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👏 Acknowledgments

- Thanks to all contributors who have helped improve this tool
- Special thanks to the Claude team for creating the MCP protocol
- Built with [uv](https://github.com/astral-sh/uv) for fast, reliable Python dependency management

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ygorhora/mcp-sync-config/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ygorhora/mcp-sync-config/discussions)
- **Email**: ygorhora@gmail.com

---

<p align="center">Made with ❤️ by <a href="https://github.com/ygorhora">Ygor Hora</a></p>