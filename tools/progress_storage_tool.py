"""
Progress Storage Tool - Persists student progress data
Handles reading/writing student progress to storage
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class ProgressStorageTool:
    """
    Custom tool for storing and retrieving student progress.
    Uses JSON file storage (in production, use database).
    """
    
    def __init__(self, storage_dir: str = "data/progress"):
        """
        Initialize progress storage
        
        Args:
            storage_dir: Directory for storing progress files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_student_file(self, student_id: str) -> Path:
        """Get file path for student's progress data"""
        return self.storage_dir / f"{student_id}.json"
    
    def save_progress(
        self,
        student_id: str,
        progress_data: Dict
    ) -> bool:
        """
        Save student progress to storage
        
        Args:
            student_id: Student identifier
            progress_data: Progress data to save
            
        Returns:
            True if successful
        """
        try:
            file_path = self._get_student_file(student_id)
            
            # Add timestamp
            progress_data['last_updated'] = datetime.now().isoformat()
            
            with open(file_path, 'w') as f:
                json.dump(progress_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving progress: {e}")
            return False
    
    def load_progress(
        self,
        student_id: str
    ) -> Optional[Dict]:
        """
        Load student progress from storage
        
        Args:
            student_id: Student identifier
            
        Returns:
            Progress data or None if not found
        """
        try:
            file_path = self._get_student_file(student_id)
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"Error loading progress: {e}")
            return None
    
    def update_topic_score(
        self,
        student_id: str,
        topic: str,
        score: int,
        difficulty: str = "medium"
    ) -> bool:
        """
        Update score for a specific topic
        
        Args:
            student_id: Student identifier
            topic: Topic name
            score: Score (0-100)
            difficulty: Difficulty level
            
        Returns:
            True if successful
        """
        # Load existing progress
        progress = self.load_progress(student_id) or self._init_progress()
        
        # Update topic scores
        if 'topics' not in progress:
            progress['topics'] = {}
        
        if topic not in progress['topics']:
            progress['topics'][topic] = {
                'scores': [],
                'difficulties': [],
                'attempts': 0
            }
        
        progress['topics'][topic]['scores'].append(score)
        progress['topics'][topic]['difficulties'].append(difficulty)
        progress['topics'][topic]['attempts'] += 1
        progress['topics'][topic]['last_score'] = score
        progress['topics'][topic]['last_attempt'] = datetime.now().isoformat()
        
        # Calculate average
        scores = progress['topics'][topic]['scores']
        progress['topics'][topic]['average_score'] = sum(scores) / len(scores)
        
        return self.save_progress(student_id, progress)
    
    def get_topic_progress(
        self,
        student_id: str,
        topic: str
    ) -> Optional[Dict]:
        """
        Get progress for specific topic
        
        Args:
            student_id: Student identifier
            topic: Topic name
            
        Returns:
            Topic progress data or None
        """
        progress = self.load_progress(student_id)
        
        if not progress or 'topics' not in progress:
            return None
        
        return progress['topics'].get(topic)
    
    def get_all_topics(self, student_id: str) -> List[str]:
        """
        Get list of all topics student has worked on
        
        Args:
            student_id: Student identifier
            
        Returns:
            List of topic names
        """
        progress = self.load_progress(student_id)
        
        if not progress or 'topics' not in progress:
            return []
        
        return list(progress['topics'].keys())
    
    def get_weak_topics(
        self,
        student_id: str,
        threshold: float = 70.0
    ) -> List[Dict]:
        """
        Identify topics where student is struggling
        
        Args:
            student_id: Student identifier
            threshold: Score threshold for weak topics
            
        Returns:
            List of weak topics with details
        """
        progress = self.load_progress(student_id)
        
        if not progress or 'topics' not in progress:
            return []
        
        weak_topics = []
        
        for topic, data in progress['topics'].items():
            avg_score = data.get('average_score', 0)
            
            if avg_score < threshold:
                weak_topics.append({
                    'topic': topic,
                    'average_score': avg_score,
                    'attempts': data.get('attempts', 0),
                    'last_score': data.get('last_score', 0)
                })
        
        # Sort by lowest score first
        weak_topics.sort(key=lambda x: x['average_score'])
        
        return weak_topics
    
    def get_strong_topics(
        self,
        student_id: str,
        threshold: float = 85.0
    ) -> List[Dict]:
        """
        Identify topics where student excels
        
        Args:
            student_id: Student identifier
            threshold: Score threshold for strong topics
            
        Returns:
            List of strong topics
        """
        progress = self.load_progress(student_id)
        
        if not progress or 'topics' not in progress:
            return []
        
        strong_topics = []
        
        for topic, data in progress['topics'].items():
            avg_score = data.get('average_score', 0)
            
            if avg_score >= threshold:
                strong_topics.append({
                    'topic': topic,
                    'average_score': avg_score,
                    'attempts': data.get('attempts', 0)
                })
        
        # Sort by highest score first
        strong_topics.sort(key=lambda x: x['average_score'], reverse=True)
        
        return strong_topics
    
    def _init_progress(self) -> Dict:
        """Initialize new progress structure"""
        return {
            'topics': {},
            'created_at': datetime.now().isoformat(),
            'total_sessions': 0,
            'total_problems_solved': 0
        }
    
    def increment_session_count(self, student_id: str) -> bool:
        """Increment total session count"""
        progress = self.load_progress(student_id) or self._init_progress()
        progress['total_sessions'] = progress.get('total_sessions', 0) + 1
        return self.save_progress(student_id, progress)