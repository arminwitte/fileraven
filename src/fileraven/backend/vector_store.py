import chromadb
from chromadb.config import Settings
import numpy as np
import uuid

class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=".chroma")
        self.collection = self.client.get_or_create_collection("documents")
    
    def add_embeddings(self, embeddings_data: dict, source_text: str):
        """
        Add embeddings to ChromaDB
        """
        id_ = uuid.uuid1()
        self.collection.add(
            embeddings=embeddings_data['embeddings'],
            documents=embeddings_data['chunks'],
            metadatas=[{"source": source_text} for _ in embeddings_data['chunks']],
            ids=[f"{id_}-{i}" for i in range(len(embeddings_data['chunks']))]
        )
    
    def search(self, query: str, n_results: int = 10):
        """
        Search for relevant context using the query
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )

        print(results["metadatas"])
        
        sources = [d.get("source",'') for d in results['metadatas'][0]]

        return results['documents'][0], sources
