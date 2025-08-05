#!/usr/bin/env python3
"""
Demo client for TutorsGPT Memory MCP Server
Demonstrates all the educational memory capabilities we've built
"""

import asyncio
import json
from datetime import datetime

import httpx

# MCP Server URL (adjust if running on different port)
MCP_SERVER_URL = "http://localhost:8000"

async def demo_tutorsgpt_memory():
    """Demonstrate TutorsGPT Memory MCP Server capabilities"""
    
    print("🎓 TutorsGPT Memory MCP Server Demo")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # 1. Create Student Profile
        print("\n📝 Step 1: Creating student profile...")
        
        profile_response = await client.post(
            f"{MCP_SERVER_URL}/tools/create_student_profile",
            json={
                "student_id": "alice_123",
                "name": "Alice Chen",
                "learning_style": "Visual",
                "grade_level": "10th Grade",
                "subjects": "Mathematics,Programming,Science",
                "course": "cs101",
                "semester": "fall2024"
            }
        )
        
        if profile_response.status_code == 200:
            result = profile_response.json()
            print(f"   ✅ {result.get('result', 'Profile created successfully')}")
        else:
            print(f"   ❌ Error: {profile_response.text}")
        
        # 2. Start Learning Session
        print("\n🚀 Step 2: Starting learning session...")
        
        session_response = await client.post(
            f"{MCP_SERVER_URL}/tools/start_learning_session",
            json={
                "student_id": "alice_123",
                "topic": "Python Variables",
                "session_type": "tutorial",
                "course": "cs101",
                "semester": "fall2024"
            }
        )
        
        session_id = None
        if session_response.status_code == 200:
            result = session_response.json()
            print(f"   ✅ {result.get('result', 'Session started')}")
            # Extract session ID from result (simplified)
            session_id = "demo_session_123"
        else:
            print(f"   ❌ Error: {session_response.text}")
        
        # 3. Track Concept Mastery
        print("\n📊 Step 3: Tracking concept mastery...")
        
        mastery_response = await client.post(
            f"{MCP_SERVER_URL}/tools/track_concept_mastery",
            json={
                "student_id": "alice_123",
                "concept": "Python Variables",
                "assessment_score": 85,
                "assessment_type": "practice",
                "course": "cs101",
                "semester": "fall2024"
            }
        )
        
        if mastery_response.status_code == 200:
            result = mastery_response.json()
            print(f"   ✅ {result.get('result', 'Mastery tracked')}")
        else:
            print(f"   ❌ Error: {mastery_response.text}")
        
        # 4. Get Tutoring Context
        print("\n🧠 Step 4: Getting tutoring context...")
        
        context_response = await client.post(
            f"{MCP_SERVER_URL}/tools/get_tutoring_context",
            json={
                "student_id": "alice_123",
                "current_topic": "Python Loops",
                "context_depth": "full",
                "course": "cs101",
                "semester": "fall2024"
            }
        )
        
        if context_response.status_code == 200:
            context = context_response.json()
            print(f"   ✅ Generated tutoring context for Python Loops")
            print(f"      - Learning history items: {len(context.get('result', {}).get('learning_history', []))}")
            print(f"      - Recent struggles: {len(context.get('result', {}).get('recent_struggles', []))}")
            print(f"      - Recommended approach: {context.get('result', {}).get('recommended_approach', 'N/A')}")
        else:
            print(f"   ❌ Error: {context_response.text}")
        
        # 5. Analyze Learning Gaps
        print("\n🔍 Step 5: Analyzing learning gaps...")
        
        gaps_response = await client.post(
            f"{MCP_SERVER_URL}/tools/analyze_learning_gaps",
            json={
                "student_id": "alice_123",
                "target_concept": "Python Functions",
                "course": "cs101",
                "semester": "fall2024"
            }
        )
        
        if gaps_response.status_code == 200:
            gaps = gaps_response.json()
            gap_count = len(gaps.get('result', []))
            print(f"   ✅ Identified {gap_count} learning gaps for Python Functions")
            for gap in gaps.get('result', [])[:2]:  # Show first 2 gaps
                if isinstance(gap, dict) and 'missing_prerequisite' in gap:
                    print(f"      - Gap: {gap['missing_prerequisite']}")
        else:
            print(f"   ❌ Error: {gaps_response.text}")
        
        # 6. Get Learning Insights
        print("\n📈 Step 6: Generating learning insights...")
        
        insights_response = await client.post(
            f"{MCP_SERVER_URL}/tools/get_learning_insights",
            json={
                "student_id": "alice_123",
                "time_period": "last_30_days",
                "course": "cs101",
                "semester": "fall2024"
            }
        )
        
        if insights_response.status_code == 200:
            insights = insights_response.json()
            analytics = insights.get('result', {})
            print(f"   ✅ Generated learning insights")
            print(f"      - Concepts mastered: {analytics.get('concepts_mastered', 0)}")
            print(f"      - Learning velocity: {analytics.get('learning_velocity', 0):.1f} concepts/week")
            print(f"      - Strength areas: {', '.join(analytics.get('strength_areas', []))}")
        else:
            print(f"   ❌ Error: {insights_response.text}")
        
        # 7. Get Topic Recommendations
        print("\n💡 Step 7: Getting topic recommendations...")
        
        recommendations_response = await client.post(
            f"{MCP_SERVER_URL}/tools/recommend_next_topics",
            json={
                "student_id": "alice_123",
                "current_subject": "Programming",
                "difficulty_preference": "adaptive",
                "course": "cs101",
                "semester": "fall2024"
            }
        )
        
        if recommendations_response.status_code == 200:
            recommendations = recommendations_response.json()
            topics = recommendations.get('result', [])
            print(f"   ✅ Generated {len(topics)} topic recommendations")
            for i, topic in enumerate(topics[:3], 1):  # Show first 3
                if isinstance(topic, dict):
                    print(f"      {i}. {topic.get('topic', 'Unknown topic')}")
        else:
            print(f"   ❌ Error: {recommendations_response.text}")
        
        # 8. End Learning Session
        if session_id:
            print("\n✅ Step 8: Ending learning session...")
            
            end_response = await client.post(
                f"{MCP_SERVER_URL}/tools/end_learning_session",
                json={
                    "session_id": session_id,
                    "student_id": "alice_123",
                    "mastery_achieved": True,
                    "difficulty_rating": 6,
                    "notes": "Student showed good understanding of variables",
                    "course": "cs101",
                    "semester": "fall2024"
                }
            )
            
            if end_response.status_code == 200:
                result = end_response.json()
                print(f"   ✅ {result.get('result', 'Session ended successfully')}")
            else:
                print(f"   ❌ Error: {end_response.text}")
        
        # 9. Search Student Memory
        print("\n🔍 Step 9: Searching student memory...")
        
        search_response = await client.post(
            f"{MCP_SERVER_URL}/tools/search_student_memory",
            json={
                "student_id": "alice_123",
                "query": "Python variables learning progress",
                "search_type": "facts",
                "course": "cs101",
                "semester": "fall2024",
                "limit": 5
            }
        )
        
        if search_response.status_code == 200:
            search_results = search_response.json()
            results = search_results.get('result', {}).get('results', [])
            print(f"   ✅ Found {len(results)} memory results")
            for result in results[:2]:  # Show first 2
                if isinstance(result, dict) and 'fact' in result:
                    print(f"      - {result['fact']}")
        else:
            print(f"   ❌ Error: {search_response.text}")
        
        print("\n🎉 TutorsGPT Memory Demo Complete!")
        print("\nThis demo showcased:")
        print("✅ Student profile management with custom types (Step 03)")
        print("✅ Learning session tracking with episodes (Step 02)")
        print("✅ Concept mastery using fact triples (Step 08)")
        print("✅ Context engineering with intelligent search (Step 06)")
        print("✅ Learning gap analysis combining multiple techniques")
        print("✅ Learning analytics with custom educational types")
        print("✅ Personalized recommendations based on progress")
        print("✅ Multi-user isolation with namespacing (Step 05)")
        print("✅ Comprehensive memory search across all data types")

async def test_server_connection():
    """Test if the MCP server is running"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_SERVER_URL}/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ MCP Server is running")
                return True
            else:
                print(f"❌ MCP Server responded with status {response.status_code}")
                return False
    except httpx.ConnectError:
        print("❌ Cannot connect to MCP Server")
        print(f"   Make sure the server is running on {MCP_SERVER_URL}")
        print("   Run: uv run python main.py")
        return False
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        return False

async def main():
    """Main demo function"""
    print("🔍 Testing server connection...")
    
    if await test_server_connection():
        await demo_tutorsgpt_memory()
    else:
        print("\n💡 To run the demo:")
        print("1. Start the TutorsGPT MCP Server: uv run python main.py")
        print("2. Run this demo: uv run python demo_client.py")

if __name__ == "__main__":
    asyncio.run(main())