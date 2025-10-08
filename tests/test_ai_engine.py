"""
Simple tests for Legal Mind AI engine
"""

import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.ai_engine import LegalMindAI
from src.txt_formatter import clean_legal_text, extract_sections, extract_case_citations


class TestLegalMindAI(unittest.TestCase):
    """Test cases for Legal Mind AI engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ai = LegalMindAI()
    
    def test_ai_engine_initialization(self):
        """Test AI engine initialization"""
        self.assertFalse(self.ai.model_loaded)
        self.ai.load_model()
        self.assertTrue(self.ai.model_loaded)
    
    def test_document_analysis(self):
        """Test document analysis functionality"""
        sample_text = "This is a test legal document."
        result = self.ai.analyze_document(sample_text)
        
        self.assertIsInstance(result, dict)
        self.assertIn("document_type", result)
        self.assertIn("summary", result)
        self.assertIn("confidence", result)
    
    def test_legal_question_answering(self):
        """Test legal question answering"""
        question = "What is a contract?"
        answer = self.ai.answer_legal_question(question)
        
        self.assertIsInstance(answer, str)
        self.assertGreater(len(answer), 0)
    
    def test_entity_extraction(self):
        """Test legal entity extraction"""
        text = "John Doe signed a contract with Jane Smith."
        entities = self.ai.extract_legal_entities(text)
        
        self.assertIsInstance(entities, list)


class TestTextUtils(unittest.TestCase):
    """Test cases for text utilities"""
    
    def test_clean_legal_text(self):
        """Test legal text cleaning"""
        dirty_text = "  This   is    a   test.  \n\n  "
        cleaned = clean_legal_text(dirty_text)
        
        self.assertEqual(cleaned, "This is a test.")
    
    def test_extract_sections(self):
        """Test section extraction"""
        text = """
        Section 1. Introduction
        This is the introduction.
        
        Section 2. Terms
        These are the terms.
        """
        sections = extract_sections(text)
        
        self.assertIsInstance(sections, list)
        self.assertGreater(len(sections), 0)
    
    def test_extract_case_citations(self):
        """Test case citation extraction"""
        text = "See Smith v. Jones, 123 F.3d 456 (2023)."
        citations = extract_case_citations(text)
        
        self.assertIsInstance(citations, list)


if __name__ == '__main__':
    unittest.main()
