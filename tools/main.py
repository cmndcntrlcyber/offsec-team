from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Tools Service",
    description="Multi-agent security tools gateway",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "tools-service"}

@app.get("/")
async def root():
    return {"message": "Tools Service API", "version": "1.0.0"}

@app.get("/tools")
async def list_tools():
    return {
        "available_tools": [
            "bug_hunter",
            "burpsuite_operator", 
            "daedelu5",
            "nexus_kamuy",
            "rt_dev"
        ]
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
