"""
Learning Session Tools for TutorsGPT Memory MCP Server
Leverages episodes (Step 02), CRUD operations (Step 07), and fact triples (Step 08)
"""

import uuid
import logging
from datetime import datetime
from typing import Any, Dict, List

from graphiti_core.nodes import EntityNode, EpisodeType
from graphiti_core.edges import EntityEdge
from educational_types import LearningSession, EducationalRelationships

logger = logging.getLogger(__name__)

def setup_learning_tools(mcp, get_graphiti_client, get_student_namespace):
    """Setup learning session and mastery tracking tools"""
    
    @mcp.tool()
    async def start_learning_session(
        student_id: str,
        topic: str,
        session_type: str = "tutorial",
        course: str = "default",
        semester: str = "current"
    ) -> str:
        """Begin a new learning session with context preparation
        
        Args:
            student_id: Student identifier
            topic: Learning topic/concept
            session_type: tutorial, practice, assessment, or review
            course: Course identifier
            semester: Semester identifier
        """
        try:
            client = await get_graphiti_client()
            namespace = get_student_namespace(student_id, course, semester)
            session_id = str(uuid.uuid4())
            
            # Create learning session episode (from Step 02)
            session_description = f"Started {session_type} session on {topic} for student {student_id}"
            
            await client.add_episode(
                name=f"Learning Session Started: {topic}",
                episode_body=session_description,
                source_description=f"{session_type} session",
                group_id=namespace,
                episode_type=EpisodeType.text
            )
            
            # Create session node with custom types (from Step 03)
            session_data = LearningSession(
                session_id=session_id,
                student_id=student_id,
                concept=topic,
                session_type=session_type,
                start_time=datetime.now(),
                duration_minutes=0,
                engagement_score=5,
                difficulty_rating=5,
                concepts_covered=[topic],
                learning_outcomes=[],
                notes=None
            )
            
            session_node = EntityNode(
                uuid=session_id,
                name=f"Learning Session: {topic}",
                group_id=namespace,
                created_at=datetime.now(),
                summary=f"{session_type} session on {topic}",
                attributes=session_data.model_dump()
            )
            
            await session_node.save(client.driver)
            
            logger.info(f"Started learning session {session_id} for student {student_id}")
            return f"Started {session_type} session on {topic}. Session ID: {session_id}"
            
        except Exception as e:
            logger.error(f"Error starting learning session: {e}")
            return f"Error starting session: {str(e)}"

    @mcp.tool()
    async def end_learning_session(
        session_id: str,
        student_id: str,
        mastery_achieved: bool,
        difficulty_rating: int,
        notes: str = "",
        course: str = "default",
        semester: str = "current"
    ) -> str:
        """Complete learning session and update student progress
        
        Args:
            session_id: Session identifier
            student_id: Student identifier
            mastery_achieved: Whether student achieved mastery
            difficulty_rating: Student's difficulty rating (1-10)
            notes: Additional session notes
            course: Course identifier
            semester: Semester identifier
        """
        try:
            client = await get_graphiti_client()
            namespace = get_student_namespace(student_id, course, semester)
            
            # Update session using CRUD operations (from Step 07)
            session_node = await EntityNode.get_by_uuid(client.driver, session_id)
            if session_node:
                session_node.attributes["difficulty_rating"] = difficulty_rating
                session_node.attributes["notes"] = notes
                session_node.attributes["mastery_achieved"] = mastery_achieved
                await session_node.save(client.driver)
            
            # Add completion episode
            completion_description = f"Completed learning session. Mastery: {mastery_achieved}, Difficulty: {difficulty_rating}/10"
            if notes:
                completion_description += f". Notes: {notes}"
                
            await client.add_episode(
                name=f"Learning Session Completed",
                episode_body=completion_description,
                source_description="Session completion",
                group_id=namespace,
                episode_type=EpisodeType.text
            )
            
            logger.info(f"Completed learning session {session_id}")
            return f"Successfully completed learning session. Mastery achieved: {mastery_achieved}"
            
        except Exception as e:
            logger.error(f"Error ending learning session: {e}")
            return f"Error ending session: {str(e)}"

    @mcp.tool()
    async def track_concept_mastery(
        student_id: str,
        concept: str,
        assessment_score: int,
        assessment_type: str = "practice",
        course: str = "default",
        semester: str = "current"
    ) -> str:
        """Record concept mastery progress using fact triples (from Step 08)
        
        Args:
            student_id: Student identifier
            concept: Concept being assessed
            assessment_score: Score achieved (0-100)
            assessment_type: quiz, test, practice, project
            course: Course identifier
            semester: Semester identifier
        """
        try:
            client = await get_graphiti_client()
            namespace = get_student_namespace(student_id, course, semester)
            
            # Create mastery fact triple (from Step 08)
            student_node = EntityNode(
                uuid=str(uuid.uuid4()),
                name=student_id,
                group_id=namespace,
                created_at=datetime.now(),
                summary=f"Student {student_id}",
                attributes={"type": "student"}
            )
            
            concept_node = EntityNode(
                uuid=str(uuid.uuid4()),
                name=concept,
                group_id=namespace,
                created_at=datetime.now(),
                summary=f"Learning concept: {concept}",
                attributes={"type": "concept"}
            )
            
            # Determine mastery relationship based on score
            if assessment_score >= 80:
                relationship = EducationalRelationships.MASTERED
                fact = f"Student {student_id} mastered {concept} with score {assessment_score}"
            elif assessment_score >= 60:
                relationship = EducationalRelationships.COMPLETED
                fact = f"Student {student_id} completed {concept} with score {assessment_score}"
            else:
                relationship = EducationalRelationships.STRUGGLED_WITH
                fact = f"Student {student_id} struggled with {concept}, score {assessment_score}"
            
            mastery_edge = EntityEdge(
                uuid=str(uuid.uuid4()),
                source_node_uuid=student_node.uuid,
                target_node_uuid=concept_node.uuid,
                group_id=namespace,
                created_at=datetime.now(),
                name=relationship,
                fact=fact,
                attributes={
                    "score": assessment_score,
                    "assessment_type": assessment_type,
                    "assessment_date": datetime.now().isoformat()
                }
            )
            
            # Add fact triple
            await client.add_triplet(student_node, mastery_edge, concept_node)
            
            # Also add as episode for natural language context
            await client.add_episode(
                name=f"Mastery Assessment: {concept}",
                episode_body=fact,
                source_description=f"{assessment_type} assessment",
                group_id=namespace,
                episode_type=EpisodeType.text
            )
            
            logger.info(f"Tracked mastery for {student_id}: {concept} = {assessment_score}")
            return f"Successfully tracked mastery: {fact}"
            
        except Exception as e:
            logger.error(f"Error tracking concept mastery: {e}")
            return f"Error tracking mastery: {str(e)}"

    @mcp.tool()
    async def recommend_next_topics(
        student_id: str,
        current_subject: str,
        difficulty_preference: str = "adaptive",
        course: str = "default",
        semester: str = "current"
    ) -> List[Dict[str, Any]]:
        """Suggest next learning topics based on student progress
        
        Args:
            student_id: Student identifier
            current_subject: Subject area for recommendations
            difficulty_preference: easy, moderate, challenging, or adaptive
            course: Course identifier
            semester: Semester identifier
        """
        try:
            client = await get_graphiti_client()
            namespace = get_student_namespace(student_id, course, semester)
            
            # Get student's completed concepts using search (from Step 06)
            completed_results = await client.search(
                query=f"student {student_id} mastered completed {current_subject}",
                group_id=namespace,
                limit=15
            )
            
            # Find concepts that build on completed ones
            next_topics = []
            for completed in completed_results:
                # Search for concepts that have this as prerequisite
                next_results = await client.search(
                    query=f"prerequisite {completed.fact} builds on",
                    group_id=namespace,
                    limit=5
                )
                
                for next_topic in next_results:
                    next_topics.append({
                        "topic": next_topic.fact,
                        "prerequisite_met": True,
                        "difficulty_level": "appropriate",
                        "confidence_score": next_topic.score,
                        "reason": f"Builds on completed concept: {completed.fact}"
                    })
            
            # If no specific recommendations, provide general ones
            if not next_topics:
                next_topics = [
                    {
                        "topic": f"Advanced {current_subject} concepts",
                        "prerequisite_met": True,
                        "difficulty_level": "moderate",
                        "confidence_score": 0.7,
                        "reason": "General progression in subject area"
                    }
                ]
            
            logger.info(f"Generated {len(next_topics)} topic recommendations for {student_id}")
            return next_topics[:5]  # Return top 5 recommendations
            
        except Exception as e:
            logger.error(f"Error generating topic recommendations: {e}")
            return [{"error": str(e)}]