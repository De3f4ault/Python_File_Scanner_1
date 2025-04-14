import curses
from ui.terminal_ui import TerminalUI

def main():
    try:
        ui = TerminalUI()
        curses.wrapper(ui.draw)
    except Exception as e:
        # Ensure curses exits cleanly
        curses.endwin()
        print(f"Error: {str(e)}")
        raise  # Re-raise after cleanup

if __name__ == "__main__":
    main()
