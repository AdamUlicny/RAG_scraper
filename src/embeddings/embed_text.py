# src/embeddings/embed_text.py

from langchain.embeddings import OllamaEmbeddings

def embed_text_chunks(chunks):
    """
    Embeds each text chunk using LangChain's Ollama integration.
    
    Parameters:
    chunks (list of str): List of text chunks to embed.
    
    Returns:
    list of list of float: A list of embedding vectors for each chunk.
    """
    # Initialize the Ollama embeddings
    embedding_model = OllamaEmbeddings(model="nomic-embed-text")  # Specify the model name

    # Generate embeddings for each chunk
    embeddings = embedding_model.embed_documents(chunks)
    
    return embeddings

if __name__ == "__main__":
    # Example text chunks; replace with actual text chunks to embed
    text_chunks = ["This is the first chunk.", "Here is the second chunk."]
    embeddings = embed_text_chunks(text_chunks)
    print("Generated embeddings:", embeddings)
