# src/embeddings/embed_text.py

from sentence_transformers import SentenceTransformer

def embed_text_chunks(chunks, model_name="all-MiniLM-L6-v2"):
    """
    Embeds each text chunk using a local embedding model.
    
    Parameters:
    chunks (list of str): List of text chunks to embed.
    model_name (str): Name of the sentence-transformers model to use.
    
    Returns:
    list of list of float: A list of embedding vectors for each chunk.
    """
    # Load the embedding model
    model = SentenceTransformer(model_name)
    
    # Generate embeddings for each chunk
    embeddings = model.encode(chunks, show_progress_bar=True)
    
    return embeddings
