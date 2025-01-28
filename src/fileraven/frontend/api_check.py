import time
from functools import lru_cache
from typing import Optional
from urllib.parse import urlparse

import httpx
import streamlit as st


class APICheckError(Exception):
    """Custom exception for API check failures"""

    pass


@lru_cache(maxsize=1)
def check_api_health(
    base_url: str,
    health_endpoint: Optional[str] = None,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    timeout: float = 5.0,
) -> bool:
    """
    Check if an API service is reachable.

    Args:
        base_url (str): The base URL of the API (e.g., "http://localhost:8000")
        health_endpoint (Optional[str]): Specific health check endpoint (e.g., "/health")
        max_retries (int): Maximum number of retry attempts
        retry_delay (float): Delay between retries in seconds
        timeout (float): Timeout for each request in seconds

    Returns:
        bool: True if API is reachable, False otherwise
    """
    # Ensure base_url doesn't end with a slash
    base_url = base_url.rstrip("/")

    # Construct the full URL
    url = base_url + (health_endpoint if health_endpoint else "")

    # Parse URL to ensure it's valid
    try:
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            return False
    except ValueError:
        return False

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=timeout) as client:
                client.get(url)
                # Consider any response (even errors) as indication that service is running
                return True
        except httpx.RequestError:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            continue
    return False


def assert_api_available(
    api_name: str,
    base_url: str,
    health_endpoint: Optional[str] = None,
    error_message: Optional[str] = None,
) -> None:
    """
    Assert that an API is available and show appropriate Streamlit messages.

    Args:
        api_name (str): Name of the API (e.g., "Ollama" or "FastAPI")
        base_url (str): The base URL of the API
        health_endpoint (Optional[str]): Specific health check endpoint
        error_message (Optional[str]): Custom error message to display if API is unavailable

    Raises:
        APICheckError: If the API is not available after all retries
    """
    check_url = base_url + (health_endpoint if health_endpoint else "")
    with st.spinner(f"Checking {api_name} API availability..."):
        if not check_api_health(base_url, health_endpoint):
            default_message = f"""
                ⚠️ {api_name} API is not reachable at {check_url}.
                Please ensure the API server is running and try again.
                """
            st.error(error_message or default_message)
            # raise APICheckError(f"{api_name} API is not available")
        st.success(f"✅ {api_name} API is available")


# Example usage in a Streamlit app
def main():
    st.title("API Health Check Demo")

    try:
        # Check FastAPI availability with health endpoint
        assert_api_available(
            api_name="FastAPI",
            base_url="http://localhost:8000",
            health_endpoint="/health",
            error_message="""
            ⚠️ FastAPI server is not running!
            Please start the server using: uvicorn main:app --reload
            """,
        )

        # Check Ollama availability without specific endpoint
        assert_api_available(
            api_name="Ollama",
            base_url="http://localhost:11434",
            error_message="""
            ⚠️ Ollama service is not running!
            Please start Ollama and ensure it's running properly.
            """,
        )

        # If both APIs are available, continue with the main app logic
        st.write("All required APIs are available! Continue with your app...")

    except APICheckError:
        st.stop()  # Stop the Streamlit app if any API is unavailable


if __name__ == "__main__":
    main()
