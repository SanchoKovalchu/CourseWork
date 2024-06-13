# Import necessary modules and classes
import platform
from pathlib import Path
from typing import Optional

from nicegui import events, ui

# Define a class for a local file picker dialog
class local_file_picker(ui.dialog):

    def __init__(self, directory: str, *,
                 upper_limit: Optional[str] = ..., multiple: bool = False, show_hidden_files: bool = False) -> None:
        """
        Initialize the Local File Picker dialog.

        :param directory: The directory to start in.
        :param upper_limit: The directory to stop at (None: no limit, default: same as the starting directory).
        :param multiple: Whether to allow multiple files to be selected.
        :param show_hidden_files: Whether to show hidden files.
        """
        super().__init__()  # Call the parent class (ui.dialog) initializer

        # Set the initial path and upper limit for the file picker
        self.path = Path(directory).expanduser()
        if upper_limit is None:
            self.upper_limit = None
        else:
            self.upper_limit = Path(directory if upper_limit == ... else upper_limit).expanduser()
        self.show_hidden_files = show_hidden_files

        # Create the file picker UI
        with self, ui.card():
            self.add_drives_toggle()  # Add a toggle for drive selection (Windows only)
            # Create a grid to display files and directories
            self.grid = ui.aggrid({
                'columnDefs': [{'field': 'name', 'headerName': 'File'}],
                'rowSelection': 'multiple' if multiple else 'single',
            }, html_columns=[0]).classes('w-96').on('cellDoubleClicked', self.handle_double_click)
            # Add Cancel and Ok buttons
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=self.close).props('outline')
                ui.button('Ok', on_click=self._handle_ok)
        self.update_grid()  # Populate the grid with files and directories

    def add_drives_toggle(self):
        # Add a drive selection toggle if running on Windows
        if platform.system() == 'Windows':
            import win32api
            drives = win32api.GetLogicalDriveStrings().split('\000')[:-1]  # Get available drives
            self.drives_toggle = ui.toggle(drives, value=drives[0], on_change=self.update_drive)

    def update_drive(self):
        # Update the current path based on the selected drive and refresh the grid
        self.path = Path(self.drives_toggle.value).expanduser()
        self.update_grid()

    def update_grid(self) -> None:
        # Get the list of files and directories in the current path
        paths = list(self.path.glob('*'))
        if not self.show_hidden_files:
            paths = [p for p in paths if not p.name.startswith('.')]  # Filter out hidden files
        paths.sort(key=lambda p: p.name.lower())  # Sort alphabetically
        paths.sort(key=lambda p: not p.is_dir())  # Sort directories before files

        # Update the grid with the files and directories
        self.grid.options['rowData'] = [
            {
                'name': f'📁 <strong>{p.name}</strong>' if p.is_dir() else p.name,  # Display directories with a folder icon
                'path': str(p),
            }
            for p in paths
        ]
        # Add a parent directory entry if not at the upper limit or root directory
        if self.upper_limit is None and self.path != self.path.parent or \
                self.upper_limit is not None and self.path != self.upper_limit:
            self.grid.options['rowData'].insert(0, {
                'name': '📁 <strong>..</strong>',
                'path': str(self.path.parent),
            })
        self.grid.update()  # Refresh the grid display

    def handle_double_click(self, e: events.GenericEventArguments) -> None:
        # Handle double-click events on grid items
        self.path = Path(e.args['data']['path'])  # Update the path to the selected item
        if self.path.is_dir():
            self.update_grid()  # If a directory, update the grid to show its contents
        else:
            self.submit([str(self.path)])  # If a file, submit the selected path

    async def _handle_ok(self):
        # Handle the Ok button click event
        rows = await ui.run_javascript(f'getElement({self.grid.id}).gridOptions.api.getSelectedRows()')  # Get selected rows from the grid
        self.submit([r['path'] for r in rows])  # Submit the selected file paths
