# Import custom styles and message functions
import styles.theme
from styles.message import message

# Import NiceGUI components for building user interfaces
from nicegui import APIRouter, ui, app

# Import the project page module and database functions
from pages import project_page
from db import get_projects, get_project_data

# NOTE: the APIRouter does not yet work with NiceGUI On Air
# (see https://github.com/zauberzeug/nicegui/discussions/2792)

# Create an API router with a prefix for project-related pages
router = APIRouter(prefix='/projects')

@router.page('/')
def example_page():
    # Define the main project list page

    # Get the list of projects for the current user from the database
    project_list = get_projects(app.storage.user["id"])

    # Create a styled frame for the page with a title
    with styles.theme.frame('- Project list -'):
        # Display a message indicating this is the project list
        message('Project list')
        
        # Add a label describing the page
        ui.label('This is list of available projects')

        # Iterate over the project list and create links for each project
        for project in project_list:
            project_id = project[0]
            # Get project data from the database using the project ID
            project_data = get_project_data(project_id)
            project_title = project_data[0]
            
            # Create a link for each project, leading to its detailed page
            ui.link(project_title, f'/projects/{project_id}').classes('text-xl text-grey-8')


@router.page('/{project_id}')
def project(project_id: str):
    # Define the project detail page

    # Create a styled frame for the project description page with a title
    with styles.theme.frame(f'- Project Description {project_id} -'):
        # Display the content of the project page using the project ID
        project_page.content(project_id)
        
        # Add a link to go back to the project list page
        ui.link('Go Back', router.prefix).classes('text-xl text-grey-8')
