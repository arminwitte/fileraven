from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn

from fileraven.backend.document_processor import process_document
from fileraven.backend.embeddings import Embedder
from fileraven.backend.vector_store import VectorStore
from fileraven.backend.rag_engine import RAGEngine

app = FastAPI(
    title="FileRaven API",
    description="API for the FileRaven document Q&A system",
    version="0.1.0"
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

class Query(BaseModel):
    question: str

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    content = await file.read()
    markdown_text = process_document(content, file.filename)
    
    embeddings = embedder.get_embeddings(markdown_text)
    vector_store.add_embeddings(embeddings, markdown_text)
    
    return {"message": "Document processed successfully"}

@app.post("/query")
async def query(query: Query):
    """Query the document database"""
    context = vector_store.search(query.question)
    response = rag_engine.generate_response(query.question, context)
    
    return {"response": response}

def main():
    """Run the FastAPI application"""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()