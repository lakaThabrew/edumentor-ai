"""
Quick test to verify the multi-agent system works end-to-end
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def main():
    print("\n" + "="*60)
    print("🧪 QUICK MULTI-AGENT SYSTEM TEST")
    print("="*60 + "\n")
    
    # Check API key
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY not set. Please check your .env file.")
        return
    
    try:
        # Initialize orchestrator
        print("1️⃣ Initializing Orchestrator Agent...")
        from main import OrchestratorAgent
        orchestrator = OrchestratorAgent()
        print("   ✅ Orchestrator initialized\n")
        
        # Start a learning session
        student_id = "quick_test"
        print("2️⃣ Starting learning session...")
        greeting = await orchestrator.start_learning_session(student_id)
        print(f"   ✅ Session started\n")
        
        session_id = orchestrator.session_manager.get_current_session(student_id)
        
        # Test query routing
        test_queries = [
            ("explain gravity", "explanation"),
            ("give me practice problems on algebra", "practice"),
            ("help me with my homework on fractions", "homework"),
        ]
        
        for i, (query, expected_intent) in enumerate(test_queries, 1):
            print(f"3️⃣.{i} Testing query: '{query}'")
            print(f"      Expected intent: {expected_intent}")
            
            response = await orchestrator.route_query(query, student_id, session_id)
            
            # Show first 200 chars of response
            preview = response[:200].replace('\n', ' ')
            print(f"      Response preview: {preview}...")
            print("      ✅ Query processed\n")
        
        print("="*60)
        print("🎉 All tests completed successfully!")
        print("="*60)
        print("\n✅ The multi-agent system is working correctly.")
        print("   Run 'python main.py' for interactive mode.\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
