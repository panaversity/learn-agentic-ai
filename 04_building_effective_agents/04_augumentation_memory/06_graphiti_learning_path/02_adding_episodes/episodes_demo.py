import asyncio
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv, find_dotenv

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

# Gemini setup (same as Step 01)
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

load_dotenv(find_dotenv())

async def main():
    """Complete example using all three episode types"""
    
    # Initialize Graphiti (same setup as Step 01)
    graphiti = Graphiti(
        os.environ.get('NEO4J_URI', 'bolt://localhost:7687'),
        os.environ.get('NEO4J_USER', 'neo4j'),
        os.environ.get('NEO4J_PASSWORD', 'password'),
        llm_client=GeminiClient(
            config=LLMConfig(
                api_key=os.environ.get('GEMINI_API_KEY'),
                model="gemini-2.0-flash"
            )
        ),
        embedder=GeminiEmbedder(
            config=GeminiEmbedderConfig(
                api_key=os.environ.get('GEMINI_API_KEY'),
                embedding_model="embedding-001"
            )
        ),
        cross_encoder=GeminiRerankerClient(
            config=LLMConfig(
                api_key=os.environ.get('GEMINI_API_KEY'),
                model="gemini-2.0-flash-exp"
            )
        )
    )
    
    try:
        await graphiti.build_indices_and_constraints()
        print("🚀 Starting Episode Types Demo...")
        
        # 1. TEXT EPISODE - Student background
        print("\n📝 Adding text episode (student background)...")
        await graphiti.add_episode(
            name="alice_enrollment",
            episode_body=(
                "Alice Chen is a 22-year-old biology student who enrolled in Python 101. "
                "She has excellent analytical skills from her science background but has "
                "never programmed before. Alice wants to learn Python to analyze DNA "
                "sequences and other biological data for her research."
            ),
            source=EpisodeType.text,
            source_description="Student enrollment system",
            reference_time=datetime.now() - timedelta(days=7),
        )
        
        # 2. MESSAGE EPISODE - Tutoring conversation
        print("💬 Adding message episode (tutoring session)...")
        await graphiti.add_episode(
            name="alice_tutoring_loops",
            episode_body=(
                "Student: I'm confused about for loops in Python\n"
                "Tutor: No problem! What specifically is confusing you?\n"
                "Student: I understand the concept but keep getting syntax errors\n"
                "Tutor: Let's look at your code. Show me what you're trying to do\n"
                "Student: for base in dna_sequence print(base)\n"
                "Tutor: Ah! You're missing the colon. Try: for base in dna_sequence:\n"
                "Student: Oh wow, that fixed it! Thank you so much"
            ),
            source=EpisodeType.message,
            source_description="Online tutoring session",
            reference_time=datetime.now() - timedelta(days=3),
        )
        
        # 3. JSON EPISODE - Assessment results
        print("📊 Adding JSON episode (assessment data)...")
        assessment_result = {
            "student_id": "alice_chen_001",
            "student_name": "Alice Chen",
            "course": "Python 101",
            "assessment_type": "loops_quiz",
            "date": "2024-01-15",
            "score": 88,
            "max_score": 100,
            "time_spent_minutes": 35,
            "questions_correct": 7,
            "questions_total": 8,
            "topics_tested": ["for_loops", "while_loops", "nested_loops"],
            "strengths": ["basic loop syntax", "iteration logic"],
            "needs_improvement": ["nested loop complexity"],
            "instructor_notes": "Great progress! Ready for functions next."
        }
        
        await graphiti.add_episode(
            name="alice_loops_assessment",
            episode_body=assessment_result,
            source=EpisodeType.json,
            source_description="Assessment system results",
            reference_time=datetime.now() - timedelta(days=1),
        )
        
        print("✅ All episodes added successfully!")
        
        # Search across all episode types
        print("\n🔍 Searching across all episode types...")
        search_results = await graphiti.search(
            query="Alice Chen Python learning progress loops",
            num_results=10
        )
        
        print(f"\n📊 Found {len(search_results)} results:")
        for i, result in enumerate(search_results[:5], 1):
            print(f"  {i}. {result.fact}")
        
        # Specific searches by type
        print("\n🎯 Searching for tutoring interactions...")
        tutoring_results = await graphiti.search(
            query="tutoring session loops syntax error colon",
            num_results=5
        )
        
        print(f"Tutoring insights: {len(tutoring_results)} results")
        for result in tutoring_results[:3]:
            print(f"  • {result.fact}")
        
        print("\n🎓 Episode types demo completed!")
        
    finally:
        await graphiti.close()
        print("Connection closed.")

