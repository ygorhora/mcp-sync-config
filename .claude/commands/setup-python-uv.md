# Usage
`@setup-python-uv.md [--git]`

## Parameters
- `--git`: (Optional) Initialize git repository, create private GitHub repo, and configure local git settings

# Python Environment
- Check pyenv versions available
```sh
$ pyenv versions
```
- Set the latest version on current project
```sh
$ pyenv local <latest-version>
```
- Install `uv` with the latest version of python activated
```sh
$ pip install uv
```
- Check if `uv` was correctly installed on pyenv version installed on the project
```sh
$ pyenv whence uv
```
- Init `uv` project:
```sh
$ uv init
```

# Environment Configuration
- Create empty .env file for environment variables:
```sh
$ touch .env
```

# Code Quality Setup with Ruff

- Install Ruff as a development dependency:
```sh
$ uv add --dev ruff
```

- Create a basic Ruff configuration in `pyproject.toml`:
```toml
[tool.ruff]
line-length = 120
target-version = "py313"  # Adjust to your Python version

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "A",    # flake8-builtins
    "C4",   # flake8-comprehensions
    "PIE",  # flake8-pie
    "PT",   # flake8-pytest-style
    "RET",  # flake8-return
    "SIM",  # flake8-simplify
    "ARG",  # flake8-unused-arguments
    "PTH",  # flake8-use-pathlib
    "PL",   # pylint
    "RUF",  # ruff-specific rules
]
ignore = [
    "E501",     # line too long (handled by formatter)
    "PLR0913",  # too many arguments
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

- Run Ruff to check and format your code:
```sh
# Check for linting issues
$ uv run ruff check .

# Fix auto-fixable issues
$ uv run ruff check --fix .

# Format code
$ uv run ruff format .
```

- (Optional) Add Makefile targets for easier Ruff usage:
```makefile
.PHONY: lint
lint:
	uv run ruff check .

.PHONY: format
format:
	uv run ruff format .

.PHONY: lint-fix
lint-fix:
	uv run ruff check --fix .
```

# Git & GitHub (Only if --git flag is passed)

When `--git` flag is provided, the script will:
1. Ask for your Git user name and email
2. Initialize a git repository
3. Download Python .gitignore from toptal.com
4. Create a private GitHub repository with the current folder name
5. Configure local git settings with provided credentials
6. Make initial commit and push to GitHub

## Commands that will be executed:

### Initialize Git Repository
```sh
$ git init
```

### Download Python .gitignore
```sh
$ curl -o .gitignore https://www.toptal.com/developers/gitignore/api/python
```

### Create Private GitHub Repository
```sh
$ REPO_NAME=$(basename "$PWD")
$ gh repo create "$REPO_NAME" --private
```

### Configure Local Git Settings
Replace `<user-name>` and `<user-email>` with the values provided when prompted:
```sh
$ git config --local user.name "<user-name>"
$ git config --local user.email "<user-email>"
```

### Add Remote Origin
```sh
$ git remote add origin https://github.com/<username>/<repo-name>.git
```

### Initial Commit and Push
```sh
$ git add .
$ git commit -m "Initial commit"
$ git branch -M main
$ git push -u origin main
```