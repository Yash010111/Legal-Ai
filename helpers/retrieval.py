"""
Legal data retrieval helper
Retrieves data from JSON files and answers legal questions
"""

import json
import os
from typing import Dict, List, Any, Optional
import re


class LegalRAGRetriever:
    """Retrieves and answers legal questions from TXT files using RAG (datasets folder)"""
    def __init__(self, data_dir: str = "datasets"):
        self.data_dir = data_dir
        self.documents = []
        self.load_documents()

    def load_documents(self) -> None:
        """Load all TXT documents from the datasets directory"""
        if not os.path.exists(self.data_dir):
            print(f"Warning: Data directory {self.data_dir} not found")
            return
        for filename in os.listdir(self.data_dir):
            if filename.lower().endswith('.txt'):
                file_path = os.path.join(self.data_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        self.documents.append({
                            'filename': filename,
                            'text': text
                        })
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    def search_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for relevant passages in TXT documents using keyword and semantic matching
        Args:
            query: Search query
            top_k: Number of top results to return
        Returns:
            List of relevant passages
        """
        results = []
        query_lower = query.lower()
        query_words = [word for word in query_lower.split() if len(word) > 2]
        for doc in self.documents:
            text = doc['text'].lower()
            score = 0
            # Exact phrase match
            if query_lower in text:
                score += 100
            # Word matches
            for word in query_words:
                if word in text:
                    score += 10
            # Find best matching paragraph
            paragraphs = re.split(r'\n{2,}', doc['text'])
            best_para = ""
            best_para_score = 0
            for para in paragraphs:
                para_lower = para.lower()
                para_score = 0
                if query_lower in para_lower:
                    para_score += 100
                for word in query_words:
                    if word in para_lower:
                        para_score += 10
                if para_score > best_para_score:
                    best_para_score = para_score
                    best_para = para
            if best_para_score > 0:
                results.append({
                    'filename': doc['filename'],
                    'passage': best_para.strip(),
                    'score': best_para_score
                })
            elif score > 0:
                # Fallback: add whole document
                results.append({
                    'filename': doc['filename'],
                    'passage': doc['text'][:500],
                    'score': score
                })
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def answer_legal_question(self, question: str) -> str:
        """
        Answer a legal question using RAG from TXT documents
        Args:
            question: The legal question
        Returns:
            Best matching passage or a helpful message
        """
        results = self.search_documents(question, top_k=1)
        if results:
            return f"Relevant info from {results[0]['filename']}\n\n{results[0]['passage']}"
        else:
            return "No relevant information found in the legal datasets. Please try rephrasing your question."
    
    def get_related_questions(self, topic: str, limit: int = 5) -> List[str]:
        """
        Get related questions for a topic by extracting sentences containing keywords from loaded documents.
        Args:
            topic: Topic to search for
            limit: Maximum number of questions to return
        Returns:
            List of related questions
        """
        related = []
        topic_lower = topic.lower()
        for doc in self.documents:
            sentences = re.split(r'[\.!?]', doc['text'])
            for sent in sentences:
                if topic_lower in sent.lower() and len(sent.strip()) > 20:
                    related.append(sent.strip())
        # Fallback: suggest fundamental rights if nothing found
        if not related:
            related = [
                "What are the fundamental rights in the Constitution of India?",
                "What is the Right to Equality?",
                "What is the Right to Freedom?",
                "What is the Right to Constitutional Remedies?"
            ]
        return related[:limit]
    
    def get_categories(self) -> List[str]:
        """Get all available categories"""
        categories = set()
        for data in self.legal_data.values():
            if 'questions' in data:
                for question_data in data['questions']:
                    category = question_data.get('category', '')
                    if category:
                        categories.add(category)
        return list(categories)
    
    def get_questions_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all questions in a specific category
        
        Args:
            category: Category name
            
        Returns:
            List of questions in the category
        """
        results = []
        for data in self.legal_data.values():
            if 'questions' in data:
                for question_data in data['questions']:
                    if question_data.get('category', '').lower() == category.lower():
                        results.append(question_data)
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the loaded legal data"""
        total_questions = 0
        total_files = len(self.legal_data)
        categories = set()
        
        for data in self.legal_data.values():
            if 'questions' in data:
                total_questions += len(data['questions'])
                for question_data in data['questions']:
                    category = question_data.get('category', '')
                    if category:
                        categories.add(category)
        
        return {
            'total_files': total_files,
            'total_questions': total_questions,
            'categories': list(categories),
            'category_count': len(categories)
        }


def answer_legal_question(question: str, data_dir: str = "datasets") -> str:
    """
    Answer a legal question using RAG from TXT documents in datasets/
    Args:
        question: The legal question
        data_dir: Directory containing TXT data files
    Returns:
        Best matching passage or a helpful message
    """
    retriever = LegalRAGRetriever(data_dir)
    return retriever.answer_legal_question(question)


def search_legal_database(query: str, data_dir: str = "datasets") -> List[Dict[str, Any]]:
    """
    Search the legal database for relevant passages in TXT documents
    Args:
        query: Search query
        data_dir: Directory containing TXT data files
    Returns:
        List of matching passages
    """
    retriever = LegalRAGRetriever(data_dir)
    return retriever.search_documents(query)


if __name__ == "__main__":
    retriever = LegalRAGRetriever()
    print("Legal RAG Retriever Test")
    print("=" * 30)
    test_questions = [
        "What is the fundamental right to equality?",
        "What are the six fundamental freedoms?",
        "What is the right to life?"
    ]
    for question in test_questions:
        print(f"Q: {question}")
        answer = retriever.answer_legal_question(question)
        print(f"A: {answer[:200]}...")
        print()
