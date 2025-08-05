"""
Student Management Tools for TutorsGPT Memory MCP Server
Leverages custom types (Step 03), CRUD operations (Step 07), and episodes (Step 02)
"""

import uuid
import logging
from datetime import datetime
from typing import Any, Dict

from graphiti_core.nodes import EntityNode, EpisodeType
from educational_types import Student

logger = logging.getLogger(__name__)

def setup_student_tools(mcp, get_graphiti_client, get_student_namespace):
    """Setup student management tools"""
    
    @mcp.tool()
    async def create_student_profile(
        student_id: str,
        name: str,
        learning_style: str,
        grade_level: str = "unknown",
        subjects: str = "",
        course: str = "default",
        semester: str = "current"
    ) -> str:
        """Create a comprehensive student profile with educational metadata
        
        Args:
            student_id: Unique identifier for the student
            name: Student's full name
            learning_style: Visual, Auditory, Kinesthetic, or Reading/Writing
            grade_level: Academic grade level
            subjects: Comma-separated list of subjects
            course: Course identifier for namespacing
            semester: Semester identifier for namespacing
        """
        try:
            client = await get_graphiti_client()
            namespace = get_student_namespace(student_id, course, semester)
            
            # Create student profile using custom types (from Step 03)
            student_data = Student(
                student_id=student_id,
                name=name,
                learning_style=learning_style,
                current_level="Beginner",
                preferred_pace="Normal",
                grade_level=grade_level,
                subjects=subjects.split(",") if subjects else [],
                learning_goals=[],
                special_needs=None
            )
            
            # Create student node using CRUD operations (from Step 07)
            student_uuid = str(uuid.uuid4())
            student_node = EntityNode(
                uuid=student_uuid,
                name=name,
                group_id=namespace,
                created_at=datetime.now(),
                summary=f"Student profile for {name}",
                attributes=student_data.model_dump()
            )
            
            await student_node.save(client.driver)
            
            # Add episode about student creation (from Step 02)
            await client.add_episode(
                name=f"Student Profile Created: {name}",
                episode_body=f"Created student profile for {name} with learning style {learning_style}",
                source_description="Student registration",
                group_id=namespace,
                episode_type=EpisodeType.text
            )
            
            logger.info(f"Created student profile for {student_id} in namespace {namespace}")
            return f"Successfully created student profile for {name} (ID: {student_id})"
            
        except Exception as e:
            logger.error(f"Error creating student profile: {e}")
            return f"Error creating student profile: {str(e)}"

    @mcp.tool()
    async def get_student_profile(
        student_id: str,
        course: str = "default",
        semester: str = "current"
    ) -> Dict[str, Any]:
        """Retrieve comprehensive student profile and learning history
        
        Args:
            student_id: Student identifier
            course: Course identifier for namespacing
            semester: Semester identifier for namespacing
        """
        try:
            client = await get_graphiti_client()
            namespace = get_student_namespace(student_id, course, semester)
            
            # Search for student using intelligent search (from Step 06)
            search_results = await client.search(
                query=f"student profile {student_id}",
                group_id=namespace,
                limit=5
            )
            
            if not search_results:
                return {"error": f"No profile found for student {student_id}"}
            
            # Get recent learning episodes
            episodes = await client.get_episodes(
                group_id=namespace,
                last_n=10
            )
            
            return {
                "student_id": student_id,
                "namespace": namespace,
                "profile_data": search_results[0].fact if search_results else None,
                "recent_episodes": [ep.name for ep in episodes],
                "total_episodes": len(episodes)
            }
            
        except Exception as e:
            logger.error(f"Error retrieving student profile: {e}")
            return {"error": str(e)}

    @mcp.tool()
    async def search_student_memory(
        student_id: str,
        query: str,
        search_type: str = "facts",
        course: str = "default",
        semester: str = "current",
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search student's learning memory using intelligent search (from Step 06)
        
        Args:
            student_id: Student identifier
            query: Search query
            search_type: facts, episodes, or nodes
            course: Course identifier
            semester: Semester identifier
            limit: Maximum results to return
        """
        try:
            client = await get_graphiti_client()
            namespace = get_student_namespace(student_id, course, semester)
            
            if search_type == "episodes":
                episodes = await client.get_episodes(
                    group_id=namespace,
                    last_n=limit
                )
                return {
                    "results": [{"name": ep.name, "content": ep.content} for ep in episodes],
                    "total_found": len(episodes)
                }
            else:
                # Default to fact search
                results = await client.search(
                    query=query,
                    group_id=namespace,
                    limit=limit
                )
                return {
                    "results": [{"fact": r.fact, "score": r.score} for r in results],
                    "total_found": len(results)
                }
            
        except Exception as e:
            logger.error(f"Error searching student memory: {e}")
            return {"error": str(e)}