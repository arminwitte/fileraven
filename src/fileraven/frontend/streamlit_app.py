import streamlit as st
import httpx
from typing import List
import os
import uuid

from fileraven.frontend.api_check import assert_api_available
from fileraven.frontend.download_dialog import download_file

@st.dialog("API Availability")
def check_api():

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

@st.dialog("File Upload")
def upload_file(client: httpx.Client):

    # File upload
    uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])
    button_send = st.button("Send to database", use_container_width=True)
    if uploaded_file and button_send:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
        response = client.post("/upload", files=files, timeout=600.0)
        
        if response.status_code == 200:
            st.success("Document processed successfully!")
        else:
            st.error("Error processing document")

def main():
    """Run the Streamlit application"""

    with st.sidebar:
        button_check_api = st.button("\u2705 Check API availability", use_container_width=True)
        if button_check_api:
            check_api()

    # Configure API client
    API_URL = os.getenv("FILERAVEN_API_URL", "http://localhost:8000")
    client = httpx.Client(base_url=API_URL)

    st.title("FileRaven - Document Q&A System")

    with st.sidebar:
        button_upload_file = st.button("\u2B06 \uFE0F Upload a document", use_container_width=True)
        if button_upload_file:
            upload_file(client)

    with st.sidebar:
        button_download_file = st.button("\u2B07 \uFE0F Download a document", use_container_width=True)
        if button_download_file:
            download_file()

    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "sources" not in st.session_state:
        st.session_state.sources = set()

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
        response = client.post("/query", json={"question": prompt}, timeout=630.0)
        
        if response.status_code == 200:
            assistant_response = response.json()["response"]
            assistant_sources = response.json()["sources"]
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            st.session_state.sources.update(assistant_sources)
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
                # sources = set(assistant_sources)
                # for source in sources:
                #     print(source)
                #     filepath = os.path.join(source)
                #     filename = os.path.basename(filepath)
                #     with open(filepath, 'rb') as f:
                #         # st.download_button('Download Docx', f, file_name='New_File.docx')
                #         st.download_button(
                #             label=filename,
                #             data=f,
                #             file_name=filename,
                #             key=uuid.uuid1(),
# )
        else:
            st.error("Error getting response from backend")

if __name__ == "__main__":
    main()