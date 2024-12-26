import streamlit as st
import httpx
from typing import List
import os

from fileraven.frontend.api_check import assert_api_available

def main():
    """Run the Streamlit application"""


    # Check FastAPI availability
    assert_api_available(
        api_name="FastAPI",
        base_url="http://localhost:8000/",
        error_message="""
        ⚠️ FastAPI server is not running!
        Please start the server using: uvicorn main:app --reload
        """
    )

    # Check Ollama availability without specific endpoint
    assert_api_available(
        api_name="Ollama",
        base_url="http://localhost:11434",
        error_message="""
        ⚠️ Ollama service is not running!
        Please start Ollama and ensure it's running properly.
        """
    )

    # Configure API client
    API_URL = os.getenv("FILERAVEN_API_URL", "http://localhost:8000")
    client = httpx.Client(base_url=API_URL)

    st.title("FileRaven - Document Q&A System")

    # File upload
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])
    if uploaded_file:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        response = client.post("/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            st.success("Document processed successfully!")
        else:
            st.error("Error processing document")

    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your documents"):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response
        response = client.post("/query", json={"question": prompt}, timeout=61.0)
        
        if response.status_code == 200:
            assistant_response = response.json()["response"]
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
        else:
            st.error("Error getting response from backend")

if __name__ == "__main__":
    main()