from markitdown import MarkItDown
import os
from typing import Union
import tempfile

def process_document(content: Union[bytes, str], filename: str) -> str:
    """
    Process uploaded document and convert to markdown
    
    Args:
        content: Document content as bytes or string
        filename: Name of the uploaded file
        
    Returns:
        str: Processed markdown text
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
        if isinstance(content, str):
            temp_file.write(content.encode())
        else:
            temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        md = MarkItDown()
        result = md.convert(temp_path)
        return result.text_content
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)