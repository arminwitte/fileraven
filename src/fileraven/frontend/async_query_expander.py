import streamlit as st
import asyncio
import httpx
from typing import Optional, Any
from dataclasses import dataclass
from contextlib import contextmanager

from fileraven.frontend.download_dialog import download_sources

@dataclass
class QueryState:
    """Stores the state of a query execution"""
    posted: bool = False
    response: Optional[str] = None
    sources: Optional[list] = None
    error: Optional[str] = None

class AsyncQueryExpander:
    """
    A Streamlit component that shows a query, its response, and a sources button.
    Features:
    - Async query execution
    - Loading state handling
    - Error handling
    - Sources button
    """
    def __init__(
        self,
        query: str,
        api_endpoint: str,
        key: str
    ):
        self.query = query
        self.api_endpoint = api_endpoint
        self.key = key
        self.state = QueryState()
        
        # Initialize session state for this instance
        if f"query_state_{key}" not in st.session_state:
            st.session_state[f"query_state_{key}"] = QueryState()

        if not self.state.posted:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            loop.create_task(self.background_task())
            self.state.posted = True

    def render(self):
        with st.expander(f"{self.query}", expanded=True):
            if self.state.response:
                st.markdown(self.state.response)

            if self.state.error:
                st.error(f"Error: {self.state.error}")
                
            # Sources button
            if self.state.sources:
                if button_sources := st.button(
                    "Sources",
                    key=f"sources_btn_{self.key}",
                ):
                    download_sources(self.state.sources)

    async def background_task(self):
        await self.fetch_data()
        # Force a rerun to update the UI
        st.rerun()

    async def fetch_data(self):
        """Fetch data from the API endpoint"""
        state = st.session_state[f"query_state_{self.key}"]
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.api_endpoint,
                    json={"question": self.query},
                    timeout=630.0
                )
                response.raise_for_status()
                state.response = response.json()["response"]
                state.sources = response.json()["sources"]
                state.error = None
            except Exception as e:
                state.error = str(e)
                state.response = None
                state.sources = None