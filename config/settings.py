# config/settings.py
import os
from dataclasses import dataclass, field
from typing import List, Set, Dict, Any
from pathlib import Path

@dataclass
class ScannerSettings:
    """Enhanced configuration settings for the file scanner"""

    # Core settings
    max_file_size: int = 8192  # 8KB default
    default_output_format: str = "txt"
    show_hidden_files: bool = False
    show_hidden_directories: bool = False

    # Performance settings
    max_workers: int = 4  # Number of threads for scanning
    chunk_size: int = 4096  # Chunk size for streaming reads
    cache_size: int = 1000  # LRU cache size for file type detection

    # Compression settings
    default_compression: str = "gzip"  # gzip, bz2, lzma, none
    compression_level: int = 6  # 1-9 for gzip/bz2, 0-9 for lzma
    auto_compress_threshold: int = 1024 * 1024  # Auto-compress files > 1MB

    # UI settings
    use_vim_keys: bool = True
    show_file_icons: bool = True
    progress_update_interval: float = 0.05  # seconds

    # Exclusion patterns
    excluded_extensions: Set[str] = field(default_factory=lambda: {
        # Compiled/Binary
        '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib', '.exe',
        # Archives
        '.zip', '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar',
        # Images
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg',
        # Audio/Video
        '.mp3', '.wav', '.flac', '.mp4', '.avi', '.mkv', '.mov',
        # Documents (binary)
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        # Other
        '.db', '.sqlite', '.sqlite3'
    })

    excluded_directories: Set[str] = field(default_factory=lambda: {
        # Version control
        '.git', '.svn', '.hg', '.bzr',
        # Dependencies
        'node_modules', 'venv', 'env', '__pycache__', 'target',
        # IDE/Editor
        '.vscode', '.idea', '.eclipse', 'bin', 'obj',
        # Build artifacts
        'build', 'dist', '.gradle', '.maven',
        # System
        '.DS_Store', 'Thumbs.db', '$RECYCLE.BIN'
    })

    excluded_files: Set[str] = field(default_factory=lambda: {
        '.DS_Store', 'Thumbs.db', '.gitignore', '.gitkeep',
        'desktop.ini', '.directory'
    })

    # Advanced settings
    text_file_extensions: Set[str] = field(default_factory=lambda: {
        # Programming languages
        '.py', '.pyw', '.js', '.jsx', '.ts', '.tsx', '.html', '.htm',
        '.css', '.scss', '.sass', '.less', '.json', '.xml', '.yaml', '.yml',
        '.c', '.h', '.cpp', '.hpp', '.cc', '.cxx', '.java', '.kt', '.scala',
        '.rb', '.php', '.go', '.rs', '.swift', '.dart', '.r', '.m', '.mm',
        '.pl', '.pm', '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
        '.sql', '.lua', '.tcl', '.vb', '.vbs', '.asm', '.s',

        # Configuration files
        '.ini', '.cfg', '.conf', '.config', '.toml', '.properties',
        '.env', '.profile', '.bashrc', '.zshrc', '.vimrc',

        # Documentation
        '.md', '.rst', '.txt', '.text', '.rtf', '.tex', '.latex',
        '.adoc', '.asciidoc', '.org',

        # Data files
        '.csv', '.tsv', '.log', '.out', '.err',

        # Web files
        '.vue', '.svelte', '.ejs', '.hbs', '.mustache', '.twig',

        # Markup and styling
        '.xhtml', '.xsl', '.xslt', '.dtd', '.rss', '.atom',

        # Scripts and automation
        '.awk', '.sed', '.makefile', '.mk', '.cmake', '.dockerfile',
        '.docker-compose', '.github', '.gitlab-ci',

        # Other text formats
        '.diff', '.patch', '.gitignore', '.gitattributes',
        '.editorconfig', '.prettierrc', '.eslintrc'
    })

    # File size limits by type
    size_limits: Dict[str, int] = field(default_factory=lambda: {
        '.log': 16384,      # 16KB for log files
        '.txt': 32768,      # 32KB for text files
        '.md': 65536,       # 64KB for markdown files
        '.json': 131072,    # 128KB for JSON files
        'default': 8192     # 8KB default
    })

    def __post_init__(self):
        """Post-initialization setup and validation"""
        # Ensure max_workers is reasonable
        self.max_workers = max(1, min(16, self.max_workers))

        # Ensure compression level is valid
        self.compression_level = max(1, min(9, self.compression_level))

        # Set environment-based overrides
        self._apply_environment_overrides()

        # Validate paths exist for common directories
        self._validate_settings()

    def _apply_environment_overrides(self):
        """Apply settings from environment variables"""
        env_mappings = {
            'SCANNER_MAX_FILE_SIZE': ('max_file_size', int),
            'SCANNER_MAX_WORKERS': ('max_workers', int),
            'SCANNER_SHOW_HIDDEN': ('show_hidden_files', lambda x: x.lower() in ('true', '1', 'yes')),
            'SCANNER_DEFAULT_FORMAT': ('default_output_format', str),
            'SCANNER_COMPRESSION': ('default_compression', str),
            'SCANNER_COMPRESSION_LEVEL': ('compression_level', int),
        }

        for env_var, (attr, converter) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                try:
                    setattr(self, attr, converter(value))
                except (ValueError, TypeError):
                    pass  # Ignore invalid environment values

    def _validate_settings(self):
        """Validate and adjust settings as needed"""
        # Ensure compression algorithm is valid
        valid_compressions = {'gzip', 'bz2', 'lzma', 'none'}
        if self.default_compression not in valid_compressions:
            self.default_compression = 'gzip'

        # Ensure output format is valid
        valid_formats = {'txt', 'json', 'csv'}
        if self.default_output_format not in valid_formats:
            self.default_output_format = 'txt'

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

    def get_file_size_limit(self, file_path: Path) -> int:
        """Get the appropriate file size limit for a given file"""
        extension = file_path.suffix.lower()
        return self.size_limits.get(extension, self.size_limits.get('default', self.max_file_size))

    def is_text_file_by_extension(self, file_path: Path) -> bool:
        """Quick check if file is text based on extension only"""
        return file_path.suffix.lower() in self.text_file_extensions

    def should_auto_compress(self, estimated_size: int) -> bool:
        """Determine if output should be auto-compressed based on size"""
        return estimated_size > self.auto_compress_threshold

    def get_recommended_compression(self, file_count: int, estimated_size: int) -> str:
        """Get recommended compression algorithm based on content"""
        if not self.should_auto_compress(estimated_size):
            return 'none'

        # For small files, use gzip (fastest)
        if file_count < 100:
            return 'gzip'

        # For medium files, use bz2 (good balance)
        if estimated_size < 10 * 1024 * 1024:  # 10MB
            return 'bz2'

        # For large files, use lzma (best compression)
        return 'lzma'

    def update_from_dict(self, config_dict: Dict[str, Any]):
        """Update settings from a dictionary (useful for config files)"""
        for key, value in config_dict.items():
            if hasattr(self, key):
                # Handle set conversion for exclusion lists
                if key in ('excluded_extensions', 'excluded_directories', 'excluded_files', 'text_file_extensions'):
                    if isinstance(value, (list, tuple)):
                        value = set(value)

                setattr(self, key, value)

        # Re-validate after updates
        self._validate_settings()

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary format"""
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith('_'):
                # Convert sets to lists for JSON serialization
                if isinstance(value, set):
                    value = list(value)
                result[key] = value
        return result

    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about current cache settings"""
        return {
            'cache_size': self.cache_size,
            'chunk_size': self.chunk_size,
            'max_workers': self.max_workers,
            'progress_update_interval': self.progress_update_interval
        }

    def get_compression_info(self) -> Dict[str, Any]:
        """Get information about current compression settings"""
        return {
            'default_compression': self.default_compression,
            'compression_level': self.compression_level,
            'auto_compress_threshold': self.auto_compress_threshold,
            'auto_compress_threshold_mb': self.auto_compress_threshold / (1024 * 1024)
        }

    def reset_to_defaults(self):
        """Reset all settings to their default values"""
        # Store original values
        defaults = {
            'max_file_size': 8192,
            'default_output_format': 'txt',
            'show_hidden_files': False,
            'show_hidden_directories': False,
            'max_workers': 4,
            'chunk_size': 4096,
            'cache_size': 1000,
            'default_compression': 'gzip',
            'compression_level': 6,
            'auto_compress_threshold': 1024 * 1024,
            'use_vim_keys': True,
            'show_file_icons': True,
            'progress_update_interval': 0.05
        }

        for key, value in defaults.items():
            setattr(self, key, value)

        # Reset collections to defaults
        self.__post_init__()

    def create_user_profile(self, profile_name: str) -> Dict[str, Any]:
        """Create a user profile with current settings"""
        return {
            'profile_name': profile_name,
            'created': time.time(),
            'settings': self.to_dict()
        }

    def optimize_for_large_directories(self):
        """Optimize settings for scanning large directories"""
        self.max_workers = min(8, os.cpu_count() or 4)
        self.chunk_size = 8192  # Larger chunks for better I/O
        self.cache_size = 2000  # Larger cache
        self.progress_update_interval = 0.1  # Less frequent updates
        self.auto_compress_threshold = 512 * 1024  # Compress sooner

    def optimize_for_small_files(self):
        """Optimize settings for scanning many small files"""
        self.max_workers = min(6, os.cpu_count() or 4)
        self.chunk_size = 1024  # Smaller chunks
        self.cache_size = 3000  # Larger cache for file types
        self.progress_update_interval = 0.02  # More frequent updates
        self.max_file_size = 4096  # Smaller file size limit

    def optimize_for_code_projects(self):
        """Optimize settings specifically for code project scanning"""
        self.show_hidden_files = True  # Show .env, .gitignore, etc.
        self.excluded_directories.update({
            'node_modules', '.next', '.nuxt', 'dist', 'build',
            'coverage', '.nyc_output', '.pytest_cache'
        })
        self.max_file_size = 65536  # 64KB for code files
        self.default_compression = 'gzip'  # Good balance for code

