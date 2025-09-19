"""
Legal data retrieval helper
Retrieves data from JSON files and answers legal questions
"""

import json
import os
from typing import Dict, List, Any, Optional
import re


class LegalDataRetriever:
    """Helper class for retrieving legal data from JSON files"""
    
    def __init__(self, data_dir: str = "dat/sample_docs"):
        """Initialize the retriever with data directory"""
        self.data_dir = data_dir
        self.legal_data = {}
        self.load_legal_data()
    
    def load_legal_data(self) -> None:
        """Load all legal data from JSON files in the data directory"""
        if not os.path.exists(self.data_dir):
            print(f"Warning: Data directory {self.data_dir} not found")
            return
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.data_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Handle different JSON structures
                        if isinstance(data, list):
                            # Direct array of questions
                            self.legal_data[filename] = {'questions': data}
                            print(f"Loaded {filename}: {len(data)} questions")
                        elif isinstance(data, dict) and 'questions' in data:
                            # Object with questions key
                            self.legal_data[filename] = data
                            print(f"Loaded {filename}: {len(data['questions'])} questions")
                        else:
                            print(f"Warning: Unknown format in {filename}")
                            
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    def search_questions(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for questions matching the query
        
        Args:
            query: Search query
            
        Returns:
            List of matching questions and answers
        """
        results = []
        query_lower = query.lower()
        query_words = [word for word in query_lower.split() if len(word) > 2]
        
        for filename, data in self.legal_data.items():
            if 'questions' in data:
                for question_data in data['questions']:
                    question_text = question_data.get('question', '').lower()
                    answer_text = question_data.get('answer', '').lower()
                    
                    # Calculate relevance score
                    score = 0
                    
                    # Exact phrase match (highest priority)
                    if query_lower in question_text:
                        score += 100
                    if query_lower in answer_text:
                        score += 80
                    
                    # Word matches
                    for word in query_words:
                        if word in question_text:
                            score += 10
                        if word in answer_text:
                            score += 5
                    
                    # If we have a good match, add to results
                    if score > 0:
                        results.append({
                            'question': question_data.get('question', ''),
                            'answer': question_data.get('answer', ''),
                            'category': question_data.get('category', ''),
                            'source': filename,
                            'score': score
                        })
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def get_answer_for_question(self, question: str) -> Optional[str]:
        """
        Get the best answer for a given question
        
        Args:
            question: The legal question
            
        Returns:
            Best matching answer or None
        """
        results = self.search_questions(question)
        
        if not results:
            return None
        
        # Return the first (most relevant) result
        return results[0]['answer']
    
    def get_related_questions(self, topic: str, limit: int = 5) -> List[str]:
        """
        Get related questions for a topic
        
        Args:
            topic: Topic to search for
            limit: Maximum number of questions to return
            
        Returns:
            List of related questions
        """
        results = self.search_questions(topic)
        questions = [result['question'] for result in results[:limit]]
        return questions
    
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


def answer_legal_question(question: str, data_dir: str = "dat/sample_docs") -> str:
    """
    Simple function to answer a legal question using the JSON data
    
    Args:
        question: The legal question
        data_dir: Directory containing JSON data files
        
    Returns:
        Answer to the question or a default message
    """
    retriever = LegalDataRetriever(data_dir)
    answer = retriever.get_answer_for_question(question)
    
    if answer:
        return answer
    else:
        # Try to provide a helpful response even if no exact match
        results = retriever.search_questions(question)
        if results:
            return f"I found related information: {results[0]['answer']}"
        else:
            return "I don't have specific information about that question in my database. Please try rephrasing your question or ask about fundamental rights, constitutional law, or legal procedures."


def search_legal_database(query: str, data_dir: str = "dat/sample_docs") -> List[Dict[str, Any]]:
    """
    Search the legal database for relevant information
    
    Args:
        query: Search query
        data_dir: Directory containing JSON data files
        
    Returns:
        List of matching results
    """
    retriever = LegalDataRetriever(data_dir)
    return retriever.search_questions(query)


# Example usage
if __name__ == "__main__":
    # Test the retriever
    retriever = LegalDataRetriever()
    
    print("Legal Data Retriever Test")
    print("=" * 30)
    
    # Show statistics
    stats = retriever.get_statistics()
    print(f"Loaded {stats['total_files']} files with {stats['total_questions']} questions")
    print(f"Categories: {', '.join(stats['categories'])}")
    print()
    
    # Test search
    test_questions = [
        "What is the fundamental right to equality?",
        "What are the six fundamental freedoms?",
        "What is the right to life?"
    ]
    
    for question in test_questions:
        print(f"Q: {question}")
        answer = retriever.get_answer_for_question(question)
        if answer:
            print(f"A: {answer[:100]}...")
        else:
            print("A: No specific answer found")
        print()
