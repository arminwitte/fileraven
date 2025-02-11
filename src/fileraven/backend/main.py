import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fileraven.backend.document_processor import process_document
from fileraven.backend.embeddings import Embedder
from fileraven.backend.file_clerk import FileClerk
from fileraven.backend.rag_engine import RAGEngine
from fileraven.backend.vector_store import VectorStore

app = FastAPI(
    title="FileRaven API",
    description="API for the FileRaven document Q&A system",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store = VectorStore()
rag_engine = RAGEngine()
embedder = Embedder()
file_clerk = FileClerk()


class Query(BaseModel):
    question: str


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""

    # store the uploaded file
    storage_file_path, _ = await file_clerk.store(file)
    await file.seek(0)
    # storage_file_path = ""

    # read file content and transform to markdown
    content = await file.read()
    markdown_text = process_document(content, file.filename)

    # compute embeddings and store in vector database
    embeddings = embedder.get_embeddings(markdown_text)
    vector_store.add_unique_embeddings(embeddings, storage_file_path)

    return {"message": "Document processed successfully"}


@app.post("/query")
async def query(query: Query):
    """Query the document database"""
    context, sources = vector_store.search(query.question)

    print(context)
    context_str = "\n----------\n".join(context)
    # sources_str = ", ".join(set(sources))

    response = rag_engine.generate_response(query.question, context_str)

    return {"response": response, "sources": sources}


def main():
    """Run the FastAPI application"""
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
