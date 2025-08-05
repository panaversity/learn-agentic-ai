#!/usr/bin/env python3
"""
TutorsGPT Memory MCP Server - Educational AI Memory System
Leverages all Graphiti knowledge from Steps 01-08
"""

import asyncio
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv, find_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from graphiti_core import Graphiti
from graphiti_core.nodes import EntityNode, EpisodeType
from graphiti_core.edges import EntityEdge
from graphiti_core.llm_client.gemini_client import GeminiClient, LLMConfig
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.cross_encoder.gemini_reranker_client import GeminiRerankerClient

from educational_types import (
    Student, LearningSession, TutoringContext, LearningAnalytics,
    EducationalRelationships
)

load_dotenv(find_dotenv())

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Global Graphiti instance
graphiti_client: Optional[Graphiti] = None

# MCP server instructions
TUTORSGPT_MCP_INSTRUCTIONS = """
TutorsGPT Memory MCP Server - AI-Powered Educational Memory System

This server provides comprehensive educational memory capabilities for AI tutoring systems.
It combines temporal knowledge graphs with educational domain expertise to enable:

1. **Student Profile Management**: Track learning styles, progress, and preferences
2. **Learning Context Engineering**: Provide rich context for AI tutoring sessions  
3. **Progress Tracking**: Monitor mastery, struggles, and learning patterns
4. **Personalized Recommendations**: Suggest next learning steps based on history
5. **Learning Analytics**: Generate insights about student performance and patterns

Key Features:
- Multi-user isolation using student namespacing (group_id per student)
- Educational domain types (students, concepts, assessments, mastery)
- Intelligent search across learning history and knowledge relationships
- Fact triple management for structured educational relationships
- Episode management for natural learning conversations

Each student has an isolated memory space using group_id format: "student_{student_id}_{course}_{semester}"
This ensures complete privacy and personalization for each learner.

Use these tools to build intelligent, memory-powered educational AI systems that adapt
to each student's unique learning journey.
"""

# MCP server instance
mcp = FastMCP(
    'TutorsGPT Memory Server',
    instructions=TUTORSGPT_MCP_INSTRUCTIONS
)

async def get_graphiti_client() -> Graphiti:
    """Initialize and return Graphiti client"""
    global graphiti_client
    
    if graphiti_client is None:
        graphiti_client = Graphiti(
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
        await graphiti_client.build_indices_and_constraints()
        logger.info("TutorsGPT Graphiti client initialized successfully")
    
    return graphiti_client

def get_student_namespace(student_id: str, course: str = "default", semester: str = "current") -> str:
    """Generate student-specific namespace for memory isolation (from Step 05)"""
    return f"student_{student_id}_{course}_{semester}"

# Import tool functions from separate modules
from student_tools import setup_student_tools
from learning_tools import setup_learning_tools
from context_tools import setup_context_tools
from analytics_tools import setup_analytics_tools

async def main():
    """Run the TutorsGPT Memory MCP Server"""
    try:
        # Setup all tool categories
        setup_student_tools(mcp, get_graphiti_client, get_student_namespace)
        setup_learning_tools(mcp, get_graphiti_client, get_student_namespace)
        setup_context_tools(mcp, get_graphiti_client, get_student_namespace)
        setup_analytics_tools(mcp, get_graphiti_client, get_student_namespace)
        
        # Initialize Graphiti client
        await get_graphiti_client()
        logger.info("TutorsGPT Memory MCP Server started successfully")
        
        # Run the MCP server
        await mcp.run()
        
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())