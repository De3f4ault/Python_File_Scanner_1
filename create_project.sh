#!/bin/bash

# Define the project root directory
PROJECT_ROOT="file_scanner_mvp"

# Create the project directory
mkdir -p "$PROJECT_ROOT"

# Create core modules
mkdir -p "$PROJECT_ROOT/core"
touch "$PROJECT_ROOT/core/__init__.py"
touch "$PROJECT_ROOT/core/directory_navigator.py"
touch "$PROJECT_ROOT/core/file_scanner.py"
touch "$PROJECT_ROOT/core/content_processor.py"

# Create output handlers
mkdir -p "$PROJECT_ROOT/output_handlers"
touch "$PROJECT_ROOT/output_handlers/__init__.py"
touch "$PROJECT_ROOT/output_handlers/txt_handler.py"
touch "$PROJECT_ROOT/output_handlers/json_handler.py"
touch "$PROJECT_ROOT/output_handlers/csv_handler.py"

# Create UI components
mkdir -p "$PROJECT_ROOT/ui"
touch "$PROJECT_ROOT/ui/__init__.py"
touch "$PROJECT_ROOT/ui/terminal_ui.py"
touch "$PROJECT_ROOT/ui/utils.py"

# Create configuration settings
mkdir -p "$PROJECT_ROOT/config"
touch "$PROJECT_ROOT/config/__init__.py"
touch "$PROJECT_ROOT/config/settings.py"

# Create tests directory
mkdir -p "$PROJECT_ROOT/tests"
touch "$PROJECT_ROOT/tests/__init__.py"
touch "$PROJECT_ROOT/tests/test_directory_navigator.py"
touch "$PROJECT_ROOT/tests/test_file_scanner.py"
touch "$PROJECT_ROOT/tests/test_output_handlers.py"

# Create main entry point and other files
touch "$PROJECT_ROOT/application.py"
touch "$PROJECT_ROOT/README.md"

# Add placeholder content to README.md
cat <<EOL > "$PROJECT_ROOT/README.md"
# File Scanner MVP

Terminal-based utility to navigate directories, scan text files, and generate reports.

## Features
- Interactive directory navigation (Vim-like keybindings)
- Output in .txt, .json, and .csv formats
- Cross-platform support

## Setup
1. Install dependencies: \`pip install -r requirements.txt\`
2. Run the application: \`python application.py\`

## License
MIT
EOL

# Add dependencies to requirements.txt with platform-specific conditions
cat <<EOL > "$PROJECT_ROOT/requirements.txt"
# Core dependencies
curses
python-magic >= 0.4.27
pytest >= 7.0

# Platform-specific dependencies
windows-curses; sys_platform == 'win32'
EOL

echo "Project structure created successfully!"
echo "To install dependencies: pip install -r requirements.txt"