# Bonus: Bulk loading example
async def bulk_loading_demo():
    """Demonstrate efficient bulk episode loading"""
    from graphiti_core.nodes import RawEpisode
    import json
    
    # Same Graphiti setup as above
    graphiti = Graphiti(
        os.environ.get('NEO4J_URI', 'bolt://localhost:7687'),
        os.environ.get('NEO4J_USER', 'neo4j'),
        os.environ.get('NEO4J_PASSWORD', 'password'),
        llm_client=GeminiClient(
            config=LLMConfig(
                api_key=os.environ.get('GEMINI_API_KEY'),
                model="gemini-2.0-flash"
            )
        ),
        embedder=GeminiEmbedder(
            config=GeminiEmbedderConfig(
                api_key=os.environ.get('GEMINI_API_KEY'),
                embedding_model="embedding-001"
            )
        ),
        cross_encoder=GeminiRerankerClient(
            config=LLMConfig(
                api_key=os.environ.get('GEMINI_API_KEY'),
                model="gemini-2.0-flash-exp"
            )
        )
    )
    
    try:
        await graphiti.build_indices_and_constraints()
        print("⚡ Starting Bulk Loading Demo...")
        
        # Prepare multiple episodes
        episodes = []
        
        # Create 5 assessment records
        for i in range(5):
            assessment = {
                "student_id": f"student_{i:03d}",
                "student_name": f"Student {i+1}",
                "course": "Python 101",
                "assignment": "Variables Quiz",
                "score": 75 + (i * 5),  # Scores from 75 to 95
                "date": f"2024-01-{15+i:02d}",
                "time_spent_minutes": 20 + (i * 5),
                "topics": ["variables", "data_types", "assignment"]
            }
            
            episodes.append(RawEpisode(
                name=f"bulk_assessment_{i:03d}",
                content=json.dumps(assessment),
                source=EpisodeType.json,
                source_description="Bulk assessment import",
                reference_time=datetime.now() - timedelta(days=10-i)
            ))
        
        # Bulk load (much faster than individual episodes)
        print(f"📦 Bulk loading {len(episodes)} episodes...")
        await graphiti.add_episode_bulk(episodes)
        print(f"✅ Successfully bulk loaded {len(episodes)} episodes")
        
        # Verify bulk loading worked
        print("\n🔍 Searching bulk loaded data...")
        bulk_results = await graphiti.search(
            query="Variables Quiz assessment scores",
            num_results=8
        )
        
        print(f"Found {len(bulk_results)} results from bulk loading:")
        for i, result in enumerate(bulk_results[:5], 1):
            print(f"  {i}. {result.fact}")
            
    finally:
        await graphiti.close()
        print("Bulk loading demo completed.")

if __name__ == "__main__":
    print("Choose demo to run:")
    print("1. Main episode types demo")
    print("2. Bulk loading demo")
    print("3. Both demos")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(main())
    elif choice == "2":
        asyncio.run(bulk_loading_demo())
    elif choice == "3":
        asyncio.run(main())
        print("\n" + "="*50 + "\n")
        asyncio.run(bulk_loading_demo())
    else:
        print("Running main demo by default...")
        asyncio.run(main())