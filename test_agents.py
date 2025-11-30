"""
Test script for EduMentor AI agents
Tests individual components before running full system
"""

import asyncio
import os
from dotenv import load_dotenv
from google import genai

# Load environment
load_dotenv()

async def test_tutor_agent():
    """Test Tutor Agent"""
    print("\n" + "="*60)
    print("Testing Tutor Agent...")
    print("="*60)
    
    try:
        from agents.tutor_agent import TutorAgent
        from memory_bank import MemoryBank
        
        client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        memory = MemoryBank()
        tutor = TutorAgent(client, memory)
        
        response = await tutor.teach(
            "What is photosynthesis?",
            "test_student"
        )
        
        print("\n✅ Tutor Agent Response:")
        print(response[:300] + "..." if len(response) > 300 else response)
        return True
        
    except Exception as e:
        print(f"\n❌ Tutor Agent Error: {e}")
        return False

async def test_quiz_generator():
    """Test Quiz Generator Agent"""
    print("\n" + "="*60)
    print("Testing Quiz Generator Agent...")
    print("="*60)
    
    try:
        from agents.quiz_generator_agent import QuizGeneratorAgent
        
        client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        quiz_gen = QuizGeneratorAgent(client)
        
        quiz = await quiz_gen.generate_quiz(
            topic="basic algebra",
            student_id="test_student",
            num_questions=3,
            difficulty="medium"
        )
        
        print("\n✅ Quiz Generated:")
        print(quiz[:400] + "..." if len(quiz) > 400 else quiz)
        return True
        
    except Exception as e:
        print(f"\n❌ Quiz Generator Error: {e}")
        return False

async def test_progress_tracker():
    """Test Progress Tracker Agent"""
    print("\n" + "="*60)
    print("Testing Progress Tracker Agent...")
    print("="*60)
    
    try:
        from agents.progress_tracker_agent import ProgressTrackerAgent
        from memory_bank import MemoryBank
        
        client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        memory = MemoryBank()
        
        # Add some test data
        memory.add_interaction(
            "test_student",
            "Help with math",
            "Here's how to solve it...",
            "homework"
        )
        
        tracker = ProgressTrackerAgent(client, memory)
        report = await tracker.analyze_progress("test_student")
        
        print("\n✅ Progress Report:")
        print(report[:400] + "..." if len(report) > 400 else report)
        return True
        
    except Exception as e:
        print(f"\n❌ Progress Tracker Error: {e}")
        return False

async def test_concept_explainer():
    """Test Concept Explainer Agent"""
    print("\n" + "="*60)
    print("Testing Concept Explainer Agent...")
    print("="*60)
    
    try:
        from agents.concept_explainer_agent import ConceptExplainerAgent
        
        client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))
        explainer = ConceptExplainerAgent(client)
        
        explanation = await explainer.explain(
            "gravity",
            "test_student",
            "simple"
        )
        
        print("\n✅ Concept Explanation:")
        print(explanation[:400] + "..." if len(explanation) > 400 else explanation)
        return True
        
    except Exception as e:
        print(f"\n❌ Concept Explainer Error: {e}")
        return False

def test_memory_bank():
    """Test Memory Bank"""
    print("\n" + "="*60)
    print("Testing Memory Bank...")
    print("="*60)
    
    try:
        from memory_bank import MemoryBank
        
        memory = MemoryBank()
        
        # Test adding interaction
        memory.add_interaction(
            "test_student",
            "What is 2+2?",
            "Let me guide you...",
            "homework"
        )
        
        # Test getting context
        context = memory.get_student_context("test_student")
        
        print("\n✅ Memory Bank Working")
        print(f"Context: {context}")
        return True
        
    except Exception as e:
        print(f"\n❌ Memory Bank Error: {e}")
        return False

def test_session_manager():
    """Test Session Manager"""
    print("\n" + "="*60)
    print("Testing Session Manager...")
    print("="*60)
    
    try:
        from session_manager import SessionManager
        
        sm = SessionManager()
        
        # Create session
        session_id = sm.create_session("test_student")
        
        # Update session
        sm.update_session(session_id, "Hello", "Hi there!")
        
        # Get history
        history = sm.get_conversation_history(session_id)
        
        print("\n✅ Session Manager Working")
        print(f"Session ID: {session_id}")
        print(f"History: {history}")
        return True
        
    except Exception as e:
        print(f"\n❌ Session Manager Error: {e}")
        return False

async def test_knowledge_tool():
    """Test Knowledge Base Tool"""
    print("\n" + "="*60)
    print("Testing Knowledge Base Tool...")
    print("="*60)
    
    try:
        from tools.knowledge_base_tool import KnowledgeBaseTool
        
        tool = KnowledgeBaseTool()
        # Test retrieval (await async method directly)
        results = await tool.retrieve("photosynthesis")
        
        print("\n✅ Knowledge Base Tool Working")
        print(f"Results: {results}")
        return True
        
    except Exception as e:
        print(f"\n❌ Knowledge Base Tool Error: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("\n🧪 EDUMENTOR AI - COMPONENT TESTS")
    print("=" * 60)
    
    # Check API key
    if not os.getenv('GOOGLE_API_KEY'):
        print("\n❌ ERROR: GOOGLE_API_KEY not found in environment")
        print("Please set it in your .env file")
        return
    
    results = {}
    
    # Test components
    print("\n📦 Testing Core Components...")
    results['memory_bank'] = test_memory_bank()
    results['session_manager'] = test_session_manager()
    results['knowledge_tool'] = await test_knowledge_tool()
    
    # Test agents (async)
    print("\n🤖 Testing AI Agents...")
    results['tutor'] = await test_tutor_agent()
    results['quiz_generator'] = await test_quiz_generator()
    results['progress_tracker'] = await test_progress_tracker()
    results['concept_explainer'] = await test_concept_explainer()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for component, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{component.replace('_', ' ').title()}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to run the main application.")
        print("Run: python main.py")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(run_all_tests())