"""
Progress Tracker Agent - Analyzes student learning progress
Generates insights and identifies knowledge gaps
"""

import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime
from google import genai
from google.genai import types


class ProgressTrackerAgent:
    """
    Specialized agent for tracking and analyzing student progress.
    Provides insights on strengths, weaknesses, and learning trajectory.
    """
    
    def __init__(self, client: genai.Client, memory_bank):
        """
        Initialize progress tracker agent
        
        Args:
            client: GenAI client
            memory_bank: Memory bank with student history
        """
        self.client = client
        self.memory_bank = memory_bank
        self.model_name = 'gemini-2.0-flash-exp'
        
    async def analyze_progress(self, student_id: str) -> str:
        """
        Analyze student's learning progress and generate report
        
        Args:
            student_id: Student identifier
            
        Returns:
            Progress report string
        """
        # Get student interaction history from memory
        history = self.memory_bank.get_interaction_history(student_id)
        profile = self.memory_bank.get_student_context(student_id)
        
        if not history:
            return """📊 PROGRESS REPORT

You're just getting started! I don't have enough data yet to analyze your progress.
Keep working with me, and I'll be able to provide detailed insights soon!

Tips for effective learning:
✓ Practice regularly
✓ Ask questions when confused
✓ Review challenging topics
✓ Test yourself with quizzes"""
        
        # Build analysis prompt
        prompt = f"""Analyze this student's learning progress and create a comprehensive report:

STUDENT PROFILE:
Level: {profile.get('level', 'intermediate')}
Learning Style: {profile.get('learning_style', 'visual')}
Strengths: {', '.join(profile.get('strengths', [])) or 'Not yet identified'}
Knowledge Gaps: {', '.join(profile.get('gaps', [])) or 'None identified'}
Recent Topics: {', '.join(profile.get('recent_topics', [])) or 'None'}

INTERACTION HISTORY (last {len(history)} sessions):
{self._format_history(history)}

Create a detailed progress report with:

1. OVERALL PROGRESS SUMMARY
   - General assessment of learning journey
   - Notable improvements
   - Engagement level

2. TOPICS MASTERED
   - List topics where student shows strong understanding
   - Specific achievements

3. AREAS FOR IMPROVEMENT
   - Topics needing more practice
   - Specific concepts to review
   - Recommended focus areas

4. LEARNING PATTERNS OBSERVED
   - Study habits
   - Question types asked
   - Engagement patterns

5. SPECIFIC RECOMMENDATIONS
   - Next topics to study
   - Study strategies
   - Practice suggestions

6. MOTIVATIONAL ENCOURAGEMENT
   - Celebrate progress
   - Encourage continued learning
   - Set positive tone

Make it personal, encouraging, and actionable. Use emojis where appropriate."""

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.6,
                    max_output_tokens=1200,
                )
            )
            
            report = f"""📊 PROGRESS REPORT - {datetime.now().strftime('%B %d, %Y')}
{'=' * 60}

{response.text}

{'=' * 60}
📈 Total Sessions: {len(history)}
🎯 Keep up the great work!

Want detailed analytics on a specific topic? Just ask!"""

            return report
            
        except Exception as e:
            return f"Error generating progress report: {e}"
    
    def _format_history(self, history: List[Dict]) -> str:
        """Format interaction history for analysis"""
        formatted = []
        
        # Get last 10 interactions for analysis
        recent_history = history[-10:] if len(history) > 10 else history
        
        for i, interaction in enumerate(recent_history, 1):
            topic = interaction.get('topic', 'General')
            intent = interaction.get('intent', 'unknown')
            timestamp = interaction.get('timestamp', 'N/A')
            
            formatted.append(
                f"Session {i}:\n"
                f"  Date: {timestamp}\n"
                f"  Topic: {topic}\n"
                f"  Intent: {intent}\n"
            )
        
        return "\n".join(formatted)
    
    async def identify_gaps(self, student_id: str) -> List[str]:
        """
        Identify specific knowledge gaps for targeted intervention
        
        Args:
            student_id: Student identifier
            
        Returns:
            List of identified knowledge gaps
        """
        history = self.memory_bank.get_interaction_history(student_id)
        
        if not history:
            return []
        
        prompt = f"""Analyze these student interactions and identify specific knowledge gaps:

{self._format_history(history)}

Identify 3-5 specific concepts or skills where the student shows difficulty.

Return ONLY a JSON array of strings, e.g.:
["quadratic formula", "photosynthesis steps", "subject-verb agreement"]

Focus on:
- Recurring questions about same topics
- Difficulty patterns
- Misconceptions
- Topics they avoid

Return only the JSON array, no other text."""

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=300,
                    response_mime_type="application/json"
                )
            )
            
            gaps = json.loads(response.text)
            
            # Validate it's a list
            if isinstance(gaps, list):
                # Update memory bank with identified gaps
                self.memory_bank.update_student_gaps(student_id, gaps)
                return gaps
            else:
                return []
            
        except Exception as e:
            print(f"Error identifying gaps: {e}")
            return []
    
    async def identify_strengths(self, student_id: str) -> List[str]:
        """
        Identify student's learning strengths
        
        Args:
            student_id: Student identifier
            
        Returns:
            List of identified strengths
        """
        history = self.memory_bank.get_interaction_history(student_id)
        
        if not history:
            return []
        
        prompt = f"""Analyze these student interactions and identify their learning strengths:

{self._format_history(history)}

Identify 3-5 specific strengths, skills, or topics they excel at.

Return ONLY a JSON array of strings, e.g.:
["problem solving", "creative thinking", "algebra", "science concepts"]

Focus on:
- Topics they engage with confidently
- Quick understanding
- Advanced questions
- Consistent performance

Return only the JSON array, no other text."""

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=300,
                    response_mime_type="application/json"
                )
            )
            
            strengths = json.loads(response.text)
            
            if isinstance(strengths, list):
                # Update profile with strengths
                for strength in strengths:
                    self.memory_bank.add_strength(student_id, strength)
                return strengths
            else:
                return []
            
        except Exception as e:
            print(f"Error identifying strengths: {e}")
            return []
    
    async def generate_study_plan(
        self,
        student_id: str,
        target_topics: Optional[List[str]] = None,
        duration_days: int = 7
    ) -> str:
        """
        Generate personalized study plan
        
        Args:
            student_id: Student identifier
            target_topics: Specific topics to focus on (optional)
            duration_days: Study plan duration
            
        Returns:
            Formatted study plan
        """
        profile = self.memory_bank.get_student_context(student_id)
        gaps = profile.get('gaps', [])
        
        topics_to_cover = target_topics if target_topics else gaps[:5]
        
        if not topics_to_cover:
            topics_to_cover = ["Review fundamentals", "Explore new topics"]
        
        prompt = f"""Create a {duration_days}-day personalized study plan for this student:

STUDENT PROFILE:
Level: {profile.get('level', 'intermediate')}
Strengths: {', '.join(profile.get('strengths', [])) or 'To be discovered'}
Areas to improve: {', '.join(gaps) or 'General review'}

TOPICS TO COVER:
{', '.join(topics_to_cover)}

Create a day-by-day plan with:
- Daily learning objectives
- Specific topics/concepts to study
- Estimated time (realistic)
- Practice activities
- Review checkpoints

Make it achievable, motivating, and balanced."""

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1200,
                )
            )
            
            study_plan = f"""📅 PERSONALIZED {duration_days}-DAY STUDY PLAN
{'=' * 60}

{response.text}

{'=' * 60}
💡 Remember: Consistency is key! Even 20 minutes daily makes a difference.
"""
            return study_plan
            
        except Exception as e:
            return f"Error generating study plan: {e}"
    
    async def calculate_mastery_score(
        self,
        student_id: str,
        topic: str
    ) -> Dict:
        """
        Calculate mastery score for a specific topic
        
        Args:
            student_id: Student identifier
            topic: Topic to assess
            
        Returns:
            Mastery assessment dict
        """
        history = self.memory_bank.get_interaction_history(student_id)
        
        # Filter interactions related to this topic
        topic_interactions = [
            i for i in history 
            if topic.lower() in i.get('query', '').lower() or 
               topic.lower() in i.get('topic', '').lower()
        ]
        
        if not topic_interactions:
            return {
                "topic": topic,
                "mastery_level": "Not Assessed",
                "percentage": 0,
                "interactions": 0,
                "recommendation": f"Start learning about {topic} to build mastery!"
            }
        
        # Simple mastery calculation based on engagement
        num_interactions = len(topic_interactions)
        
        # More interactions generally indicate growing mastery
        if num_interactions >= 10:
            mastery_level = "Advanced"
            percentage = 85
        elif num_interactions >= 6:
            mastery_level = "Proficient"
            percentage = 70
        elif num_interactions >= 3:
            mastery_level = "Developing"
            percentage = 55
        else:
            mastery_level = "Beginner"
            percentage = 30
        
        return {
            "topic": topic,
            "mastery_level": mastery_level,
            "percentage": percentage,
            "interactions": num_interactions,
            "recommendation": self._get_mastery_recommendation(mastery_level, topic)
        }
    
    def _get_mastery_recommendation(self, level: str, topic: str) -> str:
        """Get recommendation based on mastery level"""
        recommendations = {
            "Advanced": f"Excellent mastery of {topic}! Consider teaching others or exploring advanced applications.",
            "Proficient": f"Strong understanding of {topic}. Practice with challenging problems to master it completely.",
            "Developing": f"Good progress on {topic}. Keep practicing and reviewing key concepts.",
            "Beginner": f"You're starting your journey with {topic}. Focus on fundamentals and don't rush.",
            "Not Assessed": f"Ready to learn {topic}? Let's start with the basics!"
        }
        return recommendations.get(level, "Keep learning!")