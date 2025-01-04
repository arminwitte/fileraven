from sentence_transformers import SentenceTransformer
import re
from typing import Dict, List, Tuple
import numpy as np

class Embedder:
    """
    A class to transform markdown text into vector embeddings while preserving
    original markdown formatting for LLM context. Uses recursive semantic splitting
    and progressive merging with overlap.
    
    Attributes:
        chunk_size (int): Maximum number of tokens per chunk
        overlap_size (int): Number of overlapping tokens between chunks
        model_name (str): Name of the embedding model to use
    """
    
    def __init__(
        self,
        chunk_size: int = 228,
        overlap_size: int = 32,
        model_name: str = "all-MiniLM-L6-v2"
    ):
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.model = SentenceTransformer(model_name)

    def _get_token_count(self, text: str) -> int:
        """Get the number of tokens in a text chunk."""
        return len(self.model.tokenizer.encode(text))

    def _emergency_split(self, text: str) -> List[str]:
        """
        Split text into chunks if no semantic split is possible and chunk is too large.
        Tries to split at sentence boundaries first, then hard splits at token limit.
        """
        chunks = []
        current_chunk = ""
        current_tokens = 0
        
        # Try to split at sentence boundaries first
        sentences = re.split(r'([.!?]\s+)', text)
        
        for sentence in sentences:
            sentence_tokens = self._get_token_count(sentence)
            
            if sentence_tokens > self.chunk_size:
                # If a single sentence is too large, split by tokens
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                    current_tokens = 0
                
                # Encode and decode to maintain subword token boundaries
                tokens = self.model.tokenizer.encode(sentence)
                start = 0
                while start < len(tokens):
                    end = start + self.chunk_size
                    chunk = self.model.tokenizer.decode(tokens[start:end])
                    chunks.append(chunk.strip())
                    start = end
            
            elif current_tokens + sentence_tokens > self.chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
                current_tokens = sentence_tokens
            
            else:
                current_chunk += sentence
                current_tokens += sentence_tokens
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    def _split_semantic(self, text: str) -> List[str]:
        """
        Split text into semantic chunks recursively using markdown structure.
        Returns the smallest possible semantic chunks.
        """
        if not text.strip():
            return []

        if self._get_token_count(text) <= self.chunk_size:
            return [text.strip()]

        # List of (pattern, is_separator) tuples
        # is_separator determines if the pattern itself should be a separate chunk
        split_patterns = [
            (r'(?=^#{1,6}\s)', False),  # Headers
            (r'(?:^|\n)```[\s\S]*?```', True),  # Code blocks
            (r'(?:(?:^|\n)\|[^\n]*\|\s*\n\|[-:\|\s]*\|\s*\n(?:\|[^\n]*\|\s*\n)*)', True),  # Tables
            (r'(?:(?:^|\n)(?:[-*+]|\d+\.)\s+(?:(?!\n(?:[-*+]|\d+\.)\s).)*)', True),  # Lists
            (r'\n\n+', False),  # Paragraphs
            (r'(?<=[:;.!?])\s+', False)  # Sentences
        ]

        for pattern, is_separator in split_patterns:
            if is_separator:
                # Split and keep separators as their own chunks
                chunks = re.split(f'({pattern})', text, flags=re.MULTILINE)
                if len(chunks) > 1:
                    result = []
                    for chunk in chunks:
                        if chunk.strip():
                            result.extend(self._split_semantic(chunk))
                    return result
            else:
                # Split at pattern boundaries
                chunks = re.split(pattern, text, flags=re.MULTILINE)
                if len(chunks) > 1:
                    result = []
                    for chunk in chunks:
                        if chunk.strip():
                            result.extend(self._split_semantic(chunk))
                    return result

        # If no semantic split is possible and chunk is still too large
        return self._emergency_split(text)

    def _merge_chunks(self, chunks: List[str]) -> List[str]:
        """
        Merge semantic chunks until they reach chunk_size, using the last semantic
        chunk as overlap with the next merged chunk.
        """
        if not chunks:
            return []

        merged_chunks = []
        current_chunks = []
        current_tokens = 0
        
        for chunk in chunks:
            chunk_tokens = self._get_token_count(chunk)
            
            # If adding this chunk would exceed chunk_size
            if current_tokens + chunk_tokens > self.chunk_size and current_chunks:
                # Add current group as a chunk
                merged_chunks.append('\n\n'.join(current_chunks))
                # Start new group with the last semantic chunk as overlap
                current_chunks = [current_chunks[-1], chunk]
                current_tokens = self._get_token_count(current_chunks[-2]) + chunk_tokens
            else:
                current_chunks.append(chunk)
                current_tokens += chunk_tokens
        
        # Add the remaining chunks
        if current_chunks:
            merged_chunks.append('\n\n'.join(current_chunks))
        
        return merged_chunks

    def get_embeddings(self, text: str) -> Dict[str, List[float]]:
        """
        Transform markdown text into vector embeddings and return original chunks.
        
        Args:
            text (str): Input markdown text
            
        Returns:
            Dict with:
                'chunks': List[str] - Original text chunks with overlap
                'embeddings': List[List[float]] - List of embeddings
        """
        # Clean and split into smallest semantic chunks
        semantic_chunks = self._split_semantic(text.strip())
        
        # Merge chunks with overlap
        final_chunks = self._merge_chunks(semantic_chunks)
        
        # Generate embeddings
        embeddings = [
            self.model.encode(chunk)
            for chunk in final_chunks
        ]

        # for chunk in final_chunks:
        #     print("----------------- CHUNK ---------------------")
        #     print(chunk)

        print(f"Number of chunks: {len(final_chunks)}")
        
        return {
            'chunks': final_chunks,
            'embeddings': embeddings
        }
    
    def __call__(self, text: str) -> Dict[str, List[float]]:
        """Allow the class to be called directly to generate embeddings."""
        return self.get_embeddings(text)