"""
Memory Bank - Long-term memory storage for student learning
Implements ADK memory concepts for persistent student context
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict
from pathlib import Path


class MemoryBank:
    """
    Long-term memory system for storing student learning history.
    Tracks: interactions, topics, strengths, weaknesses, preferences.
    
    Implements ADK Memory Bank concept for context persistence.
    """
    
    def __init__(self, storage_dir: str = "data/memory"):
        """
        Initialize memory bank
        
        Args:
            storage_dir: Directory for memory storage
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for fast access
        self.cache = {}
        
    def _get_memory_file(self, student_id: str) -> Path:
        """Get file path for student's memory"""
        return self.storage_dir / f"memory_{student_id}.json"
    
    def _load_memory(self, student_id: str) -> Dict:
        """Load student memory from storage"""
        # Check cache first
        if student_id in self.cache:
            return self.cache[student_id]
        
        file_path = self._get_memory_file(student_id)
        
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    memory = json.load(f)
                    self.cache[student_id] = memory
                    return memory
            except Exception as e:
                print(f"Error loading memory: {e}")
        
        # Initialize new memory
        return self._init_memory(student_id)
    
    def _save_memory(self, student_id: str, memory: Dict) -> bool:
        """Save student memory to storage"""
        try:
            file_path = self._get_memory_file(student_id)
            
            with open(file_path, 'w') as f:
                json.dump(memory, f, indent=2)
            
            # Update cache
            self.cache[student_id] = memory
            return True
            
        except Exception as e:
            print(f"Error saving memory: {e}")
            return False
    
    def _init_memory(self, student_id: str) -> Dict:
        """Initialize new student memory structure"""
        memory = {
            "student_id": student_id,
            "created_at": datetime.now().isoformat(),
            "profile": {
                "level": "intermediate",  # beginner, intermediate, advanced
                "learning_style": "visual",  # visual, auditory, kinesthetic
                "strengths": [],
                "gaps": [],
                "interests": []
            },
            "interactions": [],
            "topics_studied": {},
            "performance_history": [],
            "preferences": {
                "explanation_detail": "medium",  # simple, medium, detailed
                "practice_difficulty": "medium"  # easy, medium, hard
            },
            "context_summary": ""
        }
        
        self._save_memory(student_id, memory)
        return memory
    
    def add_interaction(
        self,
        student_id: str,
        query: str,
        response: str,
        intent: str
    ):
        """
        Add new interaction to memory
        
        Args:
            student_id: Student identifier
            query: Student's query
            response: Agent's response
            intent: Determined intent of interaction
        """
        memory = self._load_memory(student_id)
        
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response_summary": response[:200],  # Store summary to save space
            "intent": intent,
            "topic": self._extract_topic(query)
        }
        
        memory["interactions"].append(interaction)
        
        # Keep only last 50 interactions for context compaction
        if len(memory["interactions"]) > 50:
            memory["interactions"] = memory["interactions"][-50:]
        
        # Update topics studied
        topic = interaction["topic"]
        if topic:
            if topic not in memory["topics_studied"]:
                memory["topics_studied"][topic] = {
                    "first_seen": datetime.now().isoformat(),
                    "count": 0
                }
            memory["topics_studied"][topic]["count"] += 1
            memory["topics_studied"][topic]["last_seen"] = datetime.now().isoformat()
        
        self._save_memory(student_id, memory)
    
    def get_student_context(self, student_id: str) -> Dict:
        """
        Get comprehensive student context for agent use.
        
        Returns:
            Context dict with profile, recent topics, strengths, gaps
        """
        memory = self._load_memory(student_id)
        
        # Get recent topics (last 5 interactions)
        recent_topics = [
            i["topic"] for i in memory["interactions"][-5:]
            if i.get("topic")
        ]
        
        return {
            "level": memory["profile"]["level"],
            "learning_style": memory["profile"]["learning_style"],
            "strengths": memory["profile"]["strengths"],
            "gaps": memory["profile"]["gaps"],
            "interests": memory["profile"]["interests"],
            "recent_topics": list(set(recent_topics)),  # Unique topics
            "total_interactions": len(memory["interactions"]),
            "preferences": memory["preferences"]
        }
    
    def get_interaction_history(
        self,
        student_id: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get interaction history for progress analysis
        
        Args:
            student_id: Student identifier
            limit: Maximum interactions to return
            
        Returns:
            List of recent interactions
        """
        memory = self._load_memory(student_id)
        return memory["interactions"][-limit:]
    
    def update_student_profile(
        self,
        student_id: str,
        **kwargs
    ):
        """
        Update student profile attributes
        
        Args:
            student_id: Student identifier
            **kwargs: Profile attributes to update (level, learning_style, etc.)
        """
        memory = self._load_memory(student_id)
        
        for key, value in kwargs.items():
            if key in memory["profile"]:
                memory["profile"][key] = value
        
        self._save_memory(student_id, memory)
    
    def add_strength(self, student_id: str, strength: str):
        """Add identified strength to student profile"""
        memory = self._load_memory(student_id)
        
        if strength not in memory["profile"]["strengths"]:
            memory["profile"]["strengths"].append(strength)
            self._save_memory(student_id, memory)
    
    def add_gap(self, student_id: str, gap: str):
        """Add identified knowledge gap to student profile"""
        memory = self._load_memory(student_id)
        
        if gap not in memory["profile"]["gaps"]:
            memory["profile"]["gaps"].append(gap)
            self._save_memory(student_id, memory)
    
    def update_student_gaps(self, student_id: str, gaps: List[str]):
        """Update complete list of knowledge gaps"""
        memory = self._load_memory(student_id)
        memory["profile"]["gaps"] = gaps
        self._save_memory(student_id, memory)
    
    def get_context_summary(self, student_id: str) -> str:
        """
        Get compact context summary for LLM prompts.
        Implements context compaction strategy.
        
        Returns:
            Compact string summary of student context
        """
        context = self.get_student_context(student_id)
        
        summary = f"""Student Level: {context['level']}
Learning Style: {context['learning_style']}
Recent Topics: {', '.join(context['recent_topics'][:3]) if context['recent_topics'] else 'None'}
Strengths: {', '.join(context['strengths'][:3]) if context['strengths'] else 'Not yet identified'}
Areas for Growth: {', '.join(context['gaps'][:3]) if context['gaps'] else 'None identified'}"""
        
        return summary
    
    def _extract_topic(self, query: str) -> Optional[str]:
        """Extract main topic from query using simple keyword matching"""
        query_lower = query.lower()
        
        # Topic keywords (expand as needed)
        topics = {
            "math": ["algebra", "geometry", "calculus", "equation", "formula", "math"],
            "science": ["biology", "chemistry", "physics", "photosynthesis", "atom", "force"],
            "english": ["grammar", "writing", "essay", "literature", "reading"],
            "history": ["history", "war", "ancient", "civilization"],
            "computer": ["programming", "code", "algorithm", "python", "java"]
        }
        
        for topic, keywords in topics.items():
            if any(keyword in query_lower for keyword in keywords):
                return topic
        
        return None
    
    def compact_old_memories(self, student_id: str, threshold: int = 100):
        """
        Compact old memories to save space (context engineering).
        Summarizes old interactions instead of storing full details.
        
        Args:
            student_id: Student identifier
            threshold: Number of interactions before compaction
        """
        memory = self._load_memory(student_id)
        
        if len(memory["interactions"]) < threshold:
            return  # No compaction needed
        
        # Keep recent 50, summarize older ones
        recent = memory["interactions"][-50:]
        old = memory["interactions"][:-50]
        
        # Create summary of old interactions
        topic_counts = defaultdict(int)
        for interaction in old:
            topic = interaction.get("topic")
            if topic:
                topic_counts[topic] += 1
        
        summary = f"Earlier sessions covered: {dict(topic_counts)}"
        memory["context_summary"] = summary
        memory["interactions"] = recent
        
        self._save_memory(student_id, memory)