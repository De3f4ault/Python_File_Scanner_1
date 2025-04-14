import magic
from pathlib import Path

class FileScanner:
    def __init__(self, max_size=8192):
        self.max_size = max_size  # Maximum file size to read (default: 8KB)
        self.mime = magic.Magic(mime=True)  # For detecting file types
        self.progress_callback = None  # Callback for progress updates

    def set_progress_callback(self, callback):
        """Set a callback function for progress tracking"""
        self.progress_callback = callback

    def is_text_file(self, file_path):
        """Check if a file is a text file using libmagic"""
        try:
            return "text" in self.mime.from_file(str(file_path))
        except Exception:
            return False

    def read_file(self, file_path):
        """Read file content safely, up to max_size"""
        try:
            with open(file_path, "rb") as f:
                return f.read(self.max_size).decode("utf-8", errors="ignore")
        except Exception:
            return None

    def scan_directory(self, directory):
        """Scan a directory for text files and extract their contents"""
        results = []
        paths = list(Path(directory).rglob("*"))  # Recursively find all files/directories
        total = len(paths)

        for i, path in enumerate(paths, start=1):
            if self.progress_callback:
                self.progress_callback(i, total)  # Update progress

            if path.is_file() and self.is_text_file(path):  # Check if it's a text file
                content = self.read_file(path)
                if content is not None:
                    results.append({
                        "path": str(path),
                        "content": content.strip()
                    })

        if self.progress_callback:
            self.progress_callback(total, total)  # Ensure progress reaches 100%
        return results
