# File Scanner

The **File Scanner** is a versatile, terminal-based Python utility designed to navigate directories, scan text files, and generate structured output reports in multiple formats (`.txt`, `.json`, `.csv`, `.pdf`, `.epub`). Its modular design, robust error handling, and support for customization make it an ideal tool for developers, analysts, and system administrators.

---

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Output Formats](#output-formats)
5. [Customization](#customization)
6. [Dependencies](#dependencies)
7. [Contributing](#contributing)
8. [License](#license)

---

## Features

- **Directory Navigation**:  
  - Browse directories interactively using arrow keys or Vim-like keybindings (`hjkl`).
  - Navigate back to parent directories and confirm selections seamlessly.
  
- **File Scanning**:  
  - Automatically detects text files based on binary content checks.
  - Reads file contents up to a configurable size limit (default: 8KB).
  - Supports metadata extraction (e.g., file size, modification date).

- **Output Generation**:  
  - Generate reports in various formats: `.txt`, `.json`, `.csv`, `.pdf`, `.epub`.
  - Enhanced TXT output with line numbers, metadata, and better formatting.
  - Customizable output templates (e.g., headers, footers).

- **Progress Tracking**:  
  - Real-time progress bar during scanning.
  - Completion confirmation with full output path.

- **Error Handling**:  
  - Prevents empty filenames and checks write permissions before saving.
  - Displays errors clearly in the terminal UI.

- **Cross-Platform Compatibility**:  
  - Works on Unix-like systems (Linux, macOS) and Windows (requires `windows-curses`).

---

## Installation

### Prerequisites
- Python 3.7 or higher.
- Dependencies listed in `requirements.txt`.

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/file-scanner.git
   cd file-scanner
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   > **Note for Windows Users**: The `windows-curses` library is included as an optional dependency in `requirements.txt` and will only be installed on Windows systems.

3. Run the application:
   ```bash
   python application.py
   ```

---

## Usage

1. **Navigate Directories**:
   - Use arrow keys (`↑`, `↓`, `←`, `→`) or Vim-like keybindings (`hjkl`) to browse directories.
   - Press `s` to confirm the selected directory for scanning.

2. **Configure Output**:
   - Enter a filename for the report (with validation).
   - Choose an output format: `.txt`, `.json`, `.csv`, `.pdf`, or `.epub`.
   - Select the save location interactively.

3. **Track Progress**:
   - A real-time progress bar will display the scanning status.
   - Upon completion, the full output path will be displayed.

4. **Verify Output**:
   - Check the generated file in the chosen directory.

---

## Output Formats

- **TXT**:  
  - Plain text report with file paths, contents, line numbers, and metadata.
  - Includes a table of contents for easy navigation.

- **JSON**:  
  - Structured JSON format with file paths and contents.

- **CSV**:  
  - Tabular format with columns for file paths and contents.

- **PDF**:  
  - Professional PDF reports with customizable templates.

- **EPUB**:  
  - eBook-friendly format for long-form content.

---

## Customization

- **Settings**:  
  Configure default settings in `config/settings.py`:
  - Maximum file size for scanning (default: 8KB).
  - Default output format (default: `.txt`).
  - Output directory path.

- **Output Templates**:  
  Customize output templates by modifying handlers in `output_handlers/`.

- **Keyboard Shortcuts**:  
  Add or modify keybindings in `ui/terminal_ui.py`.

---

## Dependencies

- `curses` (or `windows-curses` for Windows compatibility).
- `python-magic` for file type detection.
- `fpdf` for PDF generation.
- `EbookLib` for EPUB generation.
- Additional libraries for testing and advanced features.

Refer to `requirements.txt` for the complete list of dependencies.

---

## Contributing

We welcome contributions! Here's how you can help:

1. **Report Bugs**: Open an issue with detailed steps to reproduce the problem.
2. **Suggest Features**: Propose new features or improvements via issues.
3. **Submit Pull Requests**: Fork the repository, make your changes, and submit a PR.

### Development Guidelines
- Follow the existing code style and structure.
- Write unit tests for new features.
- Ensure cross-platform compatibility.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Future Enhancements

- Support for additional output formats (e.g., `.html`, `.docx`).
- Search functionality to find specific keywords within files.
- Parallel processing for improved performance with large directories.
- GUI version for broader accessibility.

---

## Acknowledgments

- Inspired by tools like LazyVim/Neovim for its intuitive navigation.
- Built using open-source libraries like `curses`, `python-magic`, `fpdf`, and `EbookLib`.

---

Feel free to reach out with questions, feedback, or feature requests! 🚀
