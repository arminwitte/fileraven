FROM python:3.11-slim

WORKDIR /code

# Install requirements first for better caching
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir -e ".[frontend]"

# Copy application code
# COPY . ./fileraven/frontend
# RUN pip install --no-cache-dir .

# Streamlit runs on port 8501 by default
EXPOSE 8501

# Run streamlit
CMD ["streamlit", "run", "src/fileraven/frontend/streamlit_app.py"]