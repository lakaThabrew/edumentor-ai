"""
EduMentor AI - Main Orchestrator Agent
Coordinates the multi-agent educational system
"""

import os
import asyncio
import sys
import argparse
from typing import Dict, List, Any
from dotenv import load_dotenv
import re

# Load environment variables first
load_dotenv()

# ADK Imports
from google import genai
from google.genai import types
from tools.genai_utils import async_chat

# Local imports
from agents.tutor_agent import TutorAgent
from agents.quiz_generator_agent import QuizGeneratorAgent
from agents.progress_tracker_agent import ProgressTrackerAgent
from agents.concept_explainer_agent import ConceptExplainerAgent
from session_manager import SessionManager
from memory_bank import MemoryBank
from observability import ObservabilityManager

class OrchestratorAgent:
    """
    Main orchestrator that coordinates all sub-agents.
    Uses sequential and parallel routing to determine which agent(s) to invoke.
    Implements multi-agent coordination from ADK course.
    """
    
    def __init__(self):
        """Initialize the orchestrator and all sub-agents"""
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")
        
        print("🔧 Initializing EduMentor AI components...")
        
        # Initialize GenAI client
        self.client = genai.Client(api_key=self.api_key)
        print("  ✓ GenAI client connected")
        
        # Initialize observability
        self.observability = ObservabilityManager()
        self.logger = self.observability.get_logger("orchestrator")
        print("  ✓ Observability system ready")
        
        # Initialize session manager and memory
        self.session_manager = SessionManager()
        self.memory_bank = MemoryBank()
        print("  ✓ Session & Memory systems initialized")
        
        # Initialize sub-agents
        self.logger.info("Initializing specialized agents...")
        print("  ✓ Loading Tutor Agent...")
        self.tutor = TutorAgent(self.client, self.memory_bank)
        
        print("  ✓ Loading Quiz Generator Agent...")
        self.quiz_generator = QuizGeneratorAgent(self.client)
        
        print("  ✓ Loading Progress Tracker Agent...")
        self.progress_tracker = ProgressTrackerAgent(self.client, self.memory_bank)
        
        print("  ✓ Loading Concept Explainer Agent...")
        self.concept_explainer = ConceptExplainerAgent(self.client)
        
        self.logger.info("All agents initialized successfully")
        print("\n✅ All systems operational!\n")
        
    async def route_query(self, query: str, student_id: str, session_id: str) -> str:
        """
        Route student query to appropriate agent(s).
        Uses LLM to intelligently determine routing.
        Implements sequential and parallel agent coordination.
        
        Args:
            query: Student's question or request
            student_id: Unique student identifier
            session_id: Current session ID
            
        Returns:
            Response from agent(s)
        """
        self.logger.info(f"Routing query for student {student_id}: {query[:50]}...")
        
        # Start trace for this request (observability)
        import time
        trace_id = f"query_{student_id}_{int(time.time())}"
        self.observability.start_trace(trace_id, "route_query", {"student_id": student_id})
        
        start_time = time.time()
        
        try:
            # Get student context from memory (long-term memory)
            student_context = self.memory_bank.get_student_context(student_id)
            
            # Determine intent using LLM
            intent = await self._determine_intent(query, student_context)
            
            self.logger.info(f"Determined intent: {intent}")
            self.observability.add_trace_event(trace_id, "intent_determined", {"intent": intent})
            
            # Route based on intent (Multi-agent coordination)
            if intent == "explanation":
                # Sequential: Concept explainer then tutor
                self.logger.info("Sequential routing: Concept Explainer -> Tutor")
                explanation = await self.concept_explainer.explain(query, student_id)
                response = await self.tutor.teach(query, student_id, context=explanation[:500])
                
            elif intent == "practice":
                # Parallel: Generate quiz and provide tutor support simultaneously
                self.logger.info("Parallel routing: Quiz Generator || Tutor")
                quiz_task = asyncio.create_task(
                    self.quiz_generator.generate_quiz(query, student_id, num_questions=5)
                )
                tutor_task = asyncio.create_task(
                    self.tutor.teach(f"Provide study tips for: {query}", student_id)
                )
                
                # Wait for both tasks to complete
                results = await asyncio.gather(quiz_task, tutor_task, return_exceptions=True)
                
                quiz = results[0] if not isinstance(results[0], Exception) else f"Quiz error: {results[0]}"
                tutor_response = results[1] if not isinstance(results[1], Exception) else f"Tutor error: {results[1]}"
                
                response = f"{tutor_response}\n\n{'='*60}\n📝 PRACTICE QUIZ\n{'='*60}\n\n{quiz}"
                
            elif intent == "progress":
                # Progress tracking (single agent)
                self.logger.info("Routing to Progress Tracker")
                response = await self.progress_tracker.analyze_progress(student_id)
                
            elif intent == "homework":
                # Sequential: Tutor guides, then generates practice
                self.logger.info("Sequential routing: Tutor -> Quiz Generator")
                guidance = await self.tutor.teach(query, student_id)
                practice = await self.quiz_generator.generate_quiz(
                    f"Practice problems for: {query}", 
                    student_id,
                    num_questions=3
                )
                response = f"{guidance}\n\n{'='*60}\n📝 PRACTICE PROBLEMS\n{'='*60}\n\n{practice}"
                
            else:
                # Default: Use tutor agent
                self.logger.info("Routing to Tutor Agent (default)")
                response = await self.tutor.teach(query, student_id)
            
            # Update session and memory (session & state management)
            self.session_manager.update_session(session_id, query, response)
            self.memory_bank.add_interaction(student_id, query, response, intent)
            
            # Track metrics (observability)
            duration = time.time() - start_time
            self.observability.record_metric("query_routed", 1, {"intent": intent})
            self.observability.log_performance("orchestrator", "route_query", duration, True)
            self.observability.end_trace(trace_id, "success")
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(f"Error routing query: {e}")
            self.observability.log_performance("orchestrator", "route_query", duration, False)
            self.observability.end_trace(trace_id, "error", {"error": str(e)})

            # Handle API quota errors (RESOURCE_EXHAUSTED / 429) with a concise message
            err_text = str(e)
            retry_seconds = None
            try:
                import re
                m = re.search(r'retry in (\d+(?:\.\d+)?)s', err_text)
                if m:
                    retry_seconds = float(m.group(1))
            except Exception:
                retry_seconds = None

            if 'RESOURCE_EXHAUSTED' in err_text or '429' in err_text:
                # Try a local knowledge-base fallback before returning retry message
                try:
                    from tools.knowledge_base_tool import KnowledgeBaseTool
                    kb = KnowledgeBaseTool()
                    kb_results = await kb.retrieve(query)
                    if kb_results and not kb_results.lower().startswith('no specific'):
                        return ("I couldn't reach the language API right now due to quota limits, "
                                "but here's some knowledge I can share from the local knowledge base:\n\n"
                                f"{kb_results}\n\n"
                                "(This is a limited fallback; for full help please retry after the cooldown.)")
                except Exception:
                    # If fallback fails, continue to return the retry message below
                    pass

                if retry_seconds:
                    return (f"I apologize — the language API quota was exceeded. "
                            f"Please try again in ~{int(retry_seconds)} seconds.")
                else:
                    return ("I apologize — the language API quota was exceeded. "
                            "Please check your API key / billing or try again later.")

            return f"I apologize, but I encountered an error processing your request: {e}\n\nPlease try rephrasing your question or type 'help' for assistance."
    
    async def _determine_intent(self, query: str, context: Dict) -> str:
        """
        Use LLM to determine the intent of the student's query.
        
        Args:
            query: Student's question
            context: Student context from memory
            
        Returns:
            Intent string: explanation, practice, progress, homework, or general
        """
        prompt = f"""Analyze this student query and determine the intent.

Student Query: "{query}"

Student Context:
- Recent topics: {context.get('recent_topics', [])}
- Difficulty level: {context.get('level', 'intermediate')}
- Learning gaps: {context.get('gaps', [])}

Return ONLY ONE WORD from these options:
- explanation: Student wants a concept explained or clarified (keywords: "explain", "what is", "how does", "why", "understand")
- practice: Student wants practice problems, quiz, or exercises (keywords: "practice", "quiz", "test me", "problems", "exercises")
- progress: Student asking about their progress, scores, or performance (keywords: "progress", "how am I doing", "stats", "performance", "report")
- homework: Student needs help with specific homework or assignment (keywords: "homework", "help with", "assignment", "solve", "stuck on")
- general: General question, greeting, or doesn't fit other categories

Intent (ONE WORD ONLY):"""
        
        try:
            response_text = await async_chat(
                self.client,
                'gemini-2.0-flash',
                "",
                prompt,
                temperature=0.3,
                max_output_tokens=10,
            )

            intent = response_text.strip()

            # Validate intent
            m = re.search(r'(explanation|practice|progress|homework|general)', response_text.lower())
            if m:
                intent = m.group(1)
            else:
                intent = 'general'

            return intent
        except Exception as e:
            self.logger.error(f"Error determining intent: {e}")
            return 'general'
    
    async def start_learning_session(self, student_id: str) -> str:
        """
        Start a new learning session for a student
        
        Args:
            student_id: Student identifier
            
        Returns:
            Greeting message
        """
        session_id = self.session_manager.get_current_session(student_id) or \
             self.session_manager.create_session(student_id)
        self.logger.info(f"Started session {session_id} for student {student_id}")
        
        # Increment session count in progress storage
        try:
            from tools.progress_storage_tool import ProgressStorageTool
            storage = ProgressStorageTool()
            storage.increment_session_count(student_id)
        except:
            pass  # Non-critical
        
        # Get personalized greeting from memory
        context = self.memory_bank.get_student_context(student_id)
        total_sessions = context.get('total_interactions', 0)
        
        greeting = f"""╔══════════════════════════════════════════════════════════╗
║  🎓 Welcome to EduMentor AI - Your Learning Assistant    ║
╚══════════════════════════════════════════════════════════╝

Hello! I'm here to help you learn and grow. 👋

I can assist you with:
  📚 Understanding difficult concepts
  ✍️  Homework and problem-solving  
  📝 Practice quizzes and exercises
  📊 Tracking your learning progress

💡 Tips:
  • Type 'progress' to see your learning stats
  • Type 'help' for available commands
  • Type 'quit' or 'exit' to end session
"""
        
        if total_sessions > 0:
            greeting += f"\n🌟 Welcome back! This is session #{total_sessions + 1}"
        
        if context.get('recent_topics'):
            recent = context['recent_topics'][:2]
            greeting += f"\n📖 Last time we worked on: {', '.join(recent)}"
        
        greeting += "\n\n" + "─" * 60
        greeting += "\n\nWhat would you like to learn today?"
        
        return greeting
    
    async def interactive_mode(self):
        """
        Run interactive CLI mode for testing and demonstration.
        Main user interface for the application.
        """
        print("╔══════════════════════════════════════════════════════════╗")
        print("║        EduMentor AI - Interactive Learning Mode          ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print()
        print("📋 Available Commands:")
        print("  • 'quit' or 'exit'  - End the session")
        print("  • 'progress'        - View your learning progress")
        print("  • 'help'            - Show all commands")
        print("  • 'clear'           - Clear the screen")
        print()
        
        # Get student ID
        student_id = input("👤 Enter your student ID (or name): ").strip()
        if not student_id:
            student_id = "demo_student"
            print(f"   Using default ID: {student_id}")
        
        print()
        
        # Start session
        greeting = await self.start_learning_session(student_id)
        print(greeting)
        print()
        
        session_id = self.session_manager.get_current_session(student_id)
        
        # Main interaction loop
        interaction_count = 0
        while True:
            try:
                # Get user input
                query = input("\n💬 You: ").strip()
                
                if not query:
                    continue
                
                # Handle commands
                if query.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print("\n" + "─" * 60)
                    print("👋 Thank you for learning with EduMentor AI!")
                    print(f"📊 Total interactions this session: {interaction_count}")
                    
                    # Show session stats
                    stats = self.session_manager.get_session_stats(session_id)
                    if stats:
                        duration_min = stats['duration_seconds'] / 60
                        print(f"⏱️  Session duration: {duration_min:.1f} minutes")
                    
                    print("🌟 Keep learning and stay curious!")
                    print("─" * 60 + "\n")
                    break
                
                if query.lower() == 'help':
                    print("""
╔══════════════════════════════════════════════════════════╗
║                    Available Commands                    ║
╚══════════════════════════════════════════════════════════╝

📋 Commands:
  progress     - View your detailed learning progress report
  help         - Show this help message
  clear        - Clear the screen
  quit/exit    - End the session

💡 Example Questions:
  • "Explain photosynthesis"
  • "Give me practice problems on algebra"
  • "Help me with my math homework"
  • "What are Newton's laws of motion?"
  • "Test me on biology"
  • "How am I doing?" (same as 'progress')

🎯 Learning Tips:
  • Ask specific questions for best results
  • Show your work when solving problems
  • Request practice after learning new concepts
  • Check your progress regularly
""")
                    continue
                
                if query.lower() == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print("Screen cleared.\n")
                    continue
                
                if query.lower() in ['progress', 'how am i doing', 'my progress']:
                    print("\n📊 Generating progress report...\n")
                    response = await self.progress_tracker.analyze_progress(student_id)
                else:
                    # Route the query to appropriate agents
                    print()  # Add spacing
                    response = await self.route_query(query, student_id, session_id)
                
                # Display response
                print(f"\n🤖 EduMentor:")
                print("─" * 60)
                print(response)
                print("─" * 60)
                
                interaction_count += 1
                
            except KeyboardInterrupt:
                print("\n\n" + "─" * 60)
                print("👋 Session interrupted. Goodbye!")
                print("─" * 60 + "\n")
                break
            except Exception as e:
                self.logger.error(f"Error in interactive mode: {e}", exc_info=True)
                print(f"\n❌ Error: {e}")
                print("Please try again or rephrase your question.")
                print("Type 'help' for assistance.\n")


async def main():
    """Main entry point for EduMentor AI"""
    print("\n" + "=" * 60)
    print("🚀 Starting EduMentor AI...")
    print("=" * 60 + "\n")

    # Allow non-interactive mode via CLI args for automated runs/tests
    parser = argparse.ArgumentParser(description="EduMentor AI runner")
    parser.add_argument('--student-id', dest='student_id', help='Student ID to use for the session', default=None)
    parser.add_argument('--prompt', dest='prompt', help='Single query to route (non-interactive)', default=None)
    args = parser.parse_args()

    try:
        # Check for API key
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ ERROR: GOOGLE_API_KEY not found in environment!\n")
            print("📋 Please follow these steps:")
            print("  1. Copy .env.example to .env")
            print("  2. Edit .env and add your Google API key")
            print("  3. Get your API key from: https://aistudio.google.com/app/apikey")
            print("\nExample .env file:")
            print("  GOOGLE_API_KEY=your_actual_api_key_here")
            print()
            return

        # Initialize orchestrator (this initializes all agents)
        orchestrator = OrchestratorAgent()

        # If both CLI args provided, run a single automated session and exit
        if args.student_id and args.prompt:
            student_id = str(args.student_id)
            query = str(args.prompt)

            # Start or restore a session for the student
            greeting = await orchestrator.start_learning_session(student_id)
            print(greeting)

            session_id = orchestrator.session_manager.get_current_session(student_id)
            print(f"\n💬 Running automated query for student {student_id}: {query}\n")

            # Route the single query and print response
            response = await orchestrator.route_query(query, student_id, session_id)

            print(f"\n🤖 EduMentor (automated):\n{"─"*60}\n{response}\n{"─"*60}")
            print("\n✅ Automated run completed")
            return

        # Otherwise run interactive mode
        await orchestrator.interactive_mode()

        print("\n✅ Session ended successfully")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease check your .env file and ensure GOOGLE_API_KEY is set correctly.")
    except KeyboardInterrupt:
        print("\n\n⚠️  Session interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        print("\n🔍 Full error trace:")
        traceback.print_exc()
        print("\n💡 Try running 'python test_agents.py' to diagnose the issue.")


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 9):
        print("❌ Error: Python 3.9 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Startup error: {e}")
        sys.exit(1)