import httpx

class RAGEngine:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        
    def generate_response(self, query: str, context: str, source: str):
        """
        Generate response using Ollama with RAG context
        """
        prompt = f"""Context: {context}

Question: {query}

Sources: {source}

Please provide a response based on the context above.
The answer should be short and concise.
If the context doesn't contain relevant information, please say so.
Finally, if applicable, add the files listed under sources as a markdown formated list of links to the local files at the bottom of the response."""
        
        # print(prompt)

        # Call Ollama API
        response = httpx.post(
            self.ollama_url,
            json={
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False
            },
            timeout=600.0,
        )

        print(response)
        
        return response.json()["response"]
