FROM python:3.11-slim

WORKDIR /app

# Optional: pass a PyTorch index URL at build time for GPU wheels.
# Example: https://download.pytorch.org/whl/cu124
ARG TORCH_INDEX_URL=

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && if [ -n "$TORCH_INDEX_URL" ]; then \
        pip install --no-cache-dir --index-url "$TORCH_INDEX_URL" torch torchvision; \
    fi

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
