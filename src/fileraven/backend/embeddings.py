from sentence_transformers import SentenceTransformer
import re
from typing import Dict, List
import torch

class Embedder:
    """
    A class to transform markdown text into vector embeddings while preserving
    original markdown formatting for LLM context.
    
    Attributes:
        chunk_size (int): Maximum number of tokens per chunk
        chunk_overlap_size (int): Number of overlapping tokens between chunks
        model_name (str): Name of the embedding model to use
    """
    
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap_size: int = 64,
        model_name: str = "all-MiniLM-L6-v2" # "paraphrase-multilingual-mpnet-base-v2"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap_size = chunk_overlap_size
        self.model = SentenceTransformer(model_name)

    def _minimal_cleaning(self, text: str) -> str:
        """
        Minimal cleaning of text while preserving markdown structure.
        Only removes excessive whitespace.
        
        Args:
            text (str): Input markdown text
            
        Returns:
            str: Cleaned text with markdown preserved
        """
        # Replace multiple newlines with double newline
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Remove excessive spaces while preserving markdown indentation
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
    
    def get_embeddings(self, text: str) -> Dict[str, torch.Tensor]:
        """
        Transform markdown text into vector embeddings and return original chunks.
        
        Args:
            text (str): Input markdown text
            
        Returns:
            Dict with:
                'chunks': List[str] - Original text chunks
                'embeddings': torch.Tensor - Embeddings tensor
        """
        # Minimal cleaning while preserving markdown
        cleaned_text = self._minimal_cleaning(text)
        
        # Get initial tokens
        tokens = self.model.tokenizer.encode(cleaned_text)
        chunk_embeddings = []
        text_chunks = []
        
        # Process in overlapping chunks
        start_idx = 0
        while start_idx < len(tokens):
            # Get chunk of tokens
            end_idx = min(start_idx + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start_idx:end_idx]
            
            # Get the original text for this chunk by decoding these specific tokens
            chunk_text = self.model.tokenizer.decode(chunk_tokens)
            text_chunks.append(chunk_text)
            
            # Get embedding
            embedding = self.model.encode(chunk_text, convert_to_tensor=True)
            chunk_embeddings.append(embedding)
            
            # Move to next chunk with overlap
            start_idx += self.chunk_size - self.chunk_overlap_size
        
        embeddings = torch.stack(chunk_embeddings) if chunk_embeddings else torch.tensor([])
        
        return {
            'chunks': text_chunks,
            'embeddings': embeddings
        }
    
    def __call__(self, text: str) -> Dict[str, torch.Tensor]:
        """
        Allow the class to be called directly to generate embeddings.
        
        Args:
            text (str): Input markdown text
            
        Returns:
            Dict with:
                'chunks': List[str] - Original text chunks
                'embeddings': torch.Tensor - Embeddings tensor
        """
        return self.get_embeddings(text)