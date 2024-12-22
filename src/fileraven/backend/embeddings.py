from sentence_transformers import SentenceTransformer
import textwrap

def create_embeddings(text: str):
    """
    Create embeddings from text using sentence-transformers
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Split text into chunks
    chunks = textwrap.wrap(text, width=512, break_long_words=False, break_on_hyphens=False)
    
    # Create embeddings
    embeddings = model.encode(chunks)
    
    return {
        'chunks': chunks,
        'embeddings': embeddings
    }