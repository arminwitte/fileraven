import chromadb
from chromadb.config import Settings
import numpy as np

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=".chroma")
        self.collection = self.client.get_or_create_collection("documents")
    
    def add_embeddings(self, embeddings_data: dict, source_text: str):
        """
        Add embeddings to ChromaDB
        """
        self.collection.add(
            embeddings=embeddings_data['embeddings'].tolist(),
            documents=embeddings_data['chunks'],
            metadatas=[{"source": source_text} for _ in embeddings_data['chunks']],
            ids=[f"id_{i}" for i in range(len(embeddings_data['chunks']))]
        )
    
    def search(self, query: str, n_results: int = 3):
        """
        Search for relevant context using the query
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        return " ".join(results['documents'][0])
