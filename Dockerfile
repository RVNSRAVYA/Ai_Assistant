FROM python:3.11-slim

# Create a non‑root user to run the app
RUN useradd -m appuser

WORKDIR /app

# Install system build dependencies (if needed) and clean up
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project (excluding .git, etc.)
COPY . ./

# Switch to non‑root user
USER appuser

# Expose the port that Railway provides via the PORT env var (default 8000)
EXPOSE $PORT

# Start the FastAPI app. The entrypoint reads PORT from env.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
