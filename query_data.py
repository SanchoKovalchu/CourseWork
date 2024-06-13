# Import necessary libraries and modules
import argparse
from langchain.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama

from get_embedding_function import get_embedding_function

# Constants for Chroma database path and prompt template
CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

# Function to perform retrieval-augmented generation (RAG) query
def query_rag(query_text: str):
    # Prepare the Chroma database
    embedding_function = get_embedding_function()  # Get the embedding function
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)  # Initialize Chroma database

    # Search the database for similar documents
    results = db.similarity_search_with_score(query_text, k=5)  # Perform similarity search
    print(results)  # Print the search results

    # Create context text from search results
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])  # Concatenate page content
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)  # Create prompt template
    prompt = prompt_template.format(context=context_text, question=query_text)  # Format the prompt with context and question

    # Initialize the language model and generate response
    model = Ollama(model="mistral")  # Initialize the Ollama model
    response_text = model.invoke(prompt)  # Invoke the model with the prompt

    # Return the response text
    return response_text
