# Makefile for mcp-sync installation
# Install the MCP sync tool system-wide or for current user

# Variables
SCRIPT_NAME = mcp-sync
PROJECT_DIR = $(shell pwd)
USER_BIN_DIR = $(HOME)/.local/bin
SYSTEM_BIN_DIR = /usr/local/bin
WRAPPER_SCRIPT = $(PROJECT_DIR)/$(SCRIPT_NAME)

# Default target
.DEFAULT_GOAL := help

.PHONY: help
help: ## Show this help message
	@echo "MCP Sync Tool Installation"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

.PHONY: install
install: install-user ## Install for current user (default)

.PHONY: update
update: ## Update installation (uninstall then install)
	@echo "Updating mcp-sync..."
	@$(MAKE) -s uninstall
	@$(MAKE) -s install
	@echo "Update complete!"

.PHONY: deps
deps: ## Install Python dependencies
	@echo "Installing Python dependencies..."
	@command -v uv >/dev/null 2>&1 || { echo "Error: uv is not installed. Please install uv first."; exit 1; }
	@uv sync

.PHONY: wrapper
wrapper: ## Create the wrapper script
	@echo "Creating wrapper script..."
	@echo '#!/bin/bash' > $(WRAPPER_SCRIPT)
	@echo '# Auto-generated wrapper script for mcp-sync' >> $(WRAPPER_SCRIPT)
	@echo 'set -e' >> $(WRAPPER_SCRIPT)
	@echo '' >> $(WRAPPER_SCRIPT)
	@echo '# Project directory' >> $(WRAPPER_SCRIPT)
	@echo 'PROJECT_DIR="$(PROJECT_DIR)"' >> $(WRAPPER_SCRIPT)
	@echo '' >> $(WRAPPER_SCRIPT)
	@echo '# Check if project directory exists' >> $(WRAPPER_SCRIPT)
	@echo 'if [ ! -d "$$PROJECT_DIR" ]; then' >> $(WRAPPER_SCRIPT)
	@echo '    echo "Error: Project directory not found: $$PROJECT_DIR"' >> $(WRAPPER_SCRIPT)
	@echo '    echo "You may need to reinstall mcp-sync"' >> $(WRAPPER_SCRIPT)
	@echo '    exit 1' >> $(WRAPPER_SCRIPT)
	@echo 'fi' >> $(WRAPPER_SCRIPT)
	@echo '' >> $(WRAPPER_SCRIPT)
	@echo '# Change to project directory and run with uv' >> $(WRAPPER_SCRIPT)
	@echo 'cd "$$PROJECT_DIR"' >> $(WRAPPER_SCRIPT)
	@echo '' >> $(WRAPPER_SCRIPT)
	@echo '# Check if uv is available' >> $(WRAPPER_SCRIPT)
	@echo 'if ! command -v uv >/dev/null 2>&1; then' >> $(WRAPPER_SCRIPT)
	@echo '    echo "Error: uv is not installed. Please install uv to use mcp-sync."' >> $(WRAPPER_SCRIPT)
	@echo '    exit 1' >> $(WRAPPER_SCRIPT)
	@echo 'fi' >> $(WRAPPER_SCRIPT)
	@echo '' >> $(WRAPPER_SCRIPT)
	@echo '# Run the Python script with all arguments' >> $(WRAPPER_SCRIPT)
	@echo 'exec uv run python main.py "$$@"' >> $(WRAPPER_SCRIPT)
	@chmod +x $(WRAPPER_SCRIPT)
	@echo "Wrapper script created at $(WRAPPER_SCRIPT)"

.PHONY: install-user
install-user: deps wrapper ## Install for current user in ~/.local/bin
	@echo "Installing for current user..."
	@mkdir -p $(USER_BIN_DIR)
	@cp $(WRAPPER_SCRIPT) $(USER_BIN_DIR)/$(SCRIPT_NAME)
	@chmod +x $(USER_BIN_DIR)/$(SCRIPT_NAME)
	@echo ""
	@echo "✓ Installed $(SCRIPT_NAME) to $(USER_BIN_DIR)"
	@echo ""
	@if ! echo "$$PATH" | grep -q "$(USER_BIN_DIR)"; then \
		echo "⚠️  Warning: $(USER_BIN_DIR) is not in your PATH"; \
		echo "  Add this line to your ~/.bashrc or ~/.zshrc:"; \
		echo "  export PATH=\"$(USER_BIN_DIR):\$$PATH\""; \
		echo ""; \
	fi
	@echo "You can now run 'mcp-sync' from any directory"

