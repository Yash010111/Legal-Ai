"""
FastAPI server for Legal Mind AI MCP
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn

from .routes import router

app = FastAPI(
    title="Legal Mind AI MCP Server",
    description="Model Context Protocol server for Legal Mind AI",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Legal Mind AI MCP Server is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "legal-mind-ai-mcp"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
