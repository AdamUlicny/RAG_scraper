# src/retrieval/retrieve_chunks.py

import chromadb
from chromadb.config import Settings
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

def initialize_chroma_collection(collection_name="document_chunks"):
    """
    Initializes a ChromaDB collection for storing embeddings.
    
    Parameters:
    collection_name (str): Name of the collection to initialize.
    
    Returns:
    Chroma: The LangChain Chroma wrapper instance.
    """
    # Configure Chroma to use local storage
    client_settings = Settings()
    client = chromadb.Client(client_settings)
    
    # Initialize the embedding model
    embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Initialize the Chroma collection
    collection = Chroma(collection_name=collection_name, embedding_function=embedding_function, client=client)
    
    return collection

def add_chunks_to_chroma(chunks, collection):
    """
    Adds text chunks to the ChromaDB collection using LangChain's Chroma wrapper.
    
    Parameters:
    chunks (list of str): List of text chunks.
    collection (Chroma): The Chroma collection instance.
    """
    # Adding text chunks directly to Chroma, where embeddings are handled internally
    collection.add_texts(texts=chunks)

def retrieve_similar_chunks(query_text, collection, top_k=3):
    """
    Retrieves the top K most similar chunks to a query using LangChain's Chroma wrapper.
    
    Parameters:
    query_text (str): The text query to embed and retrieve similar chunks for.
    collection (Chroma): The Chroma collection instance.
    top_k (int): Number of top similar chunks to retrieve.
    
    Returns:
    list of dict: List of dictionaries with "chunk" and "metadata" keys.
    """
    results = collection.similarity_search(query_text, k=top_k)
    
    return [{"chunk": result.page_content, "metadata": result.metadata} for result in results]
