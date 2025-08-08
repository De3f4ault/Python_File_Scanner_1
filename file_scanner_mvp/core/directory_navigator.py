from pathlib import Path
from config.settings import settings

class DirectoryNavigator:
    def __init__(self, start_path="."):
        self.current_path = Path(start_path).resolve()
        self.selected = 0
        self.confirmed_path = None
        self.show_hidden = settings.show_hidden_files and settings.show_hidden_directories

    def toggle_hidden_visibility(self):
        """Toggle visibility of hidden files and directories"""
        self.show_hidden = not self.show_hidden
        # Reset selection when toggling to avoid index errors
        self.selected = 0

    def list_items(self):
        """Return list of directories and files (directories first), respecting hidden file settings"""
        try:
            all_items = []
            for item in Path(self.current_path).iterdir():
                # Apply filtering based on settings
                if self.show_hidden:
                    # Show all items when explicitly enabled
                    all_items.append(item)
                else:
                    # Use settings to filter items
                    if settings.should_show_item(item):
                        all_items.append(item)

            # Sort: directories first, then files, both alphabetically
            sorted_items = sorted(all_items, key=lambda x: (not x.is_dir(), x.name.lower()))
            return [item.name for item in sorted_items]
        except PermissionError:
            return []

    def get_current_item_path(self):
        """Get the full path of the currently selected item"""
        items = self.list_items()
        if items and 0 <= self.selected < len(items):
            return self.current_path / items[self.selected]
        return None

    def is_current_item_hidden(self):
        """Check if the currently selected item is hidden"""
        current_item_path = self.get_current_item_path()
        if current_item_path:
            return current_item_path.name.startswith('.')
        return False

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
            self.selected = 0

    def go_up(self):
        """Navigate to parent directory"""
        parent = self.current_path.parent
        if parent != self.current_path:
            self.current_path = parent
            self.selected = 0

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

    def get_item_count_info(self):
        """Get information about visible vs total items"""
        try:
            all_items = list(Path(self.current_path).iterdir())
            total_items = len(all_items)
            visible_items = len(self.list_items())
            hidden_items = total_items - visible_items

            return {
                'total': total_items,
                'visible': visible_items,
                'hidden': hidden_items
            }
        except PermissionError:
            return {'total': 0, 'visible': 0, 'hidden': 0}
