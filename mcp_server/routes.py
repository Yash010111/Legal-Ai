"""
API routes for Legal Mind AI MCP Server
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_engine import LegalMindAI
from text_utils import clean_legal_text, extract_sections, extract_case_citations

router = APIRouter()

# Initialize AI engine
ai_engine = LegalMindAI()


class QueryRequest(BaseModel):
    """Request model for legal queries"""
    question: str
    context: Optional[str] = None


class DocumentAnalysisRequest(BaseModel):
    """Request model for document analysis"""
    document_text: str


class QueryResponse(BaseModel):
    """Response model for queries"""
    answer: str
    confidence: float
    sources: List[str] = []


class DocumentAnalysisResponse(BaseModel):
    """Response model for document analysis"""
    document_type: str
    key_entities: List[Dict[str, Any]]
    summary: str
    sections: List[Dict[str, Any]]
    citations: List[str]
    confidence: float


@router.post("/query", response_model=QueryResponse)
async def query_legal_question(request: QueryRequest):
    """
    Answer a legal question
    
    Args:
        request: Query request with question and optional context
        
    Returns:
        Answer to the legal question
    """
    try:
        answer = ai_engine.answer_legal_question(
            question=request.question,
            context=request.context or ""
        )
        
        return QueryResponse(
            answer=answer,
            confidence=0.8,  # TODO: Implement actual confidence scoring
            sources=[]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-document", response_model=DocumentAnalysisResponse)
async def analyze_document(request: DocumentAnalysisRequest):
    """
    Analyze a legal document
    
    Args:
        request: Document analysis request with document text
        
    Returns:
        Analysis results including entities, sections, and citations
    """
    try:
        # Clean the document text
        cleaned_text = clean_legal_text(request.document_text)
        
        # Extract sections
        sections = extract_sections(cleaned_text)
        
        # Extract case citations
        citations = extract_case_citations(cleaned_text)
        
        # Analyze with AI engine
        analysis = ai_engine.analyze_document(cleaned_text)
        
        return DocumentAnalysisResponse(
            document_type=analysis.get("document_type", "legal_document"),
            key_entities=analysis.get("key_entities", []),
            summary=analysis.get("summary", "Document analysis completed"),
            sections=sections,
            citations=citations,
            confidence=analysis.get("confidence", 0.0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document for processing
    
    Args:
        file: Uploaded document file
        
    Returns:
        Processing status and document ID
    """
    try:
        # TODO: Implement document upload and processing
        content = await file.read()
        
        return {
            "message": "Document uploaded successfully",
            "filename": file.filename,
            "size": len(content),
            "document_id": "temp_id"  # TODO: Generate proper document ID
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def list_documents():
    """
    List all uploaded documents
    
    Returns:
        List of uploaded documents
    """
    try:
        # TODO: Implement document listing
        return {
            "documents": [],
            "total": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
