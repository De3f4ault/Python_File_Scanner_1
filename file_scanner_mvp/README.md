🧪 Python File Scanner MVP

A terminal-based Python application that allows users to navigate directories, scan text files, and generate structured reports in various formats.​
📌 Project Overview

This utility enables users to:​

    Browse Directories: Navigate through the file system using an interactive interface.​

    Select Files: Identify and process text files within the selected directory.​

    Generate Reports: Export the contents of scanned files into structured outputs such as .txt, .json, .csv, .pdf, and .epub.​

The application leverages Python's curses library for the terminal UI and integrates third-party libraries like EbookLib, fpdf, and python-magic for advanced output handling.​
✨ Features
📁 Directory Navigation

    Interactive browsing using arrow keys.​

    Navigate to parent directories and select target folders.​

📄 File Scanning

    Automatically detects text files based on content.​

    Reads file contents up to a configurable size limit (default: 8KB).​

📝 Report Generation

    Supports multiple output formats:​

        .txt: Plain text report with file paths and contents.​

        .json: Structured JSON representation of file data.​

        .csv: Tabular format with file paths and contents.​

        .pdf: PDF document with formatted file contents.​

        .epub: E-book format for portable documentation.​

    Includes a visual progress bar during processing.​

🎨 Interactive UI

    User-friendly terminal interface with color-coded elements.​

    Displays headers, footers, and dynamic feedback (e.g., error messages, success notifications).​

⚠️ Error Handling

    Gracefully handles permission errors, unsupported formats, and invalid inputs.​

    Provides clear feedback to the user via pop-up messages.​

🖥️ Cross-Platform Compatibility

    Works on Unix-like systems (Linux, macOS) and Windows (requires windows-curses).​

🧱 Project Structure

file_scanner_mvp/
├── application.py             # Main entry point for the application
├── config/
│   └── settings.py            # Configuration settings
├── core/
│   ├── file_scanner.py        # File detection logic
│   └── navigator.py           # Directory navigation logic
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

📦 Dependencies

Install the required packages using:

pip install -r requirements.txt

Main Libraries:

    curses / windows-curses – Terminal interface​

    EbookLib – EPUB generation​

    fpdf – PDF generation​

    python-magic – File type detection​

🚀 Getting Started
Prerequisites

    Python 3.x​

Running the Application

python application.py

Follow the on-screen instructions to:

    Browse and select a directory.​

    Choose an output format.​

    Export the scanned files.​

📚 Use Cases

    Code Audits: Scan directories containing source code and generate reports for review.​

    Documentation: Create .pdf or .epub documents from text files for offline reading.​

    Data Extraction: Extract and organize text data into structured formats like .csv or .json.​

    System Monitoring: Scan logs or configuration files for troubleshooting or reporting.​

🌟 Strengths

    Modularity: Each component (UI, file processing, output generation) is decoupled, making the codebase easy to extend and maintain.​

    Customizability: Users can add new output formats by implementing additional handlers in the output_handlers module.​

    User-Friendly: The curses-based UI provides an intuitive and responsive experience.​

🔮 Future Enhancements

    Additional Formats: Support for more output formats (e.g., .html, .docx).​

    Search Functionality: Allow users to search for specific keywords within files.​

    Parallel Processing: Improve performance by processing files concurrently.​

    GUI Version: Develop a graphical user interface for broader accessibility.​

📄 License

This project is licensed under the MIT License.
