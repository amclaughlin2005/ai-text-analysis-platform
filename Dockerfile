# Use Python 3.11 official image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy backend requirements first (for better caching)
COPY backend/requirements.txt /app/backend/

# Install Python dependencies
RUN cd backend && pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory
COPY backend/ /app/backend/

# Set Python path
ENV PYTHONPATH=/app/backend

# Expose port (Railway will override this)
EXPOSE 8000

# Change to backend directory and start the server
WORKDIR /app/backend
CMD ["python3", "production_server.py"]
