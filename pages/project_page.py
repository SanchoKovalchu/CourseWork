# Import the NiceGUI module for building user interfaces
from nicegui import ui

# Import the message function from the styles module for displaying styled messages
from styles.message import message

# Import database-related functions: pick_file, view_documents, view_reports, get_project_data, and get_project_documents
from db import pick_file, view_documents, view_reports, get_project_data, get_project_documents

# Import the generate_report function from the AI module for generating reports
from AI import generate_report

# Define the content function which takes a project_id as a string parameter and returns None
def content(project_id: str) -> None:
    # Get the project data from the database using the project_id
    project_data = get_project_data(project_id)
    
    # Get the documents related to the project from the database using the project_id
    project_documents = get_project_documents(project_id)
    
    # Count the number of documents related to the project
    documents_count = len(project_documents)
    
    # Extract the project title from the project data
    project_title = project_data[0]
    
    # Extract the project start date from the project data
    project_start_date = project_data[1]
    
    # Extract the project end date from the project data
    project_end_date = project_data[2]
    
    # Extract the project manager's name from the project data
    project_manager = project_data[3]

    # Display a message showing the project ID
    message(f'Project  #{project_id}')
    
    # Display a message indicating this is the project page and apply a bold font class
    message('This is the page for the project.').classes('font-bold')
    
    # Display a message showing the project title
    message(f'Title: {project_title}')
    
    # Display a message showing the project start date
    message(f'Start date: {project_start_date}')
    
    # Display a message showing the project end date
    message(f'End date: {project_end_date}')
    
    # Display a message showing the project manager's name
    message(f'Project Manager: {project_manager}')
    
    # Display a message showing the number of documents downloaded for the project
    message(f'Documents downloaded: {documents_count}')
    
    # Create a row for horizontally arranging the buttons
    with ui.row():
        # Add a button to "Add document", which calls pick_file with the project_id when clicked. The button has an 'add' icon, blue color, and size 20px
        ui.button(text='Add document', on_click=lambda: pick_file(project_id), icon='add', color='blue').props("size=20px")
        
        # Add a button to "View documents", which calls view_documents with the project_id when clicked. The button has a 'visibility' icon, blue color, and size 20px
        ui.button(text='View documents', on_click=lambda: view_documents(project_id), icon='visibility', color='blue').props("size=20px")
        
        # Add a button to "View reports", which calls view_reports with the project_id when clicked. The button has a 'flag' icon, blue color, and size 20px
        ui.button(text='View reports', on_click=lambda: view_reports(project_id), icon='flag', color='blue').props("size=20px")
        
        # Add a button to "Generate risk report", which calls generate_report with the project_id when clicked. The button has a 'description' icon, blue color, and size 20px
        ui.button(text='Generate risk report', on_click=lambda: generate_report(project_id), icon='description', color='blue').props("size=20px")
