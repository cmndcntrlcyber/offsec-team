# Tools Service - Multi-agent security tools gateway
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create requirements.txt for tools service
RUN echo "fastapi==0.104.1\n\
uvicorn[standard]==0.24.0\n\
pydantic==2.5.0\n\
httpx==0.25.2\n\
aiofiles==23.2.1\n\
python-multipart==0.0.6\n\
python-jose[cryptography]==3.3.0\n\
passlib[bcrypt]==1.7.4\n\
redis==5.0.1\n\
psycopg2-binary==2.9.9\n\
sqlalchemy==2.0.23\n\
alembic==1.13.0\n\
celery==5.3.4\n\
prometheus-client==0.19.0\n\
structlog==23.2.0\n\
openapi-schema-pydantic==1.2.4" > requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/cache

# Create a basic main.py if it doesn't exist
RUN if [ ! -f main.py ]; then \
    echo 'from fastapi import FastAPI, HTTPException\n\
from fastapi.middleware.cors import CORSMiddleware\n\
import uvicorn\n\
import os\n\
import logging\n\
\n\
# Configure logging\n\
logging.basicConfig(level=logging.INFO)\n\
logger = logging.getLogger(__name__)\n\
\n\
app = FastAPI(\n\
    title="Tools Service",\n\
    description="Multi-agent security tools gateway",\n\
    version="1.0.0"\n\
)\n\
\n\
# CORS middleware\n\
app.add_middleware(\n\
    CORSMiddleware,\n\
    allow_origins=["*"],\n\
    allow_credentials=True,\n\
    allow_methods=["*"],\n\
    allow_headers=["*"],\n\
)\n\
\n\
@app.get("/health")\n\
async def health_check():\n\
    return {"status": "healthy", "service": "tools-service"}\n\
\n\
@app.get("/")\n\
async def root():\n\
    return {"message": "Tools Service API", "version": "1.0.0"}\n\
\n\
@app.get("/tools")\n\
async def list_tools():\n\
    return {\n\
        "available_tools": [\n\
            "bug_hunter",\n\
            "burpsuite_operator",\n\
            "daedelu5",\n\
            "nexus_kamuy",\n\
            "rt_dev"\n\
        ]\n\
    }\n\
\n\
if __name__ == "__main__":\n\
    port = int(os.getenv("PORT", 8001))\n\
    uvicorn.run(app, host="0.0.0.0", port=port)' > main.py; \
fi

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Expose port
EXPOSE 8001

# Run the service
CMD ["python", "main.py"]
