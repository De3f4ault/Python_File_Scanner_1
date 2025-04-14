from pathlib import Path

class DirectoryNavigator:
    def __init__(self, start_path="."):
        self.current_path = Path(start_path).resolve()
        self.selected = 0
        self.confirmed_path = None  # Track confirmed directory

    def list_items(self):
        """Return list of directories and files (directories first)"""
        try:
            items = sorted(Path(self.current_path).iterdir(), key=lambda x: (not x.is_dir(), x.name))
            return [item.name for item in items]
        except PermissionError:
            return []

    def confirm_directory(self):
        """Confirm current directory as target for scanning"""
        self.confirmed_path = self.current_path
        return self.confirmed_path

    def enter(self):
        """Handle directory entry"""
        items = self.list_items()
        if not items:
            return

        selected_item = items[self.selected]
        selected_path = self.current_path / selected_item

        if selected_path.is_dir():
            self.current_path = selected_path
            self.selected = 0  # Reset selection

    def go_up(self):
        """Navigate to parent directory"""
        parent = self.current_path.parent
        if parent != self.current_path:
            self.current_path = parent
            self.selected = 0  # Reset selection

    def select_next(self):
        """Move selection down"""
        items = self.list_items()
        if items:
            self.selected = (self.selected + 1) % len(items)

    def select_prev(self):
        """Move selection up"""
        items = self.list_items()
        if items:
            self.selected = (self.selected - 1) % len(items)
