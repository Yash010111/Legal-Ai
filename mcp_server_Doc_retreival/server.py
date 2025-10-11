"""
FastAPI server for Legal Mind AI MCP
Supports both HTTP API and MCP protocol for client communication
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uvicorn
import json
import asyncio
import sys
import os

from mcp_server_Doc_retreival.routes import router

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


class MCPRequest(BaseModel):
    """MCP request model"""
    jsonrpc: str = "2.0"
    id: int
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPResponse(BaseModel):
    """MCP response model"""
    jsonrpc: str = "2.0"
    id: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


class MCPTool(BaseModel):
    """MCP tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


# MCP Tools available to clients
MCP_TOOLS = [
    MCPTool(
        name="ask_legal_question",
        description="Ask a legal question and get an answer from the Legal Mind AI",
        inputSchema={
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The legal question to ask"
                },
                "context": {
                    "type": "string",
                    "description": "Optional context for the question"
                }
            },
            "required": ["question"]
        }
    ),
    MCPTool(
        name="analyze_legal_document",
        description="Analyze a legal document for entities, sections, and citations",
        inputSchema={
            "type": "object",
            "properties": {
                "document_text": {
                    "type": "string",
                    "description": "The legal document text to analyze"
                }
            },
            "required": ["document_text"]
        }
    ),
    MCPTool(
        name="search_legal_database",
        description="Search the legal database for relevant information",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for the legal database"
                }
            },
            "required": ["query"]
        }
    )
]


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Legal Mind AI MCP Server is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "legal-mind-ai-mcp"}


@app.post("/mcp", response_model=MCPResponse)
async def mcp_endpoint(request: MCPRequest):
    """
    MCP (Model Context Protocol) endpoint for client communication
    
    Args:
        request: MCP request with method and parameters
        
    Returns:
        MCP response with result or error
    """
    try:
        if request.method == "initialize":
            return MCPResponse(
                id=request.id,
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {
                            "listChanged": True
                        }
                    },
                    "serverInfo": {
                        "name": "legal-mind-ai-mcp",
                        "version": "0.1.0"
                    }
                }
            )
        elif request.method == "tools/list":
            return MCPResponse(
                id=request.id,
                result={
                    "tools": [tool.dict() for tool in MCP_TOOLS]
                }
            )
        elif request.method == "tools/call":
            if not request.params or "name" not in request.params:
                return MCPResponse(
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": "Error: Invalid params: missing tool name"
                            }
                        ]
                    },
                    error={
                        "code": -32602,
                        "message": "Invalid params: missing tool name"
                    }
                )
            tool_name = request.params["name"]
            tool_args = request.params.get("arguments", {})
            # Route to appropriate tool handler
            if tool_name == "ask_legal_question":
                result = await handle_ask_legal_question(tool_args)
            elif tool_name == "analyze_legal_document":
                result = await handle_analyze_legal_document(tool_args)
            elif tool_name == "search_legal_database":
                result = await handle_search_legal_database(tool_args)
            else:
                return MCPResponse(
                    id=request.id,
                    result={
                        "content": [
                            {
                                "type": "text",
                                "text": f"Error: Unknown tool: {tool_name}"
                            }
                        ]
                    },
                    error={
                        "code": -32601,
                        "message": f"Unknown tool: {tool_name}"
                    }
                )
            return MCPResponse(
                id=request.id,
                result=result
            )
        else:
            return MCPResponse(
                id=request.id,
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": f"Error: Unknown method: {request.method}"
                        }
                    ]
                },
                error={
                    "code": -32601,
                    "message": f"Unknown method: {request.method}"
                }
            )
    except Exception as e:
        return MCPResponse(
            id=request.id,
            result={
                "content": [
                    {
                        "type": "text",
                        "text": f"Internal error: {str(e)}"
                    }
                ]
            },
            error={
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        )


async def handle_ask_legal_question(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle ask_legal_question tool call using RAG from helpers/retrieval.py"""
    try:
        from helpers import retrieval
        question = args.get("question", "")
        # context is ignored for now, but can be used for advanced retrieval
        answer = retrieval.answer_legal_question(question)
        return {
            "content": [
                {
                    "type": "text",
                    "text": answer
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error processing legal question: {str(e)}"
                }
            ]
        }


async def handle_analyze_legal_document(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle analyze_legal_document tool call"""
    try:
        # Import here to avoid circular imports
        from .routes import ai_engine
        from src.txt_formatter import clean_legal_text, extract_sections, extract_case_citations
        
        document_text = args.get("document_text", "")
        
        # Clean the document text
        cleaned_text = clean_legal_text(document_text)
        
        # Extract sections
        sections = extract_sections(cleaned_text)
        
        # Extract case citations
        citations = extract_case_citations(cleaned_text)
        
        # Analyze with AI engine
        analysis = ai_engine.analyze_document(cleaned_text)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Document Analysis Results:\n\n"
                           f"Document Type: {analysis.get('document_type', 'legal_document')}\n"
                           f"Summary: {analysis.get('summary', 'Document analysis completed')}\n"
                           f"Sections Found: {len(sections)}\n"
                           f"Citations Found: {len(citations)}\n"
                           f"Confidence: {analysis.get('confidence', 0.0)}"
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error analyzing document: {str(e)}"
                }
            ]
        }


async def handle_search_legal_database(args: Dict[str, Any]) -> Dict[str, Any]:
    """Handle search_legal_database tool call using RAG from helpers/retrieval.py"""
    try:
        from helpers import retrieval
        query = args.get("query", "")
        results = retrieval.search_legal_database(query)
        if results:
            passages = "\n\n".join([
                f"From {r['filename']}\n{r['passage'][:500]}" for r in results
            ])
            text = f"Search results for '{query}':\n\n{passages}"
        else:
            text = f"No relevant information found for '{query}' in the legal datasets."
        return {
            "content": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error searching database: {str(e)}"
                }
            ]
        }


if __name__ == "__main__":
    print("🚀 Starting Legal Mind AI MCP Server...")
    print("🌐 Server will be accessible at:")
    print("   - Local: http://localhost:8000")
    print("   - Network: http://[YOUR_IP]:8000")
    print("   - MCP Endpoint: http://[YOUR_IP]:8000/mcp")
    print("   - Health Check: http://[YOUR_IP]:8000/health")
    print("\n📋 For clients on other PCs, use your machine's IP address")
    print("   Find your IP with: ipconfig (Windows) or ifconfig (Linux/Mac)")
    print("\n🔧 Starting server...")
    
    uvicorn.run(
        app, 
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,
        log_level="info"
    )
