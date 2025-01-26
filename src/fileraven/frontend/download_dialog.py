import os
import uuid
import streamlit as st

@st.dialog("Downloads")
def download_file():
    sources = st.session_state.sources
    for source in sources:
        filepath = os.path.join(source)
        filename = os.path.basename(filepath)
        with open(filepath, 'rb') as f:
            # st.download_button('Download Docx', f, file_name='New_File.docx')
            st.download_button(
                label=filename,
                data=f,
                file_name=filename,
                key=uuid.uuid1(),
            )


@st.dialog("Sources")
def download_sources(sources: list):
    for source in sources:
        filepath = os.path.join(source)
        filename = os.path.basename(filepath)
        with open(filepath, 'rb') as f:
            # st.download_button('Download Docx', f, file_name='New_File.docx')
            st.download_button(
                label=filename,
                data=f,
                file_name=filename,
                key=uuid.uuid1(),
            )