import magic
from pathlib import Path
from config.settings import settings

class FileScanner:
    def __init__(self, max_size=None):
        self.max_size = max_size or settings.max_file_size
        self.mime = magic.Magic(mime=True)
        self.progress_callback = None
        self.include_hidden = settings.show_hidden_files

    def set_progress_callback(self, callback):
        """Set a callback function for progress tracking"""
        self.progress_callback = callback

    def set_include_hidden(self, include_hidden: bool):
        """Set whether to include hidden files in scanning"""
        self.include_hidden = include_hidden

    def should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed based on settings"""
        # Check if file should be shown based on settings
        if not settings.should_show_item(file_path):
            return False

        # Additional check for hidden files if not explicitly including them
        if not self.include_hidden and file_path.name.startswith('.'):
            return False

        return True

    def should_process_directory(self, dir_path: Path) -> bool:
        """Determine if a directory should be processed (entered) during scanning"""
        # Check if directory should be processed based on settings
        if not settings.should_show_item(dir_path):
            return False

        # Additional check for hidden directories
        if not settings.show_hidden_directories and dir_path.name.startswith('.'):
            return False

        return True

    def is_text_file(self, file_path):
        """Check if a file is a text file using libmagic"""
        try:
            mime_type = self.mime.from_file(str(file_path))
            # Extended text file detection
            text_types = [
                'text/',
                'application/json',
                'application/xml',
                'application/javascript',
                'application/x-sh',
                'application/x-python',
            ]
            return any(mime_type.startswith(text_type) for text_type in text_types)
        except Exception:
            # Fallback: check common text file extensions
            text_extensions = {
                '.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.md',
                '.yml', '.yaml', '.ini', '.cfg', '.conf', '.log', '.sh', '.bat',
                '.csv', '.tsv', '.sql', '.toml', '.rst', '.tex'
            }
            return file_path.suffix.lower() in text_extensions

    def read_file(self, file_path):
        """Read file content safely, up to max_size"""
        try:
            with open(file_path, "rb") as f:
                content = f.read(self.max_size)
                return content.decode("utf-8", errors="ignore")
        except Exception as e:
            return f"[Error reading file: {str(e)}]"

    def scan_directory(self, directory, include_hidden=None):
        """Scan a directory for text files and extract their contents"""
        if include_hidden is not None:
            self.include_hidden = include_hidden

        results = []
        scanned_count = 0
        skipped_count = 0

        # Get all paths recursively, but filter during iteration
        all_paths = []
        root_path = Path(directory)

        def collect_paths(path):
            """Recursively collect paths, respecting directory filters"""
            try:
                for item in path.iterdir():
                    if item.is_dir():
                        if self.should_process_directory(item):
                            all_paths.append(item)
                            collect_paths(item)  # Recurse into allowed directories
                    elif item.is_file():
                        all_paths.append(item)
            except PermissionError:
                pass  # Skip directories we can't access

        collect_paths(root_path)
        total = len(all_paths)

        for i, path in enumerate(all_paths, start=1):
            if self.progress_callback:
                self.progress_callback(i, total, scanned_count, skipped_count)

            if path.is_file():
                if self.should_process_file(path) and self.is_text_file(path):
                    content = self.read_file(path)
                    if content is not None:
                        results.append({
                            "path": str(path),
                            "content": content.strip(),
                            "size": path.stat().st_size,
                            "is_hidden": path.name.startswith('.'),
                            "modified": path.stat().st_mtime
                        })
                        scanned_count += 1
                else:
                    skipped_count += 1

        if self.progress_callback:
            self.progress_callback(total, total, scanned_count, skipped_count)

        return {
            'files': results,
            'stats': {
                'total_paths': total,
                'files_scanned': scanned_count,
                'files_skipped': skipped_count,
                'include_hidden': self.include_hidden
            }
        }
