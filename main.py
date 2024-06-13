# Import necessary modules and functions
import project_router
import authentication
import pages.home_page
import styles.theme
from fastapi.responses import RedirectResponse
from nicegui import app, ui
from typing import Optional
from db import initialize_db, fill_db, delete_database_file, get_user_id, get_current_user_data

# Define the login page
@ui.page('/login')
def login() -> Optional[RedirectResponse]:
    def try_login() -> None:
        # Function to attempt user login
        user_id = get_user_id(username.value, password.value)
        if user_id:
            # If user ID is found, update the app's storage with user details
            current_user = get_current_user_data(user_id)
            app.storage.user.update(
                {
                'id': user_id, 
                'name': current_user, 
                'username': username.value, 
                'authenticated': True
                })
            ui.navigate.to(app.storage.user.get('referrer_path', '/'))  # Navigate to the referrer path or home page
        else:
            # If login fails, show a notification
            ui.notify('Wrong username or password', color='negative')

    if app.storage.user.get('authenticated', False):
        # If the user is already authenticated, redirect to the home page
        return RedirectResponse('/')
    
    # Create the login form
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)  # Input for username
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)  # Input for password
        ui.button('Log in', on_click=try_login)  # Login button
    return None

# Define the home page
@ui.page('/')
def index_page() -> None:
    with styles.theme.frame('- Homepage -'):
        pages.home_page.content()  # Load the content for the home page

# Include the project router for modularized routes
app.include_router(project_router.router)
# Add authentication middleware to handle authentication on each request
app.add_middleware(authentication.AuthMiddleware)

# Initialize the database
delete_database_file()  # Delete the existing database file
initialize_db()  # Initialize the database with necessary tables
fill_db()  # Fill the database with initial data

# Run the NiceGUI application with a title and storage secret
ui.run(title='AI-System for reporting', storage_secret='THIS_NEEDS_TO_BE_CHANGED')