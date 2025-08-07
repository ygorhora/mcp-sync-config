# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of MCP Claude Config Sync Tool
- Interactive checkbox interface for server selection
- Support for global and project-specific configurations
- URL-based configuration loading
- Built-in editor integration with `--edit` flag
- Press 'e' during selection to edit mcpServers.json
- `--binding` flag to capture servers from .claude.json back to mcpServers.json
- Automatic backup creation before modifications
- Comprehensive test suite
- Installation via Makefile
- Support for Linux and WSL2
- Makefile commands for backup management (list-backups, clean-backups)

### Features
- Sync MCP servers between mcpServers.json and ~/.claude.json
- Visual status indicators for enabled/disabled servers
- Batch enable/disable operations
- Custom file path support
- Environment variable support for editor selection

### Developer Experience
- Python 3.13+ support
- uv package manager integration
- pytest-based test suite
- Type hints throughout codebase
- Comprehensive documentation

## [0.1.0] - 2024-01-XX

### Added
- First public release

[Unreleased]: https://github.com/ygorhora/mcp-claude-config/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/ygorhora/mcp-claude-config/releases/tag/v0.1.0