"""
Concept Explainer Agent - Creates visual, step-by-step explanations
Breaks down complex concepts into digestible pieces
"""

import asyncio
from typing import Optional, List
from tools.error_utils import format_error
from tools.genai_utils import async_chat
from google import genai
from google.genai import types


class ConceptExplainerAgent:
    """
    Specialized agent for explaining complex concepts.
    Uses analogies, examples, and step-by-step breakdowns.
    """
    
    def __init__(self, client: genai.Client):
        """
        Initialize concept explainer agent
        
        Args:
            client: GenAI client
        """
        self.client = client
        self.model_name = 'models/gemini-1.5-pro'
        
    async def explain(
        self,
        concept: str,
        student_id: str,
        detail_level: str = "medium"
    ) -> str:
        """
        Generate detailed concept explanation
        
        Args:
            concept: Concept to explain
            student_id: Student identifier
            detail_level: simple, medium, or detailed
            
        Returns:
            Structured explanation
        """
        
        system_prompt = """You are a master at explaining complex concepts simply.

Your explanation strategy:
1. Start with a simple, relatable definition (ELI5)
2. Use a real-world analogy to build intuition
3. Break down the concept step-by-step
4. Provide visual descriptions or mental models
5. Address common misconceptions
6. Give a practice example

Explanation Principles:
- Use everyday language first, technical terms later
- Build from familiar to unfamiliar
- Use concrete examples before abstract concepts
- Draw connections to things students already know
- Make it memorable and engaging

Remember:
- Clarity over completeness
- Understanding over technical accuracy
- Engagement over formality"""

        detail_instructions = {
            "simple": "Keep it very simple, use basic language, suitable for beginners or young students.",
            "medium": "Balance simplicity with accuracy, suitable for most students.",
            "detailed": "Provide comprehensive explanation with technical details, suitable for advanced students."
        }

        prompt = f"""{system_prompt}

DETAIL LEVEL: {detail_level}
Instruction: {detail_instructions.get(detail_level, detail_instructions['medium'])}

CONCEPT TO EXPLAIN: {concept}

Provide a comprehensive explanation with these sections:

1. 🎯 SIMPLE DEFINITION (ELI5 style)
   Explain it like the student is 10 years old

2. 🌟 REAL-WORLD ANALOGY
   Compare it to something from everyday life

3. 📝 STEP-BY-STEP BREAKDOWN
   Break down the concept into digestible pieces

4. 👁️ VISUAL DESCRIPTION
   Help them picture it or create a mental model

5. ⚠️ COMMON MISCONCEPTIONS
   What do people often get wrong?

6. 💪 PRACTICE EXAMPLE
   A simple example to apply the concept

Make it engaging, clear, and easy to understand!"""

        try:
            response_text = await async_chat(
                self.client,
                self.model_name,
                system_prompt,
                prompt,
                temperature=0.7,
                max_output_tokens=1200,
            )

            explanation = f"""
🔍 CONCEPT EXPLANATION: {concept}
{'=' * 60}

{response_text}

{'=' * 60}
💡 Need more help? Feel free to ask follow-up questions!
"""
            return explanation
        except Exception as e:
            return f"Error explaining concept: {format_error(e)}"
    
    async def create_analogy(
        self,
        concept: str,
        familiar_domain: Optional[str] = None
    ) -> str:
        """
        Create a helpful analogy for difficult concepts
        
        Args:
            concept: Concept to explain
            familiar_domain: Optional domain to base analogy on (e.g., "cooking", "sports")
            
        Returns:
            Analogy explanation
        """
        domain_hint = f"using {familiar_domain}" if familiar_domain else "using everyday experiences"
        
        prompt = f"""Create a clear, memorable analogy to explain: {concept}

{domain_hint}

The analogy should:
- Use everyday experiences or common knowledge
- Be accurate to the core concept
- Be easy to visualize
- Help build intuition
- Make the concept memorable

Provide:
1. The analogy itself
2. How it maps to the actual concept
3. Where the analogy breaks down (limitations)

Make it creative and helpful!"""

        try:
            response_text = await async_chat(
                self.client,
                self.model_name,
                "",
                prompt,
                temperature=0.8,
                max_output_tokens=500,
            )

            return f"🌟 ANALOGY:\n\n{response_text}"
        except Exception as e:
            return f"Error creating analogy: {format_error(e)}"
    
    async def break_down_steps(self, process: str) -> str:
        """
        Break down a complex process into clear steps
        
        Args:
            process: Process or procedure to break down
            
        Returns:
            Step-by-step breakdown
        """
        prompt = f"""Break down this process into clear, numbered steps: {process}

For each step:
- Explain WHAT to do (the action)
- Explain WHY it's done (the reason)
- Provide a quick tip or example

Number each step clearly and keep explanations concise but complete.
Make it actionable and easy to follow."""

        try:
            response_text = await async_chat(
                self.client,
                self.model_name,
                "",
                prompt,
                temperature=0.5,
                max_output_tokens=800,
            )

            return f"📋 STEP-BY-STEP GUIDE: {process}\n\n{response_text}"
        except Exception as e:
            return f"Error breaking down steps: {format_error(e)}"
    
    async def explain_with_examples(
        self,
        concept: str,
        num_examples: int = 3
    ) -> str:
        """
        Explain concept through multiple examples
        
        Args:
            concept: Concept to explain
            num_examples: Number of examples to provide
            
        Returns:
            Explanation with examples
        """
        prompt = f"""Explain "{concept}" through {num_examples} clear examples.

For each example:
1. Describe the scenario
2. Show how the concept applies
3. Explain what we can learn from it

Progress from simple to more complex examples.
Make each example distinct and illustrative."""

        try:
            response_text = await async_chat(
                self.client,
                self.model_name,
                "",
                prompt,
                temperature=0.7,
                max_output_tokens=1000,
            )

            return f"""
📚 LEARNING THROUGH EXAMPLES: {concept}
{'=' * 60}

{response_text}

{'=' * 60}
"""
        except Exception as e:
            return f"Error generating examples: {format_error(e)}"
    
    async def create_visual_description(
        self,
        concept: str
    ) -> str:
        """
        Create a visual description to help students picture the concept
        
        Args:
            concept: Concept to visualize
            
        Returns:
            Visual description
        """
        prompt = f"""Create a detailed visual description to help students picture: {concept}

Describe:
1. What would you SEE if you could observe this?
2. What are the key components or parts?
3. How do these parts interact or relate?
4. What colors, shapes, or patterns are involved?

Help the student create a strong mental image. Use vivid, descriptive language."""

        try:
            response_text = await async_chat(
                self.client,
                self.model_name,
                "",
                prompt,
                temperature=0.8,
                max_output_tokens=600,
            )

            return f"👁️ VISUAL DESCRIPTION:\n\n{response_text}"
        except Exception as e:
            return f"Error creating visual description: {format_error(e)}"
    
    async def address_misconceptions(
        self,
        concept: str
    ) -> str:
        """
        Address common misconceptions about a concept
        
        Args:
            concept: Concept to clarify
            
        Returns:
            Misconception clarifications
        """
        prompt = f"""What are common misconceptions about: {concept}?

For each misconception:
1. State the misconception
2. Explain why it's wrong
3. Provide the correct understanding
4. Give an example to clarify

List 3-5 common misconceptions.
Help students avoid these pitfalls."""

        try:
            response_text = await async_chat(
                self.client,
                self.model_name,
                "",
                prompt,
                temperature=0.8,
                max_output_tokens=600,
            )

            return f"""
⚠️ COMMON MISCONCEPTIONS: {concept}
{'=' * 60}

{response_text}

{'=' * 60}
"""
        except Exception as e:
            return f"Error addressing misconceptions: {format_error(e)}"
    
    async def create_concept_map(
        self,
        main_concept: str,
        related_concepts: Optional[List[str]] = None
    ) -> str:
        """
        Create a text-based concept map showing relationships
        
        Args:
            main_concept: Central concept
            related_concepts: Optional list of related concepts
            
        Returns:
            Text-based concept map
        """
        related_str = f"Include these related concepts: {', '.join(related_concepts)}" if related_concepts else ""
        
        prompt = f"""Create a concept map for: {main_concept}
{related_str}

Show:
1. The main concept at the center
2. Key sub-concepts or components
3. How they relate to each other
4. Important connections and relationships

Format as a clear text-based diagram using indentation and arrows (→).
Make the relationships clear and educational."""

        try:
            response_text = await async_chat(
                self.client,
                self.model_name,
                "",
                prompt,
                temperature=0.6,
                max_output_tokens=600,
            )

            return f"""
🗺️ CONCEPT MAP: {main_concept}
{'=' * 60}

{response_text}

{'=' * 60}
"""
        except Exception as e:
            return f"Error creating concept map: {format_error(e)}"