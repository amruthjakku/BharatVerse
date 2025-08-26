# backend/services/vector_store.py

import os

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# --- FIX APPLIED HERE: Updated import path ---
from langchain_community.vectorstores.faiss import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

# --- FIX APPLIED HERE: Pass the API key directly ---
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001", google_api_key=GEMINI_API_KEY
)

vector_store = None


def initialize_vector_store():
    """Creates an empty FAISS vector store if one doesn't exist."""
    global vector_store
    if vector_store is None:
        dummy_doc = [Document(page_content="start")]
        vector_store = FAISS.from_documents(dummy_doc, embeddings)
        print("In-memory vector store initialized.")


def add_text_to_store(text: str, metadata: dict):
    """Splits text, creates documents, and adds them to the vector store."""
    global vector_store
    if vector_store is None:
        initialize_vector_store()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = [
        Document(page_content=chunk, metadata=metadata)
        for chunk in text_splitter.split_text(text)
    ]

    vector_store.add_documents(docs)
    print(
        f"Added {len(docs)} document chunks to the vector store for record: {metadata.get('record_id')}"
    )


def search_store(query: str) -> list[Document]:
    """Searches the vector store for documents similar to the query."""
    global vector_store
    if vector_store is None:
        return []

    return vector_store.similarity_search(query, k=3)
