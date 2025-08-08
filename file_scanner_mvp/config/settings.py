# config/settings.py
from dataclasses import dataclass
from typing import List, Set
from pathlib import Path

@dataclass
class ScannerSettings:
    """Configuration settings for the file scanner"""
    max_file_size: int = 8192  # 8KB
    default_output_format: str = "txt"
    show_hidden_files: bool = False
    show_hidden_directories: bool = False

    # Additional exclusion patterns
    excluded_extensions: Set[str] = None
    excluded_directories: Set[str] = None
    excluded_files: Set[str] = None

    def __post_init__(self):
        """Initialize default exclusion sets if None"""
        if self.excluded_extensions is None:
            self.excluded_extensions = {'.pyc', '.pyo', '.pyd', '__pycache__'}

        if self.excluded_directories is None:
            self.excluded_directories = {'.git', '.svn', '.hg', 'node_modules', '__pycache__'}

        if self.excluded_files is None:
            self.excluded_files = {'.DS_Store', 'Thumbs.db', '.gitignore'}

    def should_show_item(self, path: Path) -> bool:
        """Determine if an item should be shown based on settings"""
        # Check if it's a hidden item (starts with .)
        if path.name.startswith('.'):
            if path.is_dir() and not self.show_hidden_directories:
                return False
            elif path.is_file() and not self.show_hidden_files:
                return False

        # Check exclusion lists
        if path.is_dir() and path.name in self.excluded_directories:
            return False

        if path.is_file():
            if path.name in self.excluded_files:
                return False
            if path.suffix.lower() in self.excluded_extensions:
                return False

        return True

# Global settings instance
settings = ScannerSettings()
