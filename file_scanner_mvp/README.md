Python File Scanner MVP

A terminal-based Python application for directory navigation, text file scanning, and multi-format report generation.

License: MIT
Project Overview

This utility enables users to:

    Browse directories using an interactive interface

    Scan text files with content detection

    Generate structured reports in multiple formats

Features
Directory Navigation

    Interactive browsing with arrow keys

    Navigate parent directories and select folders

    Cross-platform support (Unix/Linux, macOS, Windows)

File Scanning

    Automatic text file detection based on content

    Configurable file size limit (default: 8KB)

    Graceful error handling for permissions and unsupported formats

Report Generation

Supported Formats:

    .txt - Plain text with file paths and contents

    .json - Structured JSON representation

    .csv - Tabular format for data analysis

    .pdf - Formatted PDF documents

    .epub - Portable e-book format

UI Features:

    Color-coded terminal interface

    Progress visualization during processing

    Interactive pop-up messages and alerts

Project Structure
Copy

file_scanner_mvp/
├── application.py             # Main entry point
├── config/
│   └── settings.py            # Configuration
├── core/
│   ├── file_scanner.py        # File detection logic
│   └── navigator.py           # Directory navigation
├── output_handlers/
│   ├── csv_exporter.py
│   ├── epub_exporter.py
│   ├── json_exporter.py
│   ├── pdf_exporter.py
│   └── txt_exporter.py
├── tests/                     # Unit tests
└── ui/
    ├── base_ui.py
    ├── progress_ui.py
    └── view.py

Dependencies
Core Requirements
Copy

pip install -r requirements.txt

Main Libraries:

    curses / windows-curses - Terminal interface

    EbookLib - EPUB generation

    fpdf - PDF creation

    python-magic - File type detection

Getting Started
Prerequisites

    Python 3.10+

    pip package manager

Installation & Execution

    Clone the repository:

Copy

git clone https://github.com/De3f4ault/Python_File_Scanner_1.git
cd Python_File_Scanner_1/file_scanner_mvp

    Install dependencies:

Copy

pip install -r requirements.txt

    Run the application:

Copy

python application.py

Use Cases

    Code Audits: Scan source code directories for review

    Documentation: Create PDF/EPUB from text files

    Data Extraction: Organize text into CSV/JSON

    System Monitoring: Analyze logs and config files

Strengths

    Modular architecture for easy extension

    Customizable output handlers

    Intuitive curses-based UI

    Configurable scanning parameters

Future Enhancements

    Add HTML/DOCX export support

    Implement file content search

    Parallel processing for large directories

    Graphical user interface (GUI)

