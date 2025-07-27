FROM python:3.10-slim

# Set environment vars
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install torch CPU-only first
RUN pip install --no-cache-dir \
    torch==2.2.2+cpu \
    -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download model for offline use
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy code
COPY main.py .

# Entrypoint
CMD ["python", "main.py"]
