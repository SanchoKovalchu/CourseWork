# ------------------- IMPORTS -------------------

from nicegui import ui
import sqlite3
import fitz  # PyMuPDF
from PIL import Image
import io
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from local_file_picker import local_file_picker
import os
from typing import Optional
from constants import DB_PATH, FILES_PATH
import base64

# Initialize the database with necessary tables
def initialize_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create reports table
    c.execute('''
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        data BLOB NOT NULL,
        project_id INTEGER NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )
    ''')

    # Create documents table
    c.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        data BLOB NOT NULL,
        project_id INTEGER NOT NULL,
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )
    ''')
    
    # Create users table
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Create projects table
    c.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        start_date DATE,
        end_date DATE,
        project_manager TEXT
    )
    ''')

    # Create user_projects bridge table
    c.execute('''
    CREATE TABLE IF NOT EXISTS user_projects (
        user_id INTEGER NOT NULL,
        project_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (project_id) REFERENCES projects(id),
        PRIMARY KEY (user_id, project_id)
    )
    ''')

    conn.commit()
    conn.close()

# Function to upload PDF files from a folder to the database
def upload_files_from_folder(folder_path, project_id):
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):  # Check if the file is a PDF
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'rb') as file:
                file_data = file.read()
                add_file(filename, file_data, project_id)

# Function to populate the database with sample data
def fill_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Insert sample users
    c.execute('''
    INSERT INTO users (name, username, password)
    VALUES (?, ?, ?)
    ''', ('Oleksandr', 'admin', 'admin'))
    c.execute('''
    INSERT INTO users (name, username, password)
    VALUES (?, ?, ?)
    ''', ('User', 'user', 'user'))
    
    # Insert sample projects
    c.execute('''
    INSERT INTO projects (title, start_date, end_date, project_manager)
    VALUES (?, ?, ?, ?)
    ''', ('TEST Project 1', '2022-01-01', '2023-01-01', 'Oleksandr Kovalchuk'))
    c.execute('''
    INSERT INTO projects (title, start_date, end_date, project_manager)
    VALUES (?, ?, ?, ?)
    ''', ('TEST Project 2', '2023-01-01', '2025-01-01', 'Oleksandr Kovalchuk'))
    
    # Assign users to projects
    c.execute('''
    INSERT INTO user_projects (user_id, project_id)
    VALUES (?, ?)
    ''', ('1', '1'))
    c.execute('''
    INSERT INTO user_projects (user_id, project_id)
    VALUES (?, ?)
    ''', ('1', '2'))
    
    conn.commit()
    upload_files_from_folder(FILES_PATH, 1)
    conn.close()

# Function to delete the database file
def delete_database_file():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("Database file deleted.")
    else:
        print("Database file not found.")

# Function to add a file to the database
def add_file(name, data, project_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    INSERT INTO documents (name, data, project_id)
    VALUES (?, ?, ?)
    ''', (name, data, project_id))
    print((name, project_id))
    conn.commit()
    conn.close()

# Function to add a report to the database
def add_report(name, data, project_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    INSERT INTO reports (name, data, project_id)
    VALUES (?, ?, ?)
    ''', (name, data, project_id))
    print((name, project_id))
    conn.commit()
    conn.close()

# Function to display a PDF file
def display_pdf(file_id, type):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if type == "document":
        c.execute('SELECT name, data FROM documents WHERE id=?', (file_id,))
    if type == "report":
        c.execute('SELECT name, data FROM reports WHERE id=?', (file_id,))
    row = c.fetchone()
    conn.close()

    if row is None:
        ui.notify("File not found!")
        return

    filename, file_data = row
    with open('temp.pdf', 'wb') as f:
        f.write(file_data)

    doc = fitz.open('temp.pdf')
    fig, ax = plt.subplots(figsize=(20, 12))
    plt.subplots_adjust(bottom=0.2)
    
    page_num = 0
    total_pages = doc.page_count

    def show_page(num):
        ax.clear()
        page = doc.load_page(num)
        pix = page.get_pixmap()
        img_data = pix.tobytes(output='png')
        img = Image.open(io.BytesIO(img_data))
        ax.imshow(img)
        ax.set_title(f"{filename} - Page {num + 1}/{total_pages}")
        ax.axis('off')
        plt.draw()

    def next_page(event):
        nonlocal page_num
        if page_num < total_pages - 1:
            page_num += 1
            show_page(page_num)

    def prev_page(event):
        nonlocal page_num
        if page_num > 0:
            page_num -= 1
            show_page(page_num)

    axprev = plt.axes([0.1, 0.05, 0.1, 0.075])
    axnext = plt.axes([0.8, 0.05, 0.1, 0.075])
    
    bnext = Button(axnext, 'Next')
    bprev = Button(axprev, 'Previous')
    
    bnext.on_clicked(next_page)
    bprev.on_clicked(prev_page)
    
    show_page(page_num)
    # Maximize the plt window
    manager = plt.get_current_fig_manager()
    manager.resize(*manager.window.maxsize())
    plt.show()

