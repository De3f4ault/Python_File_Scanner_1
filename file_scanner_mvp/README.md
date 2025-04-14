📁 Python File Scanner MVP

A terminal-based Python application designed to navigate directories, scan text files, and generate structured reports in various formats.
🧭 Features
📂 Directory Navigation

    Interactive browsing using arrow keys.

    Navigate to parent directories and select target folders.

📄 File Scanning

    Automatically detects text files based on content.

    Reads file contents up to a configurable size limit (default: 8KB).

📝 Report Generation

    Supports multiple output formats:

        .txt: Plain text report with file paths and contents.

        .json: Structured JSON representation of file data.

        .csv: Tabular format with file paths and contents.

        .pdf: PDF document with formatted file contents.

        .epub: E-book format for portable documentation.

    Includes a visual progress bar during processing.

🎨 Interactive UI

    User-friendly terminal interface with color-coded elements.

    Displays headers, footers, and dynamic feedback (e.g., error messages, success notifications).

⚠️ Error Handling

    Gracefully handles permission errors, unsupported formats, and invalid inputs.

    Provides clear feedback to the user via pop-up messages.

🖥️ Cross-Platform Compatibility

    Works on Unix-like systems (Linux, macOS) and Windows (requires windows-curses).

🛠️ Technical Details
📁 Directory Structure

    application.py: Main entry point for the application.

    core/: Core logic for directory navigation, file scanning, and content processing.

    output_handlers/: Handlers for generating output in different formats.

    ui/: Terminal UI components built using curses.

    config/: Configuration settings (e.g., default output format, max file size).

📦 Dependencies

    curses: For terminal UI rendering.

    EbookLib: For generating .epub files.

    fpdf: For generating .pdf files.

    python-magic: For detecting file types.

    windows-curses: For compatibility with Windows systems.

🚀 Getting Started
Prerequisites

    Python 3.x

    Install dependencies:

pip install -r requirements.txt

Running the Application

python application.py

📚 Use Cases

    Code Audits: Scan directories containing source code and generate reports for review.

    Documentation: Create .pdf or .epub documents from text files for offline reading.

    Data Extraction: Extract and organize text data into structured formats like .csv or .json.

    System Monitoring: Scan logs or configuration files for troubleshooting or reporting.

🌟 Strengths

    Modularity: Each component (UI, file processing, output generation) is decoupled, making the codebase easy to extend and maintain.

    Customizability: Users can add new output formats by implementing additional handlers in the output_handlers module.

    User-Friendly: The curses-based UI provides an intuitive and responsive experience.

🔮 Future Enhancements

    Additional Formats: Support for more output formats (e.g., .html, .docx).

    Search Functionality: Allow users to search for specific keywords within files.

    Parallel Processing: Improve performance by processing files concurrently.

    GUI Version: Develop a graphical user interface for broader accessibility.

📄 License

This project is licensed under the MIT License.