.PHONY: install-system
install-system: deps wrapper ## Install system-wide in /usr/local/bin (requires sudo)
	@echo "Installing system-wide..."
	@if [ ! -w $(SYSTEM_BIN_DIR) ]; then \
		echo "Installing to $(SYSTEM_BIN_DIR) (requires sudo)..."; \
		sudo cp $(WRAPPER_SCRIPT) $(SYSTEM_BIN_DIR)/$(SCRIPT_NAME); \
		sudo chmod +x $(SYSTEM_BIN_DIR)/$(SCRIPT_NAME); \
	else \
		cp $(WRAPPER_SCRIPT) $(SYSTEM_BIN_DIR)/$(SCRIPT_NAME); \
		chmod +x $(SYSTEM_BIN_DIR)/$(SCRIPT_NAME); \
	fi
	@echo ""
	@echo "✓ Installed $(SCRIPT_NAME) to $(SYSTEM_BIN_DIR)"
	@echo "You can now run 'mcp-sync' from any directory"

.PHONY: uninstall
uninstall: ## Remove installed script
	@echo "Uninstalling $(SCRIPT_NAME)..."
	@if [ -f $(USER_BIN_DIR)/$(SCRIPT_NAME) ]; then \
		rm -f $(USER_BIN_DIR)/$(SCRIPT_NAME); \
		echo "Removed $(USER_BIN_DIR)/$(SCRIPT_NAME)"; \
	fi
	@if [ -f $(SYSTEM_BIN_DIR)/$(SCRIPT_NAME) ]; then \
		if [ -w $(SYSTEM_BIN_DIR)/$(SCRIPT_NAME) ]; then \
			rm -f $(SYSTEM_BIN_DIR)/$(SCRIPT_NAME); \
		else \
			echo "Removing from $(SYSTEM_BIN_DIR) (requires sudo)..."; \
			sudo rm -f $(SYSTEM_BIN_DIR)/$(SCRIPT_NAME); \
		fi; \
		echo "Removed $(SYSTEM_BIN_DIR)/$(SCRIPT_NAME)"; \
	fi
	@if [ -f $(WRAPPER_SCRIPT) ]; then \
		rm -f $(WRAPPER_SCRIPT); \
		echo "Removed wrapper script"; \
	fi
	@echo "Uninstall complete"

.PHONY: clean
clean: ## Clean generated files
	@rm -f $(WRAPPER_SCRIPT)
	@rm -rf .coverage htmlcov .pytest_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned generated files"

.PHONY: clean-backups
clean-backups: ## Clean .claude.json backup files
	@echo "Searching for .claude.json backup files in home directory..."
	@BACKUP_DIR="$${HOME}"; \
	BACKUP_COUNT=$$(ls $$BACKUP_DIR/.claude.backup.*.json 2>/dev/null | wc -l); \
	if [ $$BACKUP_COUNT -eq 0 ]; then \
		echo "No backup files found."; \
	else \
		echo "Found $$BACKUP_COUNT backup file(s):"; \
		ls -la $$BACKUP_DIR/.claude.backup.*.json 2>/dev/null | while read line; do \
			echo "  $$line"; \
		done; \
		echo ""; \
		printf "Delete all backup files? [y/N] "; \
		read REPLY; \
		case $$REPLY in \
			[yY]) \
				rm -f $$BACKUP_DIR/.claude.backup.*.json; \
				echo "✓ Deleted $$BACKUP_COUNT backup file(s)"; \
				;; \
			*) \
				echo "Cancelled. No files deleted."; \
				;; \
		esac \
	fi

.PHONY: list-backups
list-backups: ## List all .claude.json backup files
	@echo "Listing .claude.json backup files in home directory..."
	@BACKUP_DIR="$${HOME}"; \
	if ls $$BACKUP_DIR/.claude.backup.*.json >/dev/null 2>&1; then \
		echo "Found backup files:"; \
		ls -lht $$BACKUP_DIR/.claude.backup.*.json | awk '{print "  " $$9 " (" $$5 ", " $$6 " " $$7 " " $$8 ")"}'; \
	else \
		echo "No backup files found."; \
	fi

.PHONY: test
test: ## Run tests
	@echo "Running tests..."
	@uv sync --extra test
	@uv run pytest

.PHONY: test-coverage
test-coverage: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	@uv sync --extra test
	@uv run pytest --cov=main --cov-report=term --cov-report=html


.PHONY: test-watch
test-watch: ## Run tests in watch mode
	@echo "Running tests in watch mode..."
	@uv sync --extra test
	@uv run pytest-watch

.PHONY: lint
lint: ## Run linting with ruff
	@echo "Running linting..."
	@uv sync --extra dev
	@uv run ruff check .

.PHONY: format
format: ## Format code with ruff
	@echo "Formatting code..."
	@uv sync --extra dev
	@uv run ruff format .

.PHONY: lint-fix
lint-fix: ## Fix linting issues with ruff
	@echo "Fixing linting issues..."
	@uv sync --extra dev
	@uv run ruff check --fix .

.PHONY: check
check: lint test ## Run linting and tests