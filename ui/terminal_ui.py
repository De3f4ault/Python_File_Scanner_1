import curses
import time
import threading
from pathlib import Path
from core.directory_navigator import DirectoryNavigator
from core.file_scanner import FileScanner
from core.content_processor import ContentProcessor
from output_handlers.compressed_handler import (
    CompressedTXTHandler, CompressedJSONHandler, CompressedCSVHandler,
    TXTHandler, JSONHandler, CSVHandler
)
from config.settings import settings

class TerminalUI:
    def __init__(self):
        self.navigator = DirectoryNavigator()

        # Enhanced handlers with compression support
        self.handlers = {
            "txt": TXTHandler,
            "json": JSONHandler,
            "csv": CSVHandler,
            "txt.gz": (CompressedTXTHandler, "gzip"),
            "json.gz": (CompressedJSONHandler, "gzip"),
            "csv.gz": (CompressedCSVHandler, "gzip"),
            "txt.bz2": (CompressedTXTHandler, "bz2"),
            "json.bz2": (CompressedJSONHandler, "bz2"),
            "csv.bz2": (CompressedCSVHandler, "bz2"),
            "txt.xz": (CompressedTXTHandler, "lzma"),
            "json.xz": (CompressedJSONHandler, "lzma"),
            "csv.xz": (CompressedCSVHandler, "lzma")
        }

        # Progress tracking
        self.scan_start_time = None
        self.last_update_time = 0
        self.current_progress = None
        self.scan_results = None
        self.scanning_active = False

    def draw(self, stdscr):
        """Main UI loop for navigation and interaction"""
        curses.curs_set(0)
        stdscr.nodelay(0)
        stdscr.timeout(100)
        stdscr.clear()

        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)     # Header/Footer
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)    # Normal text
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)    # Selected item
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)      # Error messages
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Hidden items
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Status info
        curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)     # Progress bars

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            # Draw header with enhanced status
            header = " 🔍 File Scanner Pro "
            status = " [SELECTED]" if self.navigator.confirmed_path else ""
            hidden_status = " [SHOW HIDDEN]" if self.navigator.show_hidden else " [HIDE HIDDEN]"

            # Add performance info if available
            perf_info = ""
            if hasattr(self, 'last_scan_stats'):
                stats = self.last_scan_stats
                perf_info = f" | Scanned: {stats.get('files_scanned', 0)} files"

            path_str = f" Path: {self.navigator.current_path}{status}{hidden_status}{perf_info}"
            max_path_len = width - len(header) - 3
            if len(path_str) > max_path_len:
                path_str = path_str[:max_path_len] + "..."

            stdscr.addstr(0, 0, header, curses.color_pair(1) | curses.A_BOLD)
            stdscr.addstr(0, len(header), path_str.ljust(width - len(header)), curses.color_pair(1))

            # Draw enhanced item count info
            count_info = self.navigator.get_item_count_info()
            info_text = f" Items: {count_info['visible']}/{count_info['total']}"
            if count_info['hidden'] > 0:
                info_text += f" ({count_info['hidden']} hidden)"

            # Add current item info
            current_item = self.navigator.get_current_item_path()
            if current_item and current_item.is_file():
                try:
                    size = current_item.stat().st_size
                    if size < 1024:
                        size_str = f"{size}B"
                    elif size < 1024 * 1024:
                        size_str = f"{size//1024}KB"
                    else:
                        size_str = f"{size//(1024*1024)}MB"
                    info_text += f" | Current: {size_str}"
                except:
                    pass

            stdscr.addstr(1, 0, info_text, curses.color_pair(6))

            # Draw file list with enhanced visualization
            items = self.navigator.list_items()
            list_start_y = 3

            for idx, item in enumerate(items):
                y = idx + list_start_y
                if y >= height - 3:  # Leave space for enhanced footer
                    break

                max_item_len = width - 10
                display_item = item[:max_item_len] + ".." if len(item) > max_item_len else item

                # Enhanced color coding
                item_path = self.navigator.current_path / item
                if idx == self.navigator.selected:
                    attr = curses.color_pair(3) | curses.A_BOLD  # Selected (green + bold)
                elif item.startswith('.'):
                    attr = curses.color_pair(5)  # Hidden (yellow)
                elif item_path.is_dir():
                    attr = curses.color_pair(2) | curses.A_BOLD  # Directory (white + bold)
                else:
                    attr = curses.color_pair(2)  # File (white)

                # Enhanced indicators
                if item_path.is_dir():
                    icon = "📁"
                elif item.startswith('.'):
                    icon = "🔒"
                else:
                    # File type icons based on extension
                    ext = item_path.suffix.lower()
                    icon_map = {
                        '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨',
                        '.json': '📋', '.xml': '📄', '.md': '📝', '.txt': '📄',
                        '.yml': '⚙️', '.yaml': '⚙️', '.log': '📊', '.csv': '📊'
                    }
                    icon = icon_map.get(ext, '📄')

                indicator = "." if item.startswith('.') else " "
                prefix = f"{'►' if idx == self.navigator.selected else ' '}{indicator}"

                stdscr.addstr(y, 0, f"{prefix} {icon} {display_item}".ljust(width-1), attr)

            # Draw enhanced footer with more keybindings
            footer_lines = [
                "↑↓/jk: Navigate | →/l: Enter | ←/h: Up | s: Scan | t: Toggle Hidden | q: Quit",
                f"Hidden: {'ON' if self.navigator.show_hidden else 'OFF'} | "
                f"Current: {'Hidden' if self.navigator.is_current_item_hidden() else 'Visible'} | "
                f"Threads: {settings.max_file_size//1024}KB limit"
            ]

            for i, footer_line in enumerate(footer_lines):
                footer_y = height - len(footer_lines) + i
                if footer_y >= 0:
                    stdscr.addstr(footer_y, 0, footer_line[:width], curses.color_pair(1))

            # Handle enhanced input (including vim-style keys)
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key in (curses.KEY_RIGHT, 10, 13, ord('l')):  # Enter (with vim 'l')
                self.navigator.enter()
            elif key in (curses.KEY_LEFT, ord('h')):  # Up (with vim 'h')
                self.navigator.go_up()
            elif key in (curses.KEY_UP, ord('k')):  # Up (with vim 'k')
                self.navigator.select_prev()
            elif key in (curses.KEY_DOWN, ord('j')):  # Down (with vim 'j')
                self.navigator.select_next()
            elif key in (ord('t'), ord('H')):  # Toggle hidden files
                self.navigator.toggle_hidden_visibility()
            elif key == ord('s'):  # Start scan
                confirmed_path = self.navigator.confirm_directory()
                if confirmed_path:
                    self.show_scan_options(stdscr, confirmed_path)
            elif key == ord('p'):  # Preview file (new feature)
                self.show_file_preview(stdscr)
            elif key == ord('r'):  # Refresh directory
                self.navigator.selected = 0

    def show_file_preview(self, stdscr):
        """Show preview of currently selected file"""
        current_item = self.navigator.get_current_item_path()
        if not current_item or not current_item.is_file():
            return

        height, width = stdscr.getmaxyx()

        try:
            scanner = FileScanner()
            if scanner.is_text_file(current_item):
                preview = scanner.get_file_preview(current_item, lines=height-6)
            else:
                preview = "[Binary file - no preview available]"
        except Exception as e:
            preview = f"[Error loading preview: {str(e)}]"

        while True:
            stdscr.clear()

            # Header
            header = f" Preview: {current_item.name} "
            stdscr.addstr(0, 0, header, curses.color_pair(1) | curses.A_BOLD)
            stdscr.addstr(1, 0, "─" * min(len(header), width), curses.color_pair(1))

            # Content
            lines = preview.split('\n')
            for i, line in enumerate(lines[:height-4]):
                if i + 2 < height - 2:
                    display_line = line[:width-1] if len(line) < width else line[:width-4] + "..."
                    stdscr.addstr(i + 2, 0, display_line, curses.color_pair(2))

            # Footer
            footer = "Press any key to return..."
            stdscr.addstr(height-1, 0, footer, curses.color_pair(1))

            stdscr.refresh()
            if stdscr.getch():
                break

    def show_scan_options(self, stdscr, scan_path):
        """Enhanced scan options with threading and compression info"""
        height, width = stdscr.getmaxyx()

        # Ask about hidden files and threading
        include_hidden = False
        max_workers = 4

        option_index = 0
        options = ['include_hidden', 'max_workers']

        while True:
            stdscr.clear()

            # Header
            stdscr.addstr(height//2 - 4, 2, "🔧 Scan Configuration", curses.color_pair(1) | curses.A_BOLD)
            stdscr.addstr(height//2 - 3, 2, f"Directory: {scan_path}")

            # Options
            hidden_text = f"Include hidden files: {'YES' if include_hidden else 'NO'}"
            worker_text = f"Worker threads: {max_workers}"

            attr_hidden = curses.color_pair(3) if option_index == 0 else curses.color_pair(2)
            attr_workers = curses.color_pair(3) if option_index == 1 else curses.color_pair(2)

            stdscr.addstr(height//2 - 1, 2, f"► {hidden_text}" if option_index == 0 else f"  {hidden_text}", attr_hidden)
            stdscr.addstr(height//2, 2, f"► {worker_text}" if option_index == 1 else f"  {worker_text}", attr_workers)

            # Instructions
            stdscr.addstr(height//2 + 2, 2, "↑↓: Select | ←→: Change | ENTER: Continue | q: Cancel")

            stdscr.refresh()

            key = stdscr.getch()
            if key == ord('q'):
                return
            elif key in (curses.KEY_UP, ord('k')):
                option_index = (option_index - 1) % len(options)
            elif key in (curses.KEY_DOWN, ord('j')):
                option_index = (option_index + 1) % len(options)
            elif key in (curses.KEY_LEFT, curses.KEY_RIGHT, ord('h'), ord('l')):
                if option_index == 0:  # Hidden files
                    include_hidden = not include_hidden
                elif option_index == 1:  # Worker threads
                    if key in (curses.KEY_RIGHT, ord('l')):
                        max_workers = min(16, max_workers + 1)
                    else:
                        max_workers = max(1, max_workers - 1)
            elif key in (10, 13):  # ENTER
                break

        self.show_output_prompt(stdscr, scan_path, include_hidden, max_workers)

    def show_output_prompt(self, stdscr, scan_path, include_hidden, max_workers):
        """Enhanced output prompt with compression options"""
        stdscr.nodelay(0)
        height, width = stdscr.getmaxyx()

        # Get filename
        while True:
            stdscr.clear()
            stdscr.addstr(height//2 - 3, 2, "📝 Output Configuration", curses.color_pair(1) | curses.A_BOLD)
            stdscr.addstr(height//2 - 2, 2, f"Scan will {'include' if include_hidden else 'exclude'} hidden files")
            stdscr.addstr(height//2 - 1, 2, f"Using {max_workers} worker threads")
            stdscr.addstr(height//2, 2, "Output filename: ")
            stdscr.refresh()

            curses.echo()
            filename = stdscr.getstr().decode('utf-8').strip()
            curses.noecho()

            if filename:
                break
            else:
                stdscr.addstr(height//2 + 1, 2, "❌ Filename cannot be empty!", curses.color_pair(4))
                stdscr.getch()

        # Enhanced format selection with compression
        formats = list(self.handlers.keys())
        selected_format = 0

        while True:
            stdscr.clear()
            stdscr.addstr(height//2 - 8, 2, "📦 Select Output Format:", curses.color_pair(1) | curses.A_BOLD)

            # Group formats for better display
            basic_formats = [f for f in formats if '.' not in f or f.count('.') == 1]
            compressed_formats = [f for f in formats if f.count('.') >= 2]

            stdscr.addstr(height//2 - 6, 2, "Basic Formats:", curses.color_pair(6))
            y_offset = height//2 - 5

            for i, fmt in enumerate(basic_formats):
                attr = curses.color_pair(3) if i == selected_format else curses.color_pair(2)
                marker = "►" if i == selected_format else " "
                compression_info = ""

                stdscr.addstr(y_offset + i, 4, f"{marker} {fmt}{compression_info}", attr)

            stdscr.addstr(y_offset + len(basic_formats) + 1, 2, "Compressed Formats (recommended):", curses.color_pair(6))

            for i, fmt in enumerate(compressed_formats):
                idx = len(basic_formats) + i
                attr = curses.color_pair(3) if idx == selected_format else curses.color_pair(2)
                marker = "►" if idx == selected_format else " "

                # Add compression info
                if 'gz' in fmt:
                    comp_info = " (fast, ~75% smaller)"
                elif 'bz2' in fmt:
                    comp_info = " (better compression, ~80% smaller)"
                elif 'xz' in fmt:
                    comp_info = " (best compression, ~85% smaller)"
                else:
                    comp_info = ""

                stdscr.addstr(y_offset + len(basic_formats) + 2 + i, 4, f"{marker} {fmt}{comp_info}", attr)

            # Instructions
            stdscr.addstr(height - 3, 2, "↑↓: Select format | ENTER: Continue | q: Cancel")
            stdscr.refresh()

            key = stdscr.getch()
            if key == ord('q'):
                return
            elif key in (curses.KEY_UP, ord('k')):
                selected_format = (selected_format - 1) % len(formats)
            elif key in (curses.KEY_DOWN, ord('j')):
                selected_format = (selected_format + 1) % len(formats)
            elif key in (10, 13):
                break

        # Choose save directory
        save_navigator = DirectoryNavigator(start_path=str(Path.home()))
        confirmed_save_path = None

        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, f"💾 Save Location: {save_navigator.current_path}", curses.color_pair(1))
            stdscr.addstr(1, 0, "↑↓: Navigate | →: Enter dir | ←: Up | s: Confirm here | q: Cancel", curses.color_pair(1))

            items = save_navigator.list_items()
            for idx, item in enumerate(items):
                y = idx + 2
                if y >= height - 2:
                    break

                item_path = save_navigator.current_path / item
                icon = "📁" if item_path.is_dir() else "📄"
                attr = curses.color_pair(3) if idx == save_navigator.selected else curses.color_pair(2)
                marker = "►" if idx == save_navigator.selected else " "

                stdscr.addstr(y, 0, f"{marker} {icon} {item}".ljust(width-1), attr)

            stdscr.refresh()

            key = stdscr.getch()
            if key == ord('q'):
                return
            elif key in (curses.KEY_UP, ord('k')):
                save_navigator.select_prev()
            elif key in (curses.KEY_DOWN, ord('j')):
                save_navigator.select_next()
            elif key in (curses.KEY_RIGHT, ord('l')):
                save_navigator.enter()
            elif key in (curses.KEY_LEFT, ord('h')):
                save_navigator.go_up()
            elif key == ord('s'):
                confirmed_save_path = save_navigator.current_path
                break

        if confirmed_save_path:
            output_path = confirmed_save_path / filename
            selected_format_key = formats[selected_format]

            # Start scanning with progress
            self.start_scan_with_progress(stdscr, scan_path, output_path, selected_format_key,
                                        include_hidden, max_workers)

    def enhanced_progress_callback(self, current, total, scanned, skipped, current_file=""):
        """Enhanced progress callback with detailed tracking"""
        now = time.time()

        # Throttle updates to avoid flickering
        if now - self.last_update_time < 0.05:  # Update max 20 times per second
            return
        self.last_update_time = now

        if not self.scan_start_time:
            self.scan_start_time = now

        elapsed = now - self.scan_start_time
        if elapsed > 0 and current > 0:
            speed = current / elapsed
            eta = (total - current) / speed if speed > 0 else 0

            self.current_progress = {
                'current': current,
                'total': total,
                'scanned': scanned,
                'skipped': skipped,
                'percentage': (current / total * 100) if total > 0 else 0,
                'speed': speed,
                'eta': eta,
                'elapsed': elapsed,
                'current_file': current_file
            }

    def start_scan_with_progress(self, stdscr, scan_path, output_path, format_key, include_hidden, max_workers):
        """Start scanning with enhanced progress display"""
        height, width = stdscr.getmaxyx()

        # Initialize scanner with enhanced settings
        scanner = FileScanner(max_workers=max_workers)
        scanner.set_include_hidden(include_hidden)
        scanner.set_progress_callback(self.enhanced_progress_callback)

        # Reset progress tracking
        self.scan_start_time = time.time()
        self.current_progress = None
        self.scan_results = None
        self.scanning_active = True

        # Start scanning in background thread
        def scan_worker():
            try:
                result = scanner.scan_directory_threaded(scan_path, include_hidden)
                self.scan_results = result
                self.last_scan_stats = result.get('stats', {})
            except Exception as e:
                self.scan_results = {'error': str(e)}
            finally:
                self.scanning_active = False

        scan_thread = threading.Thread(target=scan_worker)
        scan_thread.daemon = True
        scan_thread.start()

        # Progress display loop
        while self.scanning_active:
            stdscr.clear()

            # Header
            stdscr.addstr(0, 0, "🔄 Scanning in Progress...", curses.color_pair(1) | curses.A_BOLD)
            stdscr.addstr(1, 0, f"📁 {scan_path}", curses.color_pair(6))

            if self.current_progress:
                p = self.current_progress

                # Progress bar
                bar_width = min(50, width - 20)
                filled = int(p['percentage'] * bar_width / 100)
                bar = "█" * filled + "░" * (bar_width - filled)

                stdscr.addstr(height//2 - 3, 2, f"Progress: [{bar}] {p['percentage']:.1f}%", curses.color_pair(7))
                stdscr.addstr(height//2 - 2, 2, f"Files: {p['current']}/{p['total']} | Speed: {p['speed']:.1f} files/s")
                stdscr.addstr(height//2 - 1, 2, f"Processed: {p['scanned']} | Skipped: {p['skipped']}")

                # ETA
                if p['eta'] > 0:
                    eta_min, eta_sec = divmod(int(p['eta']), 60)
                    stdscr.addstr(height//2, 2, f"ETA: {eta_min:02d}:{eta_sec:02d}")

                # Current file (truncated if too long)
                current_file = p.get('current_file', '')
                if current_file:
                    max_file_len = width - 20
                    if len(current_file) > max_file_len:
                        current_file = "..." + current_file[-(max_file_len-3):]
                    stdscr.addstr(height//2 + 2, 2, f"Current: {current_file}", curses.color_pair(5))
            else:
                stdscr.addstr(height//2, 2, "Initializing scan...")

            # Instructions
            stdscr.addstr(height - 2, 2, "Press 'q' to cancel scan", curses.color_pair(4))

            stdscr.refresh()

            # Check for cancel
            stdscr.timeout(100)
            key = stdscr.getch()
            if key == ord('q'):
                # Note: In a real implementation, you'd want to properly cancel the thread
                self.scanning_active = False
                return

        # Wait for thread to complete
        scan_thread.join()

        # Process results
        if self.scan_results and 'error' not in self.scan_results:
            self.save_results(stdscr, output_path, format_key, self.scan_results)
        else:
            error_msg = self.scan_results.get('error', 'Unknown error occurred') if self.scan_results else 'Scan cancelled'
            self.show_error(stdscr, f"Scan failed: {error_msg}")

    def save_results(self, stdscr, output_path, format_key, results):
        """Save scan results with the selected format and compression"""
        try:
            handler_info = self.handlers[format_key]

            if isinstance(handler_info, tuple):
                # Compressed format
                handler_class, compression = handler_info
                final_path = handler_class.write(results['files'], str(output_path),
                                               compression=compression, compression_level=6)
            else:
                # Standard format
                final_path = handler_info.write(results['files'], str(output_path))

            # Success message
            stats = results.get('stats', {})
            self.show_success(stdscr, final_path, stats)

        except Exception as e:
            self.show_error(stdscr, f"Error saving results: {str(e)}")

    def show_success(self, stdscr, output_path, stats):
        """Show success message with statistics"""
        height, width = stdscr.getmaxyx()

        while True:
            stdscr.clear()

            # Success header
            stdscr.addstr(height//2 - 6, 2, "✅ Scan Complete!", curses.color_pair(3) | curses.A_BOLD)

            # Statistics
            stdscr.addstr(height//2 - 4, 2, f"📊 Results:")
            stdscr.addstr(height//2 - 3, 4, f"Files scanned: {stats.get('files_scanned', 0)}")
            stdscr.addstr(height//2 - 2, 4, f"Files skipped: {stats.get('files_skipped', 0)}")
            stdscr.addstr(height//2 - 1, 4, f"Total files: {stats.get('total_paths', 0)}")

            # Output location
            stdscr.addstr(height//2 + 1, 2, f"💾 Saved to:")
            # Truncate path if too long
            display_path = str(output_path)
            if len(display_path) > width - 6:
                display_path = "..." + display_path[-(width-9):]
            stdscr.addstr(height//2 + 2, 4, display_path, curses.color_pair(6))

            # File size info
            try:
                file_size = Path(output_path).stat().st_size
                if file_size < 1024:
                    size_str = f"{file_size} bytes"
                elif file_size < 1024 * 1024:
                    size_str = f"{file_size/1024:.1f} KB"
                else:
                    size_str = f"{file_size/(1024*1024):.1f} MB"
                stdscr.addstr(height//2 + 3, 4, f"File size: {size_str}")
            except:
                pass

            stdscr.addstr(height - 2, 2, "Press any key to continue...", curses.color_pair(1))
            stdscr.refresh()

            if stdscr.getch():
                break

    def show_error(self, stdscr, error_message):
        """Show error message"""
        height, width = stdscr.getmaxyx()

        while True:
            stdscr.clear()

            stdscr.addstr(height//2 - 2, 2, "❌ Error", curses.color_pair(4) | curses.A_BOLD)

            # Word wrap error message
            words = error_message.split()
            lines = []
            current_line = ""
            max_width = width - 6

            for word in words:
                if len(current_line + word) < max_width:
                    current_line += word + " "
                else:
                    if current_line:
                        lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())

            for i, line in enumerate(lines):
                if height//2 + i < height - 3:
                    stdscr.addstr(height//2 + i, 4, line, curses.color_pair(4))

            stdscr.addstr(height - 2, 2, "Press any key to continue...", curses.color_pair(1))
            stdscr.refresh()

            if stdscr.getch():
                break
