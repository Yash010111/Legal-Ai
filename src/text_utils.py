"""
Text cleaning, formatting, and parsing utilities for Legal Mind AI
"""

import re
from typing import List, Dict, Any


def clean_legal_text(text: str) -> str:
    """
    Clean and normalize legal text for processing
    
    Args:
        text: Raw legal text
        
    Returns:
        Cleaned and normalized text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove page numbers and headers/footers
    text = re.sub(r'Page \d+ of \d+', '', text)
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Normalize legal citations
    text = normalize_citations(text)
    
    return text.strip()


def normalize_citations(text: str) -> str:
    """
    Normalize legal citations in text
    
    Args:
        text: Text containing legal citations
        
    Returns:
        Text with normalized citations
    """
    # Common legal citation patterns
    citation_patterns = [
        (r'(\d+)\s+U\.S\.C\.\s+§\s*(\d+)', r'\1 U.S.C. § \2'),
        (r'(\d+)\s+F\.\s*(\d+)\s*\((\d{4})\)', r'\1 F.\2 (\3)'),
        (r'(\d+)\s+S\.\s*Ct\.\s*(\d+)\s*\((\d{4})\)', r'\1 S. Ct. \2 (\3)'),
    ]
    
    for pattern, replacement in citation_patterns:
        text = re.sub(pattern, replacement, text)
    
    return text


def extract_sections(text: str) -> List[Dict[str, Any]]:
    """
    Extract sections and subsections from legal text
    
    Args:
        text: Legal document text
        
    Returns:
        List of sections with their content and metadata
    """
    sections = []
    
    # Pattern for section headers (e.g., "Section 1. Title", "1.1 Subsection")
    section_pattern = r'^(?:Section\s+)?(\d+(?:\.\d+)*)\.?\s+(.+)$'
    
    lines = text.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = re.match(section_pattern, line, re.IGNORECASE)
        if match:
            # Save previous section if exists
            if current_section:
                sections.append(current_section)
            
            # Start new section
            section_number = match.group(1)
            section_title = match.group(2)
            current_section = {
                'number': section_number,
                'title': section_title,
                'content': '',
                'subsections': []
            }
        elif current_section:
            current_section['content'] += line + '\n'
    
    # Add the last section
    if current_section:
        sections.append(current_section)
    
    return sections


def extract_case_citations(text: str) -> List[str]:
    """
    Extract case citations from legal text
    
    Args:
        text: Legal document text
        
    Returns:
        List of case citations found in the text
    """
    # Common case citation patterns
    patterns = [
        r'\b[A-Z][a-z]+\s+v\.\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+\d+\s+[A-Z\.]+\s+\d+\s*\(\d{4}\)',
        r'\b[A-Z][a-z]+\s+v\.\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+\d+\s+F\.\s*\d+\s*\(\d{4}\)',
        r'\b[A-Z][a-z]+\s+v\.\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+\d+\s+S\.\s*Ct\.\s*\d+\s*\(\d{4}\)',
    ]
    
    citations = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        citations.extend(matches)
    
    return list(set(citations))  # Remove duplicates


def format_legal_text(text: str, max_line_length: int = 80) -> str:
    """
    Format legal text with proper line breaks and indentation
    
    Args:
        text: Legal text to format
        max_line_length: Maximum characters per line
        
    Returns:
        Formatted legal text
    """
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append('')
            continue
        
        # If line is too long, break it at word boundaries
        if len(line) > max_line_length:
            words = line.split()
            current_line = ''
            
            for word in words:
                if len(current_line + ' ' + word) <= max_line_length:
                    current_line += (' ' + word) if current_line else word
                else:
                    if current_line:
                        formatted_lines.append(current_line)
                    current_line = word
            
            if current_line:
                formatted_lines.append(current_line)
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)



