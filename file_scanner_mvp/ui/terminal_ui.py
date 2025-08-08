import curses
from pathlib import Path
from core.directory_navigator import DirectoryNavigator
from core.file_scanner import FileScanner
from core.content_processor import ContentProcessor
from output_handlers.txt_handler import TXTHandler
from output_handlers.json_handler import JSONHandler
from output_handlers.csv_handler import CSVHandler
from config.settings import settings

class TerminalUI:
    def __init__(self):
        self.navigator = DirectoryNavigator()
        self.handlers = {
            "txt": TXTHandler(),
            "json": JSONHandler(),
            "csv": CSVHandler()
        }

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

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            # Draw header with hidden files status
            header = " File Scanner "
            status = " [SELECTED]" if self.navigator.confirmed_path else ""
            hidden_status = " [SHOW HIDDEN]" if self.navigator.show_hidden else " [HIDE HIDDEN]"

            path_str = f" Path: {self.navigator.current_path}{status}{hidden_status}"
            max_path_len = width - len(header) - 3
            if len(path_str) > max_path_len:
                path_str = path_str[:max_path_len] + "..."

            stdscr.addstr(0, 0, header, curses.color_pair(1))
            stdscr.addstr(0, len(header), path_str.ljust(width - len(header)), curses.color_pair(1))

            # Draw item count info
            count_info = self.navigator.get_item_count_info()
            info_text = f" Items: {count_info['visible']}/{count_info['total']}"
            if count_info['hidden'] > 0:
                info_text += f" ({count_info['hidden']} hidden)"

            stdscr.addstr(1, 0, info_text, curses.color_pair(6))

            # Draw file list
            items = self.navigator.list_items()
            list_start_y = 3  # Start after header and info line

            for idx, item in enumerate(items):
                y = idx + list_start_y
                if y >= height - 2:
                    break

                max_item_len = width - 6
                display_item = item[:max_item_len] + ".." if len(item) > max_item_len else item

                # Determine color based on selection and if item is hidden
                if idx == self.navigator.selected:
                    attr = curses.color_pair(3)  # Selected (green)
                elif item.startswith('.'):
                    attr = curses.color_pair(5)  # Hidden (yellow)
                else:
                    attr = curses.color_pair(2)  # Normal (white)

                # Add indicator for hidden items
                indicator = "." if item.startswith('.') else " "
                prefix = f"{'>' if idx == self.navigator.selected else ' '}{indicator}"

                stdscr.addstr(y, 0, f"{prefix} {display_item}".ljust(width-1), attr)

            # Draw footer with updated keybindings
            footer_lines = [
                "↑↓: Navigate | →: Enter | ←: Up | s: Confirm | h: Toggle Hidden | q: Quit",
                f"Hidden Files: {'ON' if self.navigator.show_hidden else 'OFF'} | Current: {'Hidden' if self.navigator.is_current_item_hidden() else 'Visible'}"
            ]

            for i, footer_line in enumerate(footer_lines):
                footer_y = height - len(footer_lines) + i
                stdscr.addstr(footer_y, 0, footer_line[:width], curses.color_pair(1))

            # Handle input
            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key in (curses.KEY_RIGHT, 10, 13):
                self.navigator.enter()
            elif key == curses.KEY_LEFT:
                self.navigator.go_up()
            elif key == curses.KEY_UP:
                self.navigator.select_prev()
            elif key == curses.KEY_DOWN:
                self.navigator.select_next()
            elif key == ord('h'):  # Toggle hidden files
                self.navigator.toggle_hidden_visibility()
            elif key == ord('s'):
                confirmed_path = self.navigator.confirm_directory()
                if confirmed_path:
                    self.show_scan_options(stdscr, confirmed_path)

    def show_scan_options(self, stdscr, scan_path):
        """Show scanning options including hidden files preference"""
        height, width = stdscr.getmaxyx()

        # Ask if user wants to include hidden files in scan
        include_hidden = False
        while True:
            stdscr.clear()
            stdscr.addstr(height//2 - 2, 2, "Scan Options:")
            stdscr.addstr(height//2 - 1, 2, f"Directory: {scan_path}")
            stdscr.addstr(height//2, 2, f"Include hidden files? {'YES' if include_hidden else 'NO'}")
            stdscr.addstr(height//2 + 1, 2, "y: Yes | n: No | ENTER: Continue")
            stdscr.refresh()

            key = stdscr.getch()
            if key == ord('y'):
                include_hidden = True
            elif key == ord('n'):
                include_hidden = False
            elif key in (10, 13):  # ENTER
                break

        self.show_output_prompt(stdscr, scan_path, include_hidden)

    def show_output_prompt(self, stdscr, scan_path, include_hidden):
        """Prompt for output filename, format, and save location"""
        stdscr.nodelay(0)
        height, width = stdscr.getmaxyx()

        # Prompt for filename
        while True:
            stdscr.clear()
            stdscr.addstr(height//2 - 2, 2, f"Scan will {'include' if include_hidden else 'exclude'} hidden files")
            stdscr.addstr(height//2 - 1, 2, "Output filename: ")
            stdscr.refresh()
            curses.echo()
            filename = stdscr.getstr().decode('utf-8').strip()
            curses.noecho()

            if filename:
                break
            else:
                stdscr.addstr(height//2, 2, "Filename cannot be empty!", curses.color_pair(4))
                stdscr.getch()

        # Select format
        formats = ["txt", "json", "csv"]
        selected_format = 0
        while True:
            stdscr.clear()
            stdscr.addstr(height//2 - 1, 2, "Select format:")
            for i, fmt in enumerate(formats):
                attr = curses.color_pair(3) if i == selected_format else curses.color_pair(2)
                stdscr.addstr(height//2 + i, 4, fmt, attr)
            stdscr.refresh()

            key = stdscr.getch()
            if key == curses.KEY_UP:
                selected_format = (selected_format - 1) % len(formats)
            elif key == curses.KEY_DOWN:
                selected_format = (selected_format + 1) % len(formats)
            elif key in (10, 13):
                break

        # Choose save directory (reuse existing logic)
        save_navigator = DirectoryNavigator(start_path=str(Path.home()))
        confirmed_save_path = None

        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, f"Save Location: {save_navigator.current_path}", curses.color_pair(1))
            stdscr.addstr(1, 0, "↑↓: Navigate | →: Enter dir | ←: Up | c: Confirm | q: Cancel", curses.color_pair(4))

            items = save_navigator.list_items()
            for idx, item in enumerate(items):
                y = idx + 2
                if y >= height - 2:
                    break
                attr = curses.color_pair(3) if idx == save_navigator.selected else curses.color_pair(2)
                stdscr.addstr(y, 0, f"{'>' if idx == save_navigator.selected else ' '} {item.ljust(width-2)}", attr)

            stdscr.refresh()

            key = stdscr.getch()
            if key == ord('q'):
                break
            elif key == ord('c'):
                confirmed_save_path = save_navigator.current_path
                break
            elif key == curses.KEY_RIGHT or key in (10, 13):
                if items:
                    selected_item = items[save_navigator.selected]
                    selected_path = save_navigator.current_path / selected_item
                    if selected_path.is_dir():
                        save_navigator.enter()
            elif key == curses.KEY_LEFT:
                save_navigator.go_up()
            elif key == curses.KEY_UP:
                save_navigator.select_prev()
            elif key == curses.KEY_DOWN:
                save_navigator.select_next()

        if confirmed_save_path:
            output_path = confirmed_save_path / f"{filename}.{formats[selected_format]}"

            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w'):
                    pass
            except IOError:
                stdscr.addstr(height//2, 2, f"No write permission: {confirmed_save_path}", curses.color_pair(4))
                stdscr.getch()
                return

            self.perform_scan(scan_path, output_path, formats[selected_format], include_hidden, stdscr)

    def perform_scan(self, scan_path, output_path, fmt, include_hidden, stdscr):
        """Perform scanning and generate output file"""
        scanner = FileScanner()
        processor = ContentProcessor()

        height, width = stdscr.getmaxyx()
        progress_win = curses.newwin(5, width, height//2 - 2, 0)

        def update_progress(current, total, scanned, skipped):
            progress_win.clear()
            if total > 0:
                progress = int((current / total) * (width - 4))
                progress_win.addstr(0, 0, f"Scanning: [{'#' * progress}{' ' * (width - 4 - progress)}]")
                progress_win.addstr(1, 0, f"Progress: {current}/{total} items processed")
                progress_win.addstr(2, 0, f"Files scanned: {scanned}")
                progress_win.addstr(3, 0, f"Files skipped: {skipped}")
                progress_win.addstr(4, 0, f"Hidden files: {'included' if include_hidden else 'excluded'}")
            progress_win.refresh()

        scanner.set_progress_callback(update_progress)
        scan_result = scanner.scan_directory(scan_path, include_hidden=include_hidden)

        # Process the data (files are now in scan_result['files'])
        processed_data = processor.process(scan_result['files'])
        self.handlers[fmt].write(processed_data, output_path)

        progress_win.clear()
        progress_win.addstr(0, 0, f"Scan complete!")
        progress_win.addstr(1, 0, f"Files scanned: {scan_result['stats']['files_scanned']}")
        progress_win.addstr(2, 0, f"Files skipped: {scan_result['stats']['files_skipped']}")
        progress_win.addstr(3, 0, f"Hidden files: {'included' if include_hidden else 'excluded'}")
        progress_win.addstr(4, 0, f"Saved to: {output_path}")
        progress_win.refresh()
        progress_win.getch()
