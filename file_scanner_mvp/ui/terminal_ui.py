import curses
from pathlib import Path
from core.directory_navigator import DirectoryNavigator
from core.file_scanner import FileScanner
from core.content_processor import ContentProcessor
from output_handlers.txt_handler import TXTHandler
from output_handlers.json_handler import JSONHandler
from output_handlers.csv_handler import CSVHandler

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
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(0)   # Wait for user input
        stdscr.timeout(100)  # Refresh rate
        stdscr.clear()

        # Initialize color pairs
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Header/Footer
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Normal text
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Selected item
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # Error messages

        while True:
            stdscr.clear()
            height, width = stdscr.getmaxyx()

            # Draw header
            header = " File Scanner "
            status = " [SELECTED]" if self.navigator.confirmed_path else ""
            path_str = f" Path: {self.navigator.current_path}{status}"
            max_path_len = width - len(header) - 3
            if len(path_str) > max_path_len:
                path_str = path_str[:max_path_len] + "..."

            stdscr.addstr(0, 0, header, curses.color_pair(1))
            stdscr.addstr(0, len(header), path_str.ljust(width - len(header)), curses.color_pair(1))

            # Draw file list
            items = self.navigator.list_items()
            for idx, item in enumerate(items):
                y = idx + 2
                if y >= height - 2:
                    break

                max_item_len = width - 4
                display_item = item[:max_item_len] + ".." if len(item) > max_item_len else item

                attr = curses.color_pair(3) if idx == self.navigator.selected else curses.color_pair(2)
                stdscr.addstr(y, 0, f"{'>' if idx == self.navigator.selected else ' '} {display_item.ljust(width-2)}", attr)

            # Draw footer
            footer = "↑↓: Navigate | →: Enter | ←: Up | s: Confirm | q: Quit"
            stdscr.addstr(height-1, 0, footer[:width], curses.color_pair(1))

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
            elif key == ord('s'):
                confirmed_path = self.navigator.confirm_directory()
                if confirmed_path:
                    self.show_output_prompt(stdscr, confirmed_path)

    def show_output_prompt(self, stdscr, scan_path):
        """Prompt for output filename, format, and save location"""
        stdscr.nodelay(0)
        height, width = stdscr.getmaxyx()

        # Prompt for filename
        while True:
            stdscr.addstr(height//2 - 2, 2, "Output filename: ")
            stdscr.refresh()
            curses.echo()
            filename = stdscr.getstr().decode('utf-8').strip()
            curses.noecho()

            if filename:
                break
            else:
                stdscr.addstr(height//2 - 1, 2, "Filename cannot be empty!", curses.color_pair(4))
                stdscr.getch()

        # Select format
        formats = ["txt", "json", "csv"]
        selected_format = 0
        while True:
            stdscr.clear()
            stdscr.addstr(height//2, 2, "Select format:")
            for i, fmt in enumerate(formats):
                attr = curses.color_pair(3) if i == selected_format else curses.color_pair(2)
                stdscr.addstr(height//2 + i + 1, 4, fmt, attr)
            stdscr.refresh()

            key = stdscr.getch()
            if key == curses.KEY_UP:
                selected_format = (selected_format - 1) % len(formats)
            elif key == curses.KEY_DOWN:
                selected_format = (selected_format + 1) % len(formats)
            elif key in (10, 13):
                break

        # Choose save directory
        save_navigator = DirectoryNavigator(start_path=str(Path.home()))
        confirmed_save_path = None

        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, f"Save Location: {save_navigator.current_path}",
                         curses.color_pair(1))
            stdscr.addstr(1, 0, "↑↓: Navigate | →: Enter dir | ←: Up | c: Confirm | q: Cancel",
                         curses.color_pair(4))  # Updated footer

            items = save_navigator.list_items()
            for idx, item in enumerate(items):
                y = idx + 2
                if y >= height - 2:
                    break
                attr = curses.color_pair(3) if idx == save_navigator.selected else curses.color_pair(2)
                stdscr.addstr(y, 0, f"{'>' if idx == save_navigator.selected else ' '} {item.ljust(width-2)}", attr)

            stdscr.refresh()

            key = stdscr.getch()
            if key == ord('q'):  # Cancel save operation
                break
            elif key == ord('c'):  # Confirm save location
                confirmed_save_path = save_navigator.current_path
                break
            elif key == curses.KEY_RIGHT or key in (10, 13):  # ENTER enters directories
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

            self.perform_scan(scan_path, output_path, formats[selected_format], stdscr)
            stdscr.addstr(height//2, 2, f"Saved to: {output_path}", curses.color_pair(3))
            stdscr.getch()

    def perform_scan(self, scan_path, output_path, fmt, stdscr):
        """Perform scanning and generate output file"""
        scanner = FileScanner()
        processor = ContentProcessor()

        height, width = stdscr.getmaxyx()
        progress_win = curses.newwin(3, width, height//2 - 1, 0)

        def update_progress(current, total):
            progress = int((current / total) * (width - 4)) if total > 0 else 0
            progress_win.addstr(0, 0, f"Scanning: [{'#' * progress}{' ' * (width - 4 - progress)}]")
            progress_win.addstr(1, 0, f"{current}/{total} files")
            progress_win.refresh()

        scanner.set_progress_callback(update_progress)
        data = scanner.scan_directory(scan_path)
        processed_data = processor.process(data)
        self.handlers[fmt].write(processed_data, output_path)
        progress_win.clear()
