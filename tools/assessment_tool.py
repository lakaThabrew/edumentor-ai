"""
Assessment Tool - Custom tool for evaluating student responses
Provides detailed feedback and scoring
"""

import asyncio
from typing import Dict, List, Optional
from enum import Enum


class DifficultyLevel(Enum):
    """Difficulty levels for assessment"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionType(Enum):
    """Types of questions that can be assessed"""
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    PROBLEM_SOLVING = "problem_solving"
    TRUE_FALSE = "true_false"
    ESSAY = "essay"


class AssessmentTool:
    """
    Custom tool for assessing student work and providing feedback.
    Can be used by quiz generator and progress tracker agents.
    """
    
    def __init__(self):
        """Initialize assessment tool"""
        self.rubrics = self._load_rubrics()
        
    def _load_rubrics(self) -> Dict:
        """Load assessment rubrics for different question types"""
        return {
            "multiple_choice": {
                "correct": 100,
                "incorrect": 0
            },
            "true_false": {
                "correct": 100,
                "incorrect": 0
            },
            "short_answer": {
                "excellent": 100,
                "good": 80,
                "partial": 60,
                "poor": 30,
                "incorrect": 0
            },
            "problem_solving": {
                "correct_answer": 50,
                "correct_method": 30,
                "clear_explanation": 20
            },
            "essay": {
                "thesis": 20,
                "supporting_evidence": 30,
                "organization": 25,
                "grammar": 15,
                "conclusion": 10
            }
        }
    
    async def evaluate_multiple_choice(
        self,
        student_answer: str,
        correct_answer: str
    ) -> Dict:
        """
        Evaluate multiple choice answer
        
        Args:
            student_answer: Student's selected option
            correct_answer: Correct option
            
        Returns:
            Evaluation dict with score and feedback
        """
        # Normalize answers (remove whitespace, make lowercase)
        student_clean = student_answer.strip().lower()
        correct_clean = correct_answer.strip().lower()
        
        # Check if correct
        is_correct = student_clean == correct_clean
        
        return {
            "score": 100 if is_correct else 0,
            "correct": is_correct,
            "feedback": "Correct! Well done. ✓" if is_correct else 
                       f"Not quite. The correct answer is {correct_answer}.",
            "suggestion": "" if is_correct else 
                         "Review the concept and try to understand why this is the correct answer.",
            "question_type": "multiple_choice"
        }
    
    async def evaluate_true_false(
        self,
        student_answer: str,
        correct_answer: str
    ) -> Dict:
        """
        Evaluate true/false answer
        
        Args:
            student_answer: Student's answer (true/false)
            correct_answer: Correct answer (true/false)
            
        Returns:
            Evaluation dict
        """
        # Normalize to boolean
        student_bool = student_answer.strip().lower() in ['true', 't', 'yes', '1']
        correct_bool = correct_answer.strip().lower() in ['true', 't', 'yes', '1']
        
        is_correct = student_bool == correct_bool
        
        return {
            "score": 100 if is_correct else 0,
            "correct": is_correct,
            "feedback": "Correct!" if is_correct else "Incorrect.",
            "suggestion": "" if is_correct else 
                         "Think about the key concepts involved in this statement.",
            "question_type": "true_false"
        }
    
    async def evaluate_open_ended(
        self,
        student_answer: str,
        reference_answer: str,
        key_concepts: List[str]
    ) -> Dict:
        """
        Evaluate open-ended answer using key concept matching
        
        Args:
            student_answer: Student's response
            reference_answer: Reference answer
            key_concepts: List of key concepts that should be mentioned
            
        Returns:
            Evaluation dict
        """
        # Simulate evaluation delay (in real system, would use LLM)
        await asyncio.sleep(0.1)
        
        if not student_answer or not student_answer.strip():
            return {
                "score": 0,
                "quality": "no_answer",
                "concepts_found": 0,
                "concepts_total": len(key_concepts),
                "feedback": "No answer provided.",
                "suggestion": "Please provide an answer to receive feedback.",
                "question_type": "open_ended"
            }
        
        student_lower = student_answer.lower()
        concepts_found = sum(1 for concept in key_concepts 
                           if concept.lower() in student_lower)
        
        concept_ratio = concepts_found / len(key_concepts) if key_concepts else 0
        
        # Calculate score
        if concept_ratio >= 0.8:
            score = 100
            quality = "excellent"
        elif concept_ratio >= 0.6:
            score = 80
            quality = "good"
        elif concept_ratio >= 0.4:
            score = 60
            quality = "partial"
        elif concept_ratio >= 0.2:
            score = 30
            quality = "poor"
        else:
            score = 0
            quality = "incorrect"
        
        # Generate feedback
        missing_concepts = [c for c in key_concepts 
                          if c.lower() not in student_lower]
        
        feedback = self._generate_feedback(quality, concepts_found, len(key_concepts))
        
        suggestion = ""
        if missing_concepts:
            num_to_show = min(2, len(missing_concepts))
            suggestion = f"Consider including: {', '.join(missing_concepts[:num_to_show])}"
        
        return {
            "score": score,
            "quality": quality,
            "concepts_found": concepts_found,
            "concepts_total": len(key_concepts),
            "feedback": feedback,
            "suggestion": suggestion,
            "missing_concepts": missing_concepts,
            "question_type": "open_ended"
        }
    
    def _generate_feedback(
        self,
        quality: str,
        found: int,
        total: int
    ) -> str:
        """Generate contextual feedback based on quality"""
        feedback_map = {
            "excellent": f"Excellent work! You covered {found}/{total} key concepts thoroughly. 🌟",
            "good": f"Good job! You covered {found}/{total} key concepts. A few more details would make it perfect. 👍",
            "partial": f"You're on the right track with {found}/{total} key concepts, but there's room for improvement. 📚",
            "poor": f"You mentioned {found}/{total} key concepts. Review the material and try to include more key points. 📖",
            "incorrect": "This answer needs significant improvement. Let's review the concept together. 🤔",
            "no_answer": "No answer provided. Please attempt the question to receive feedback."
        }
        return feedback_map.get(quality, "Answer evaluated.")
    
    async def evaluate_problem_solving(
        self,
        student_answer: str,
        correct_answer: str,
        solution_steps: List[str]
    ) -> Dict:
        """
        Evaluate problem-solving answer
        
        Args:
            student_answer: Student's solution
            correct_answer: Correct final answer
            solution_steps: Expected solution steps
            
        Returns:
            Evaluation dict
        """
        await asyncio.sleep(0.1)
        
        student_lower = student_answer.lower()
        correct_lower = str(correct_answer).lower()
        
        # Check if final answer is present
        has_correct_answer = correct_lower in student_lower
        
        # Check for solution steps
        steps_shown = sum(1 for step in solution_steps 
                         if any(word in student_lower 
                               for word in step.lower().split()))
        
        steps_ratio = steps_shown / len(solution_steps) if solution_steps else 0
        
        # Calculate component scores
        answer_score = 50 if has_correct_answer else 0
        method_score = int(30 * steps_ratio)
        
        # Check for explanation/work shown
        has_explanation = len(student_answer.split()) > 10  # Basic heuristic
        explanation_score = 20 if has_explanation else 0
        
        total_score = answer_score + method_score + explanation_score
        
        feedback_parts = []
        if has_correct_answer:
            feedback_parts.append("✓ Correct final answer")
        else:
            feedback_parts.append("✗ Final answer needs correction")
        
        if steps_ratio >= 0.7:
            feedback_parts.append("✓ Good solution method")
        else:
            feedback_parts.append("• Show more steps in your work")
        
        if has_explanation:
            feedback_parts.append("✓ Work shown clearly")
        else:
            feedback_parts.append("• Explain your reasoning more")
        
        return {
            "score": total_score,
            "answer_correct": has_correct_answer,
            "steps_shown": steps_shown,
            "steps_total": len(solution_steps),
            "feedback": "\n".join(feedback_parts),
            "suggestion": "Show all your work step-by-step and explain your reasoning." if total_score < 80 else "",
            "question_type": "problem_solving"
        }
    
    async def calculate_mastery(
        self,
        scores: List[int],
        difficulty_levels: List[DifficultyLevel]
    ) -> Dict:
        """
        Calculate student's mastery level for a topic
        
        Args:
            scores: List of scores (0-100)
            difficulty_levels: Corresponding difficulty levels
            
        Returns:
            Mastery analysis
        """
        if not scores:
            return {
                "mastery_level": "Not Assessed",
                "percentage": 0,
                "recommendation": "Complete some practice problems to assess mastery.",
                "problems_solved": 0
            }
        
        # Weight scores by difficulty
        weights = {
            DifficultyLevel.EASY: 0.5,
            DifficultyLevel.MEDIUM: 1.0,
            DifficultyLevel.HARD: 1.5
        }
        
        weighted_sum = sum(score * weights.get(level, 1.0) 
                          for score, level in zip(scores, difficulty_levels))
        
        total_weight = sum(weights.get(level, 1.0) for level in difficulty_levels)
        
        mastery_percentage = (weighted_sum / total_weight) if total_weight > 0 else 0
        
        # Determine mastery level
        if mastery_percentage >= 90:
            level = "Mastered"
            recommendation = "Excellent! Ready for advanced topics. 🎓"
        elif mastery_percentage >= 75:
            level = "Proficient"
            recommendation = "Great progress! A bit more practice will solidify your understanding. 📈"
        elif mastery_percentage >= 60:
            level = "Developing"
            recommendation = "You're getting there. Focus on the challenging areas. 📚"
        elif mastery_percentage >= 40:
            level = "Emerging"
            recommendation = "Keep practicing. Consider reviewing the basics. 📖"
        else:
            level = "Beginning"
            recommendation = "Let's work together to build your foundation in this topic. 🌱"
        
        return {
            "mastery_level": level,
            "percentage": round(mastery_percentage, 1),
            "recommendation": recommendation,
            "problems_solved": len(scores)
        }
    
    async def provide_hints(
        self,
        question: str,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    ) -> List[str]:
        """
        Generate hints for a question without giving away the answer
        
        Args:
            question: The question text
            difficulty: Difficulty level determines hint strength
            
        Returns:
            List of progressive hints
        """
        # This would ideally use an LLM, but here's a simple implementation
        hints = []
        
        if difficulty == DifficultyLevel.EASY:
            hints.append("Think about the key concept being tested.")
            hints.append("Try breaking the problem into smaller parts.")
            hints.append("The answer involves applying what you just learned.")
        elif difficulty == DifficultyLevel.MEDIUM:
            hints.append("Consider what information you're given.")
            hints.append("What formula or concept applies here?")
            hints.append("Try working backwards from what you know.")
        else:  # HARD
            hints.append("This requires combining multiple concepts.")
            hints.append("Look for patterns or relationships.")
            hints.append("Consider edge cases or special conditions.")
        
        return hints
    
    def get_rubric(self, question_type: str) -> Dict:
        """
        Get rubric for a specific question type
        
        Args:
            question_type: Type of question
            
        Returns:
            Rubric dict
        """
        return self.rubrics.get(question_type, {})
    
    async def batch_evaluate(
        self,
        evaluations: List[Dict]
    ) -> Dict:
        """
        Evaluate multiple answers at once
        
        Args:
            evaluations: List of dicts with question info and answers
            
        Returns:
            Batch evaluation results
        """
        results = []
        
        for eval_item in evaluations:
            q_type = eval_item.get('type', 'multiple_choice')
            student_ans = eval_item.get('student_answer', '')
            correct_ans = eval_item.get('correct_answer', '')
            
            if q_type == 'multiple_choice':
                result = await self.evaluate_multiple_choice(student_ans, correct_ans)
            elif q_type == 'true_false':
                result = await self.evaluate_true_false(student_ans, correct_ans)
            else:
                key_concepts = eval_item.get('key_concepts', [])
                result = await self.evaluate_open_ended(
                    student_ans, 
                    correct_ans, 
                    key_concepts
                )
            
            results.append(result)
        
        # Calculate overall statistics
        total_score = sum(r['score'] for r in results)
        avg_score = total_score / len(results) if results else 0
        
        return {
            "individual_results": results,
            "total_questions": len(results),
            "average_score": round(avg_score, 1),
            "total_score": total_score,
            "max_possible": len(results) * 100
        }