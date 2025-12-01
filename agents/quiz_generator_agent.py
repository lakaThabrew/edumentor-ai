"""
Quiz Generator Agent - Creates adaptive practice problems
Generates quizzes based on student level and topic
"""

import asyncio
import json
from typing import List, Dict, Optional
from tools.error_utils import format_error
from tools.genai_utils import async_chat
from google import genai
from google.genai import types


class QuizGeneratorAgent:
    """
    Specialized agent for generating practice problems and quizzes.
    Adapts difficulty based on student performance.
    """
    
    def __init__(self, client: genai.Client):
        """
        Initialize quiz generator agent
        
        Args:
            client: GenAI client
        """
        self.client = client
        self.model_name = 'gemini-2.0-flash'
        
    async def generate_quiz(
        self,
        topic: str,
        student_id: str,
        num_questions: int = 5,
        difficulty: str = "medium"
    ) -> str:
        """
        Generate practice quiz for given topic
        
        Args:
            topic: Subject/topic for quiz
            student_id: Student identifier
            num_questions: Number of questions to generate
            difficulty: easy, medium, or hard
            
        Returns:
            Formatted quiz string
        """
        
        system_prompt = """You are a skilled quiz and assessment creator.

Your role:
- Generate high-quality, educational practice problems
- Vary question types and difficulty appropriately
- Ensure questions test understanding, not just memorization
- Provide clear, unambiguous questions
- Include a detailed answer key with explanations

Question Design Principles:
1. Questions should be clear and specific
2. Multiple choice options should all be plausible
3. Short answer questions should have clear success criteria
4. Problem-solving questions should show step-by-step solutions

Always include:
- Clear question text
- For MC: 4 options with one clearly correct answer
- For problems: Expected solution method
- Difficulty indicator
- Learning objective being tested"""

        prompt = f"""{system_prompt}

TOPIC: {topic}
DIFFICULTY: {difficulty}
NUMBER OF QUESTIONS: {num_questions}

Generate a mix of:
- Multiple choice questions (50%)
- Short answer questions (30%)
- Problem-solving questions (20%)

Format each question clearly with:
- Question number
- Question text
- Options (for MC)
- Point value

At the end, provide an ANSWER KEY with:
- Correct answers
- Brief explanations
- Key concepts tested

Make it educational and engaging!"""

        try:
            quiz_text = await async_chat(
                self.client,
                self.model_name,
                "",
                prompt,
                temperature=0.8,
                max_output_tokens=1500,
            )
            
            # Format nicely
            formatted_quiz = f"""
📝 PRACTICE QUIZ: {topic}
Difficulty: {difficulty.upper()}
{'=' * 60}

{quiz_text}

{'=' * 60}
💡 Take your time and show your work!
"""
            return formatted_quiz
            
        except Exception as e:
            return f"Error generating quiz: {format_error(e)}"
    
    async def generate_single_question(
        self,
        topic: str,
        question_type: str = "multiple_choice",
        difficulty: str = "medium"
    ) -> Dict:
        """
        Generate a single question
        
        Args:
            topic: Subject/topic
            question_type: multiple_choice, short_answer, problem_solving
            difficulty: easy, medium, hard
            
        Returns:
            Question dict with question, options, answer
        """
        prompt = f"""Generate ONE {question_type} question about: {topic}
Difficulty: {difficulty}

Return as JSON:
{{
  "question": "question text",
  "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
  "correct_answer": "answer",
  "explanation": "why this is correct",
  "difficulty": "{difficulty}",
  "topic": "{topic}"
}}

For multiple_choice: include 4 options
For short_answer: omit options field
For problem_solving: include step-by-step solution in explanation"""

        try:
            response_text = await async_chat(
                self.client,
                self.model_name,
                "",
                prompt,
                temperature=0.8,
                max_output_tokens=500,
            )
            
            question_data = json.loads(response_text)
            return question_data
            
        except Exception as e:
            print(f"Error generating single question: {e}")
            return {
                "question": f"Error generating question: {format_error(e)}",
                "error": True
            }
    
    async def evaluate_answer(
        self,
        question: str,
        student_answer: str,
        correct_answer: str
    ) -> Dict:
        """
        Evaluate student's answer and provide feedback
        
        Args:
            question: The quiz question
            student_answer: Student's response
            correct_answer: Correct answer
            
        Returns:
            Evaluation dict with score and feedback
        """
        eval_prompt = f"""Evaluate this student answer:

QUESTION: {question}

STUDENT ANSWER: {student_answer}

CORRECT ANSWER: {correct_answer}

Provide evaluation as JSON:
{{
  "score": <number 0-100>,
  "feedback": "<positive, constructive feedback>",
  "hint": "<helpful hint if not fully correct>",
  "is_correct": <true/false>
}}

Be encouraging and educational in your feedback."""

        try:
            response_text = await async_chat(
                self.client,
                self.model_name,
                "",
                eval_prompt,
                temperature=0.3,
                max_output_tokens=500,
            )
            
            evaluation = json.loads(response_text)
            return evaluation
            
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return {
                "score": 0,
                "feedback": format_error(e),
                "hint": "Please try again",
                "is_correct": False
            }
    
    async def generate_adaptive_quiz(
        self,
        topic: str,
        student_id: str,
        previous_scores: List[int]
    ) -> str:
        """
        Generate quiz that adapts to student performance
        
        Args:
            topic: Subject/topic
            student_id: Student identifier
            previous_scores: List of recent scores to adapt difficulty
            
        Returns:
            Adaptive quiz
        """
        # Calculate average score to determine difficulty
        if previous_scores:
            avg_score = sum(previous_scores) / len(previous_scores)
            if avg_score >= 85:
                difficulty = "hard"
                message = "Great job! Here's a challenging quiz to push your skills further."
            elif avg_score >= 65:
                difficulty = "medium"
                message = "You're doing well! Here's a balanced quiz to continue your progress."
            else:
                difficulty = "easy"
                message = "Let's build your confidence with some fundamental questions."
        else:
            difficulty = "medium"
            message = "Starting with a balanced quiz to assess your level."
        
        # Generate quiz with adapted difficulty
        quiz = await self.generate_quiz(
            topic=topic,
            student_id=student_id,
            num_questions=5,
            difficulty=difficulty
        )
        
        adaptive_note = f"\n📊 {message}\nDifficulty: {difficulty.upper()}\n\n"
        
        return adaptive_note + quiz
    
    async def generate_practice_set(
        self,
        topics: List[str],
        questions_per_topic: int = 3
    ) -> str:
        """
        Generate practice set covering multiple topics
        
        Args:
            topics: List of topics to cover
            questions_per_topic: Number of questions per topic
            
        Returns:
            Comprehensive practice set
        """
        practice_set = "📚 COMPREHENSIVE PRACTICE SET\n"
        practice_set += "=" * 60 + "\n\n"
        
        for i, topic in enumerate(topics, 1):
            practice_set += f"\n--- SECTION {i}: {topic.upper()} ---\n\n"
            
            try:
                quiz = await self.generate_quiz(
                    topic=topic,
                    student_id="practice",
                    num_questions=questions_per_topic,
                    difficulty="medium"
                )
                practice_set += quiz + "\n"
            except Exception as e:
                practice_set += f"Error generating questions for {topic}: {format_error(e)}\n\n"
        
        return practice_set
    
    async def create_flashcards(
        self,
        topic: str,
        num_cards: int = 10
    ) -> List[Dict]:
        """
        Create flashcards for memorization
        
        Args:
            topic: Subject/topic
            num_cards: Number of flashcards
            
        Returns:
            List of flashcard dicts
        """
        prompt = f"""Create {num_cards} educational flashcards about: {topic}

Each flashcard should test key concepts, definitions, or facts.

Return as JSON array:
[
  {{
    "front": "question or term",
    "back": "answer or definition",
    "hint": "optional memory aid or mnemonic"
  }}
]

Make them educational, clear, and helpful for memorization."""

        try:
            response_text = await async_chat(
                self.client,
                self.model_name,
                "",
                prompt,
                temperature=0.7,
                max_output_tokens=1500,
            )
            
            flashcards = json.loads(response_text)
            return flashcards
            
        except Exception as e:
            print(f"Error creating flashcards: {e}")
            return [{
                "front": "Error",
                "back": f"Error creating flashcards: {format_error(e)}",
                "hint": ""
            }]
    
    async def generate_word_problems(
        self,
        topic: str,
        num_problems: int = 3,
        difficulty: str = "medium"
    ) -> str:
        """
        Generate word problems for applied learning
        
        Args:
            topic: Mathematical or science topic
            num_problems: Number of word problems
            difficulty: easy, medium, hard
            
        Returns:
            Formatted word problems with solutions
        """
        prompt = f"""Generate {num_problems} word problems about: {topic}
Difficulty: {difficulty}

Each word problem should:
1. Have a real-world scenario
2. Require understanding of {topic}
3. Have clear numerical or conceptual solution
4. Be appropriate for {difficulty} level

Format:
Problem 1:
[scenario and question]

Problem 2:
[scenario and question]

...

SOLUTIONS:
Problem 1: [step-by-step solution]
Problem 2: [step-by-step solution]
..."""

        try:
            response_text = await async_chat(
                self.client,
                self.model_name,
                "",
                prompt,
                temperature=0.8,
                max_output_tokens=1200,
            )
            
            word_problems = f"""
📐 WORD PROBLEMS: {topic}
Difficulty: {difficulty.upper()}
{'=' * 60}

{response_text}

{'=' * 60}
💡 Show your work and explain your reasoning!
"""
            return word_problems
            
        except Exception as e:
            return f"Error generating word problems: {e}"
    
    async def generate_true_false_quiz(
        self,
        topic: str,
        num_questions: int = 10
    ) -> str:
        """
        Generate true/false quiz for quick assessment
        
        Args:
            topic: Subject/topic
            num_questions: Number of T/F questions
            
        Returns:
            Formatted T/F quiz
        """
        prompt = f"""Generate {num_questions} True/False questions about: {topic}

Each question should:
- Test understanding of key concepts
- Be clearly true or false (no ambiguity)
- Include brief explanation in answer key

Format:
1. [Statement] - T/F
2. [Statement] - T/F
...

ANSWER KEY:
1. [True/False] - [Brief explanation]
2. [True/False] - [Brief explanation]
..."""

        try:
            response_text = await async_chat(
                self.client,
                self.model_name,
                "",
                prompt,
                temperature=0.7,
                max_output_tokens=1000,
            )
            
            tf_quiz = f"""
✓✗ TRUE/FALSE QUIZ: {topic}
{'=' * 60}

{response_text}

{'=' * 60}
"""
            return tf_quiz
        except Exception as e:
            return f"Error generating T/F quiz: {e}"