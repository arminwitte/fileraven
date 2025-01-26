import streamlit as st
import asyncio
import httpx
from typing import Optional, Any
from dataclasses import dataclass
from contextlib import contextmanager

@dataclass
class QueryState:
    """Stores the state of a query execution"""
    is_loading: bool = False
    response: Optional[Any] = None
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
        key: str,
        on_sources_click: Optional[callable] = None
    ):
        self.query = query
        self.api_endpoint = api_endpoint
        self.key = key
        self.on_sources_click = on_sources_click
        
        # Initialize session state for this instance
        if f"query_state_{key}" not in st.session_state:
            st.session_state[f"query_state_{key}"] = QueryState()

    @contextmanager
    def loading_state(self):
        """Context manager to handle loading state"""
        state = st.session_state[f"query_state_{self.key}"]
        state.is_loading = True
        try:
            yield
        finally:
            state.is_loading = False

    async def fetch_data(self):
        """Fetch data from the API endpoint"""
        state = st.session_state[f"query_state_{self.key}"]
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.api_endpoint,
                    json={"query": self.query},
                    timeout=30.0
                )
                response.raise_for_status()
                state.response = response.json()
                state.error = None
            except Exception as e:
                state.error = str(e)
                state.response = None

    def render(self):
        """Render the component"""
        state = st.session_state[f"query_state_{self.key}"]
        
        with st.expander(f"Query: {self.query}", expanded=True):
            # Create a container for the response section
            response_container = st.container()
            
            with response_container:
                if state.is_loading:
                    # Center the spinner using columns
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.spinner("Executing query...")
                        st.caption("This may take a few moments...")
            
            if state.error:
                st.error(f"Error: {state.error}")
            
            if state.response:
                st.json(state.response)
                
                # Sources button
                if st.button(
                    "Sources",
                    key=f"sources_btn_{self.key}",
                    on_click=self.on_sources_click if self.on_sources_click else None
                ):
                    if not self.on_sources_click:
                        st.info("Sources callback not configured")
            
            # Execute button (only show if no response or error)
            if not state.response and not state.error and not state.is_loading:
                if st.button("Execute Query", key=f"execute_btn_{self.key}"):
                    with self.loading_state():
                        asyncio.run(self.fetch_data())

# Example usage:
def main():
    st.title("Query Explorer")
    
    # Example sources handler
    def handle_sources():
        st.write("Displaying sources...")
    
    # Create multiple query expanders
    queries = [
        ("SELECT * FROM users", "http://api.example.com/query1"),
        ("SELECT * FROM orders", "http://api.example.com/query2")
    ]
    
    for i, (query, endpoint) in enumerate(queries):
        expander = AsyncQueryExpander(
            query=query,
            api_endpoint=endpoint,
            key=f"query_{i}",
            on_sources_click=handle_sources
        )
        expander.render()

if __name__ == "__main__":
    main()