# Global settings instance with environment variable support
import time
settings = ScannerSettings()

# Configuration loading functions
def load_config_from_file(config_path: Path) -> Dict[str, Any]:
    """Load configuration from a file (JSON or YAML)"""
    try:
        import json
        if config_path.suffix.lower() == '.json':
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)

        # Try YAML if available
        try:
            import yaml
            if config_path.suffix.lower() in ('.yml', '.yaml'):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
        except ImportError:
            pass

    except Exception:
        pass

    return {}

def save_config_to_file(config_dict: Dict[str, Any], config_path: Path):
    """Save configuration to a file"""
    try:
        import json
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)

        return True
    except Exception:
        return False

def get_config_dir() -> Path:
    """Get the user configuration directory"""
    if os.name == 'nt':  # Windows
        config_dir = Path(os.environ.get('APPDATA', Path.home())) / 'FileScanner'
    else:  # Unix-like
        config_dir = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')) / 'file_scanner'

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def load_user_config():
    """Load user configuration if it exists"""
    config_file = get_config_dir() / 'config.json'
    if config_file.exists():
        config_dict = load_config_from_file(config_file)
        if config_dict:
            settings.update_from_dict(config_dict)

def save_user_config():
    """Save current settings as user configuration"""
    config_file = get_config_dir() / 'config.json'
    return save_config_to_file(settings.to_dict(), config_file)

# Load user config on import
try:
    load_user_config()
except Exception:
    pass  # Ignore errors during config loading
