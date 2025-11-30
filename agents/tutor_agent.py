"""
Tutor Agent - Provides personalized Socratic-method tutoring
Uses LLM + Memory Bank for adaptive teaching
"""

import asyncio
from typing import Optional, Dict
from tools.error_utils import format_error
from google import genai
from google.genai import types


class TutorAgent:
    """
    Specialized agent for personalized tutoring.
    Uses Socratic method to guide students to answers.
    """
    
    def __init__(self, client: genai.Client, memory_bank):
        """
        Initialize tutor agent
        
        Args:
            client: GenAI client
            memory_bank: Memory bank for student context
        """
        self.client = client
        self.memory_bank = memory_bank
        self.model_name = 'gemini-2.0-flash-exp'
        
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        
        try:
            from tools.knowledge_base_tool import KnowledgeBaseTool
            self.knowledge_tool = KnowledgeBaseTool()
        except ImportError:
            self.knowledge_tool = None
            print("Warning: KnowledgeBaseTool not available")
        
    async def teach(
        self, 
        query: str, 
        student_id: str, 
        context: Optional[str] = None
    ) -> str:
        """
        Provide tutoring response using Socratic method
        
        Args:
            query: Student's question
            student_id: Student identifier
            context: Optional additional context
            
        Returns:
            Tutoring response
        """
        # Get student learning profile from memory
        student_profile = self.memory_bank.get_student_context(student_id)
        
        # Retrieve relevant knowledge if tool available
        knowledge = ""
        if self.knowledge_tool:
            try:
                knowledge = await self.knowledge_tool.retrieve(query)
            except Exception as e:
                print(f"Knowledge retrieval error: {e}")
                knowledge = "Using general knowledge."
        
        # Build personalized prompt
        prompt = self._build_prompt(
            query, 
            student_profile, 
            knowledge, 
            context
        )
        
        # Generate response
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,  # Balanced creativity for teaching
                    max_output_tokens=1000,
                )
            )
            
            return response.text
            
        except Exception as e:
            return f"I apologize, I'm having trouble processing that. {format_error(e)}"
    
    def _build_prompt(
        self,
        query: str,
        student_profile: Dict,
        knowledge: str,
        context: Optional[str]
    ) -> str:
        """Build personalized teaching prompt"""
        
        level = student_profile.get('level', 'intermediate')
        strengths = student_profile.get('strengths', [])
        gaps = student_profile.get('gaps', [])
        learning_style = student_profile.get('learning_style', 'visual')
        
        # Tutor system prompt
        system_prompt = """You are an expert educational tutor using the Socratic method.

Your teaching philosophy:
1. Guide students to discover answers themselves through questions
2. Build on what they already know
3. Use clear, age-appropriate language
4. Encourage critical thinking
5. Provide positive reinforcement
6. Break complex topics into manageable pieces

Teaching approach:
- Ask probing questions instead of giving direct answers
- Use real-world examples and analogies
- Check for understanding frequently
- Adjust difficulty based on student responses
- Celebrate progress and effort

Remember:
- Be patient and encouraging
- Never make students feel bad for not knowing
- Adapt explanations to their level
- Focus on understanding, not just memorization"""

        prompt = f"""{system_prompt}

STUDENT PROFILE:
- Learning Level: {level}
- Learning Style: {learning_style}
- Strengths: {', '.join(strengths) if strengths else 'Not yet assessed'}
- Knowledge Gaps: {', '.join(gaps) if gaps else 'None identified'}

RELEVANT KNOWLEDGE:
{knowledge}

{("ADDITIONAL CONTEXT: " + context) if context else ""}

STUDENT QUESTION:
{query}

Provide a helpful, encouraging response that guides the student toward understanding.
Use the Socratic method - ask questions that help them think through the problem.
Adapt your explanation to their level and learning style."""

        return prompt
    
    async def provide_hint(
        self,
        question: str,
        student_id: str,
        difficulty: str = "medium"
    ) -> str:
        """
        Provide a hint without giving away the answer
        
        Args:
            question: The problem/question
            student_id: Student identifier
            difficulty: easy, medium, hard
            
        Returns:
            Helpful hint
        """
        hint_levels = {
            "easy": "very direct hint that almost gives the answer",
            "medium": "balanced hint that guides thinking",
            "hard": "subtle hint that only provides direction"
        }
        
        prompt = f"""Provide a {hint_levels.get(difficulty, 'medium')} for this question:

{question}

The hint should:
- Not give away the complete answer
- Help the student think about the approach
- Be encouraging and positive

Hint:"""

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.6,
                    max_output_tokens=200,
                )
            )
            
            return f"💡 Hint: {response.text}"
            
        except Exception as e:
            return f"Here's a thought: Try breaking the problem into smaller steps. {format_error(e)}"
    
    async def check_understanding(
        self,
        topic: str,
        student_answer: str,
        student_id: str
    ) -> str:
        """
        Check student's understanding with follow-up questions
        
        Args:
            topic: Topic being discussed
            student_answer: Student's explanation or answer
            student_id: Student identifier
            
        Returns:
            Follow-up response
        """
        prompt = f"""A student is learning about: {topic}

They said: "{student_answer}"

Assess their understanding and provide:
1. Acknowledgment of what they got right
2. Gentle correction if needed
3. A follow-up question to deepen understanding
4. Encouragement

Be supportive and use the Socratic method."""

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                )
            )
            
            return response.text
            
        except Exception as e:
            return "That's an interesting thought! Can you tell me more about why you think that?"