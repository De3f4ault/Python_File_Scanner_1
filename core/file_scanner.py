import magic
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from config.settings import settings

class FileScanner:
    def __init__(self, max_size=None, max_workers=4):
        self.max_size = max_size or settings.max_file_size
        self.mime = magic.Magic(mime=True)
        self.progress_callback = None
        self.include_hidden = settings.show_hidden_files
        self.max_workers = max_workers

        # Caching for performance
        self._mime_cache = {}
        self._text_extensions = {
            '.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.md',
            '.yml', '.yaml', '.ini', '.cfg', '.conf', '.log', '.sh', '.bat',
            '.csv', '.tsv', '.sql', '.toml', '.rst', '.tex', '.c', '.cpp',
            '.h', '.hpp', '.java', '.php', '.rb', '.go', '.rs', '.swift',
            '.kt', '.scala', '.clj', '.hs', '.elm', '.dart', '.vue', '.jsx',
            '.tsx', '.scss', '.sass', '.less', '.styl', '.coffee', '.ts'
        }

        # Thread-safe counters
        self._lock = threading.Lock()
        self._processed_count = 0
        self._skipped_count = 0

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

    @lru_cache(maxsize=1000)
    def is_text_file_cached(self, file_path_str):
        """Cached version of text file detection with smart fallback"""
        file_path = Path(file_path_str)

        # Step 1: Quick extension check (fastest)
        if file_path.suffix.lower() in self._text_extensions:
            return True

        # Step 2: Check cache
        if file_path_str in self._mime_cache:
            return self._mime_cache[file_path_str]

        # Step 3: MIME detection (slower, cache result)
        try:
            mime_type = self.mime.from_file(str(file_path))
            text_types = [
                'text/', 'application/json', 'application/xml',
                'application/javascript', 'application/x-sh',
                'application/x-python', 'application/x-perl',
                'application/x-ruby', 'application/x-php'
            ]
            is_text = any(mime_type.startswith(t) for t in text_types)
            self._mime_cache[file_path_str] = is_text
            return is_text

        except Exception:
            # Fallback: assume non-text for unknown files
            self._mime_cache[file_path_str] = False
            return False

    def is_text_file(self, file_path):
        """Public interface using cached version"""
        return self.is_text_file_cached(str(file_path))

    def read_file_streaming(self, file_path, max_size=None):
        """Read file in chunks to handle large files efficiently"""
        max_size = max_size or self.max_size

        try:
            content_parts = []
            bytes_read = 0

            with open(file_path, "rb") as f:
                while bytes_read < max_size:
                    chunk_size = min(4096, max_size - bytes_read)
                    chunk = f.read(chunk_size)

                    if not chunk:  # EOF
                        break

                    content_parts.append(chunk)
                    bytes_read += len(chunk)

            # Combine chunks and decode
            full_content = b''.join(content_parts)
            return full_content.decode("utf-8", errors="ignore")

        except Exception as e:
            return f"[Error reading file: {str(e)}]"

    def get_file_preview(self, file_path, lines=10):
        """Get first few lines of a file for preview"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                preview_lines = []
                for i, line in enumerate(f):
                    if i >= lines:
                        break
                    preview_lines.append(line.rstrip())

                return "\n".join(preview_lines)
        except Exception as e:
            return f"[Error reading preview: {str(e)}]"

    def read_file(self, file_path):
        """Read file content safely, up to max_size - now uses streaming"""
        return self.read_file_streaming(file_path)

    def _collect_all_files(self, root_path):
        """Recursively collect all file paths for processing"""
        all_files = []

        def collect_paths(path):
            """Recursively collect paths, respecting directory filters"""
            try:
                for item in path.iterdir():
                    if item.is_dir():
                        if self.should_process_directory(item):
                            collect_paths(item)  # Recurse into allowed directories
                    elif item.is_file():
                        all_files.append(item)
            except PermissionError:
                pass  # Skip directories we can't access

        collect_paths(root_path)
        return all_files

    def _process_single_file(self, file_path):
        """Process a single file in a thread-safe manner"""
        try:
            if self.should_process_file(file_path) and self.is_text_file(file_path):
                content = self.read_file(file_path)

                with self._lock:
                    self._processed_count += 1
                    current_processed = self._processed_count
                    current_skipped = self._skipped_count

                # Update progress
                if self.progress_callback:
                    total = current_processed + current_skipped
                    self.progress_callback(total, self._total_files,
                                         current_processed, current_skipped, str(file_path))

                return {
                    "path": str(file_path),
                    "content": content.strip(),
                    "size": file_path.stat().st_size,
                    "is_hidden": file_path.name.startswith('.'),
                    "modified": file_path.stat().st_mtime,
                    "extension": file_path.suffix.lower()
                }
            else:
                with self._lock:
                    self._skipped_count += 1
                    current_processed = self._processed_count
                    current_skipped = self._skipped_count

                # Update progress for skipped files too
                if self.progress_callback:
                    total = current_processed + current_skipped
                    self.progress_callback(total, self._total_files,
                                         current_processed, current_skipped, str(file_path))
                return None

        except Exception as e:
            with self._lock:
                self._skipped_count += 1
                current_processed = self._processed_count
                current_skipped = self._skipped_count

            if self.progress_callback:
                total = current_processed + current_skipped
                self.progress_callback(total, self._total_files,
                                     current_processed, current_skipped, f"Error: {str(file_path)}")
            return None

    def scan_directory_threaded(self, directory, include_hidden=None):
        """Multi-threaded directory scanning with enhanced progress tracking"""
        if include_hidden is not None:
            self.include_hidden = include_hidden

        # Reset counters
        with self._lock:
            self._processed_count = 0
            self._skipped_count = 0

        results = []

        # Collect all file paths first
        all_files = self._collect_all_files(Path(directory))
        self._total_files = len(all_files)

        if self._total_files == 0:
            return {
                'files': results,
                'stats': {
                    'total_paths': 0,
                    'files_scanned': 0,
                    'files_skipped': 0,
                    'include_hidden': self.include_hidden
                }
            }

        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {executor.submit(self._process_single_file, f): f for f in all_files}

            # Collect results as they complete
            for future in as_completed(future_to_file):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except Exception as e:
                    # Handle any unexpected exceptions
                    with self._lock:
                        self._skipped_count += 1

        # Final progress update
        if self.progress_callback:
            self.progress_callback(self._total_files, self._total_files,
                                 self._processed_count, self._skipped_count, "Scan Complete")

        return {
            'files': results,
            'stats': {
                'total_paths': self._total_files,
                'files_scanned': self._processed_count,
                'files_skipped': self._skipped_count,
                'include_hidden': self.include_hidden,
                'compression_recommended': self._processed_count > 10  # Recommend compression for large scans
            }
        }

    def scan_directory(self, directory, include_hidden=None):
        """Legacy single-threaded method for compatibility"""
        return self.scan_directory_threaded(directory, include_hidden)

    def clear_cache(self):
        """Clear internal caches - useful for long-running processes"""
        self.is_text_file_cached.cache_clear()
        self._mime_cache.clear()

    def get_cache_stats(self):
        """Get statistics about cache performance"""
        cache_info = self.is_text_file_cached.cache_info()
        return {
            'lru_cache_hits': cache_info.hits,
            'lru_cache_misses': cache_info.misses,
            'lru_cache_size': cache_info.currsize,
            'mime_cache_size': len(self._mime_cache)
        }
