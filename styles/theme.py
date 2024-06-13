from contextlib import contextmanager
from pages.menu import menu
from nicegui import app, ui

@contextmanager
def frame(navigation_title: str):
    """Custom page frame to share the same styling and behavior across all pages"""
    ui.colors(primary='#6E93D6', secondary='#53B689', accent='#111B1E', positive='#53B689')
    # Set primary, secondary, accent, and positive colors for the UI

    with ui.header():
        # Create a header section for the UI
        ui.label('AI-System for reporting').classes('font-bold')
        # Add a label with the text 'AI-System for reporting' and apply a bold font class
        ui.space()
        # Add space for layout purposes
        ui.label(navigation_title)
        # Add a label with the navigation title passed as an argument to the frame function
        ui.space()
        # Add another space for layout purposes

        with ui.row():
            # Create a row for horizontal layout of UI elements
            ui.label(f'Current user: {app.storage.user["name"]}').style('font-weight: 600')
            # Add a label displaying the current user's name with a font weight of 600 (bold)
            ui.button(on_click=lambda: (app.storage.user.clear(), ui.navigate.to('/login')), icon='logout', color='red').props("size=8px")
            # Add a button with a logout icon, red color, and size property set to 8px. The button clears the user storage and navigates to the login page on click

        with ui.row():
            # Create another row for additional menu items
            menu()
            # Call the menu function to add menu items to the row

    with ui.column().classes('absolute-center items-center'):
        # Create a column for vertical layout of UI elements, centered both vertically and horizontally
        yield
        # Yield control back to the caller, allowing for additional content to be added within this context
