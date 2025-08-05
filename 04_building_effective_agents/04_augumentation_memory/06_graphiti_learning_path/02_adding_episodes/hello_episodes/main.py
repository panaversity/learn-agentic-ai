import asyncio
import os
import json

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
                model="gemini-2.5-flash"
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
                model="gemini-2.0-flash"
            )
        )
    )

    try:
        await graphiti.build_indices_and_constraints()
        print("🚀 Starting Episode Types Demo...")

        # 1. TEXT EPISODE - Student background
        # print("\n📝 Adding text episode (student background)...")
        # await graphiti.add_episode(
        #     name="alice_enrollment",
        #     episode_body=(
        #         "Alice Chen is a 22-year-old biology student who enrolled in Python 101. "
        #         "She has excellent analytical skills from her science background but has "
        #         "never programmed before. Alice wants to learn Python to analyze DNA "
        #         "sequences and other biological data for her research."
        #     ),
        #     source=EpisodeType.text,
        #     source_description="Student enrollment system",
        #     reference_time=datetime.now() - timedelta(days=7),
        # )

        # 2. MESSAGE EPISODE - Tutoring conversation
        # print("💬 Adding message episode (tutoring session)...")
        # await graphiti.add_episode(
        #     name="alice_tutoring_loops",
        #     episode_body=(
        #         "Student: I'm confused about for loops in Python\n"
        #         "Tutor: No problem! What specifically is confusing you?\n"
        #         "Student: I understand the concept but keep getting syntax errors\n"
        #         "Tutor: Let's look at your code. Show me what you're trying to do\n"
        #         "Student: for base in dna_sequence print(base)\n"
        #         "Tutor: Ah! You're missing the colon. Try: for base in dna_sequence:\n"
        #         "Student: Oh wow, that fixed it! Thank you so much"
        #     ),
        #     source=EpisodeType.message,
        #     source_description="Online tutoring session",
        #     reference_time=datetime.now() - timedelta(days=3),
        # )

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
            episode_body=json.dumps(assessment_result),
            source=EpisodeType.json,
            source_description="Assessment system results",
            reference_time=datetime.now() - timedelta(days=1),
        )

        print("✅ All episodes added successfully!")

        # Search across all episode types
        # print("\n🔍 Searching across all episode types...")
        # search_results = await graphiti.search(
        #     query="Alice Chen Python learning progress loops",
        #     num_results=10
        # )

        # print(f"\n📊 Found {len(search_results)} results:")
        # for i, result in enumerate(search_results[:5], 1):
        #     print(f"  {i}. {result.fact}")

        # Specific searches by type
        print("\n🎯 Searching for alice tutoring interactions...")
        tutoring_results = await graphiti.search(
            query="What is alice confusion",
            num_results=5,
        )

        print(f"Tutoring insights: {len(tutoring_results)} results")
        for result in tutoring_results[:3]:
            print(f"  • {result.fact}")

        print("\n🎓 Episode types demo completed!")

    finally:
        await graphiti.close()
        print("Connection closed.")

if __name__ == "__main__":
    asyncio.run(main())
