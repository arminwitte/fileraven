import streamlit as st
from typing import Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime

# Assuming AsyncQueryExpander is imported from the previous module
from fileraven.frontend.async_query_expander import AsyncQueryExpander

@dataclass
class QuerySession:
    """Stores the state of the query session"""
    queries: List[Tuple[str, datetime]] = None
    
    def __post_init__(self):
        if self.queries is None:
            self.queries = []

class QueryExplorer:
    """
    An interactive query exploration interface with response history.
    Features:
    - Scrollable history of queries and their responses
    - Sequential query execution with AsyncQueryExpander
    - Timestamp tracking for query sequence
    """
    def __init__(
        self,
        api_endpoint: str,
        height: int = 600
    ):
        self.api_endpoint = api_endpoint
        self.height = height
        
        # Initialize session state
        if 'query_session' not in st.session_state:
            st.session_state.query_session = QuerySession()

    def add_query(self, query: str):
        """Add a new query to the session history"""
        st.session_state.query_session.queries.append((query, datetime.now()))

    def render_query_input(self):
        """Render the query input section"""
        col1, col2 = st.columns([8, 1])
        
        with col1:
            query = st.text_input(
                "Enter your query",
                key="query_input",
                label_visibility="collapsed",
                placeholder="Type your query here..."
            )
        
        with col2:
            execute_pressed = st.button("Send", use_container_width=True)
            
        if execute_pressed and query:
            self.add_query(query)
            # Clear the input
            # st.session_state.query_input = ""
            # Trigger rerun to update interface
            st.rerun()

    def render_query_history(self):
        """Render the scrollable query history with expandable responses"""
        # Create a container with fixed height and scrolling
        with st.container(height=self.height, border=True):
            for i, (query, timestamp) in enumerate(st.session_state.query_session.queries):
                # Create unique key using timestamp
                key = f"query_{timestamp.timestamp()}"
                
                # Add timestamp and sequence number
                st.caption(
                    f"Query #{len(st.session_state.query_session.queries) - i} • "
                    f"{timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                # Create and render query expander
                expander = AsyncQueryExpander(
                    query=query,
                    api_endpoint=self.api_endpoint,
                    key=key
                )
                expander.render()
                
                # Add some spacing between queries
                st.markdown("<br>", unsafe_allow_html=True)

    def render(self):
        """Render the complete query explorer interface"""
        # Render query history first (appears above)
        self.render_query_history()
        
        # Render input section at the bottom
        self.render_query_input()

# Example usage:
def main():
    st.title("Query Explorer")
    
    def handle_sources():
        st.write("Displaying sources...")
    
    explorer = QueryExplorer(
        api_endpoint="http://api.example.com/query",
        height=500,
    )
    
    explorer.render()

if __name__ == "__main__":
    main()