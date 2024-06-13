# Import necessary libraries and modules
import sqlite3
import os
import shutil
import fitz  # PyMuPDF
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents.base import Document
from get_embedding_function import get_embedding_function
from constants import DB_PATH, CHROMA_PATH

# Function to update the Chroma database
def update_chroma(project_id):
    documents = load_documents(project_id)  # Load documents from the database
    chunks = split_documents(documents)     # Split the documents into chunks
    add_to_chroma(chunks)                   # Add the chunks to the Chroma database

# Function to load documents from the SQLite database
def load_documents(project_id):
    conn = sqlite3.connect(DB_PATH)  # Connect to the SQLite database
    cursor = conn.cursor()
    
    # Select the name and data (PDF content) of documents for the given project ID
    cursor.execute('SELECT name, data FROM documents WHERE project_id=?', (project_id, ))
    rows = cursor.fetchall()
    
    documents = []
    for row in rows:
        name, content = row
        try:
            # Extract text from the PDF content
            content_str = extract_text_from_pdf(content)
        except Exception as e:
            # Print an error message if text extraction fails
            print(f"Error extracting text from PDF for document {name}: {e}")
            continue
        
        # Create a Document object with the extracted text and metadata
        document = Document(page_content=content_str, metadata={"source": name})
        documents.append(document)
    
    conn.close()  # Close the database connection
    return documents

# Function to extract text from a PDF blob
def extract_text_from_pdf(pdf_blob):
    pdf_document = fitz.open(stream=pdf_blob, filetype="pdf")  # Open the PDF from the blob
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)  # Load each page of the PDF
        text += page.get_text()                  # Extract text from the page
    return text

# Function to split documents into smaller chunks
def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,          # Define the chunk size
        chunk_overlap=80,        # Define the overlap between chunks
        length_function=len,     # Use the length of the text to determine chunk size
        is_separator_regex=False
    )
    return text_splitter.split_documents(documents)  # Split the documents and return chunks

# Function to add document chunks to the Chroma database
def add_to_chroma(chunks: list[Document]):
    db = Chroma(
        persist_directory=CHROMA_PATH,  # Define the directory to persist the database
        embedding_function=get_embedding_function()  # Use a function to get embeddings
    )

    chunks_with_ids = calculate_chunk_ids(chunks)  # Calculate unique IDs for each chunk

    existing_items = db.get(include=[])  # Get existing items from the Chroma database
    existing_ids = set(existing_items["ids"])  # Extract existing IDs
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)  # Add new chunks that are not already in the database

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)  # Add new chunks to the database
        db.persist()  # Persist the changes
    else:
        print("✅ No new documents to add")

    db.delete_collection()  # Close the Chroma database connection

# Function to calculate unique IDs for each chunk
def calculate_chunk_ids(chunks):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page", 1)  # Default to page 1 if not available
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        chunk.metadata["id"] = chunk_id

    return chunks

# Function to clear the Chroma database
def clear_database():
    try:
        if os.path.exists(CHROMA_PATH):
            # Remove the Chroma database directory
            # shutil.rmtree(CHROMA_PATH)
            print("Database cleared successfully.")
        else:
            print("Database path does not exist.")
    except PermissionError as e:
        # Handle permission error if the directory cannot be removed
        print(f"PermissionError: {e}. Ensure no processes are using the database.")
    except Exception as e:
        # Handle any other exceptions that occur while clearing the database
        print(f"An error occurred while clearing the database: {e}")