# Function to pick and upload files for a specific project
async def pick_file(project_id) -> None:
    file_path = await local_file_picker('~', multiple=True)
    print(project_id)
    if file_path:
        for file in file_path:
            with open(file, 'rb') as f:
                file_data = f.read()
            add_file(os.path.basename(file), file_data, project_id)
        ui.notify(f'You added {len(file_path)} files.')
        ui.navigate.reload()

# Function to get file data from the database by file ID
def get_file_data(file_id, type):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if type == "document":
        c.execute('SELECT name, data FROM documents WHERE id=?', (file_id,))
    if type == "report":
        c.execute('SELECT name, data FROM reports WHERE id=?', (file_id,))
    file = c.fetchone()
    conn.close()
    if file:
        filename, file_data = file
        return filename, file_data
    return None, None

# Function to view documents for a specific project
def view_documents(project_id):
    print(project_id)
    print('View')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name FROM documents WHERE project_id=?', (project_id, ))
    files = c.fetchall()
    conn.close()
    
    with ui.dialog() as dialog, ui.card():
        ui.label('Documents:')
        if files:
            for file in files:
                file_id, filename = file
                with ui.row():
                    # Button to view the PDF
                    ui.button(filename, on_click=lambda file_id=file_id: display_pdf(file_id, "document"))
                    # Button to download the file
                    ui.button('', on_click=lambda file_id=file_id: download_file(file_id, "document"), icon='download')
        ui.button('Close', on_click=dialog.close)
    dialog.open()

# Function to handle file download by file ID
def download_file(file_id, type):
    filename, file_data = get_file_data(file_id, type)
    if file_data:
        encoded_file_data = base64.b64encode(file_data).decode('utf-8')
        ui.download(f'data:application/octet-stream;base64,{encoded_file_data}', filename)

# Function to view reports for a specific project
def view_reports(project_id):
    print(project_id)
    print('View')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, name FROM reports WHERE project_id=?', (project_id,))
    files = c.fetchall()
    conn.close()
    
    with ui.dialog() as dialog, ui.card():
        ui.label('Reports:')
        if files:
            for file in files:
                file_id, filename = file
                with ui.row():
                    # Button to view the PDF
                    ui.button(filename, on_click=lambda file_id=file_id: display_pdf(file_id, "report"))
                    # Button to download the file
                    ui.button('', on_click=lambda file_id=file_id: download_file(file_id, "report"), icon='download')
        ui.button('Close', on_click=dialog.close)
    
    dialog.open()

# Function to get user ID based on username and password
def get_user_id(username: str, password: str) -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM users WHERE username=? AND password=?', (username, password))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

# Function to get current user data based on user ID
def get_current_user_data(user_id: str) -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT name FROM users WHERE id=?', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

# Function to get projects associated with a user ID
def get_projects(user_id: str) -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT project_id FROM user_projects WHERE user_id=?', (user_id,))
    row = c.fetchall()
    conn.close()
    if row:
        return row
    return None

# Function to get project data based on project ID
def get_project_data(project_id: str) -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT title, start_date, end_date, project_manager FROM projects WHERE id=?', (project_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return row
    return None

# Function to get documents associated with a project ID
def get_project_documents(project_id: str) -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id FROM documents WHERE project_id=?', (project_id,))
    row = c.fetchall()
    conn.close()
    if row:
        result = [item[0] for item in row]
        return result
    return []
