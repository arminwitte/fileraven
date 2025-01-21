import httpx

class RAGEngine:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        
    def generate_response(self, query: str, context: str):
        """
        Generate response using Ollama with RAG context
        """
        prompt = f"""Context: {context}

Question: {query}

Please provide a response based on the context chunks (separated by dashes) above.
If the answer is not stated in the context directly, try to infer it from the context stating that you did so.
The answer should be short and concise.
If the context doesn't contain relevant information, please say so."""
        
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
