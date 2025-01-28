import uuid

import chromadb


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
            embeddings=embeddings_data["embeddings"],
            documents=embeddings_data["chunks"],
            metadatas=[{"source": source_text} for _ in embeddings_data["chunks"]],
            ids=[f"{id_}-{i}" for i in range(len(embeddings_data["chunks"]))],
        )

    def add_unique_embeddings(self, embeddings_data: dict, source_text: str):
        """
        Add embeddings to ChromaDB if they are unique
        """
        embeddings = embeddings_data["embeddings"]
        documents = embeddings_data["chunks"]
        metadatas = [{"source": source_text} for _ in embeddings_data["chunks"]]
        ids = [f"{uuid.uuid1()}-{i}" for i in range(len(embeddings_data["chunks"]))]

        # Check if embeddings are unique
        unique_embeddings = []
        unique_documents = []
        unique_metadatas = []
        unique_ids = []
        for i, (embedding, document, metadata, id_) in enumerate(
            zip(embeddings, documents, metadatas, ids)
        ):
            distance_to_chunk_in_collection = self.collection.query(
                query_texts=[document], n_results=1
            )["distances"][0]
            if (
                not distance_to_chunk_in_collection
                or distance_to_chunk_in_collection[0] > 1e-3
            ):
                unique_embeddings.append(embedding)
                unique_documents.append(document)
                unique_metadatas.append(metadata)
                unique_ids.append(id_)

        # Add unique embeddings to collection
        self.collection.add(
            embeddings=unique_embeddings,
            documents=unique_documents,
            metadatas=unique_metadatas,
            ids=unique_ids,
        )

    def search(self, query: str, n_results: int = 10):
        """
        Search for relevant context using the query
        """
        results = self.collection.query(query_texts=[query], n_results=n_results)

        print(results["metadatas"])

        sources = [d.get("source", "") for d in results["metadatas"][0]]

        return results["documents"][0], sources
