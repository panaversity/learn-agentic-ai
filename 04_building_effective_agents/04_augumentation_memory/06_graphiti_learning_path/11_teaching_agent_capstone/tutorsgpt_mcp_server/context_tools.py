"""
Context Engineering Tools for TutorsGPT Memory MCP Server
Leverages search (Step 06), fact triples (Step 08), and custom types (Step 03)
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from educational_types import TutoringContext

logger = logging.getLogger(__name__)

def setup_context_tools(mcp, get_graphiti_client, get_student_namespace):
    """Setup context engineering and tutoring support tools"""
    
    @mcp.tool()
    async def get_tutoring_context(
        student_id: str,
        current_topic: str,
        context_depth: str = "full",
        course: str = "default",
        semester: str = "current"
    ) -> Dict[str, Any]:
        """Get rich context for AI tutoring including learning history and preferences
        
        Args:
            student_id: Student identifier
            current_topic: Topic being tutored
            context_depth: full, summary, or minimal
            course: Course identifier
            semester: Semester identifier
        """
        try:
            client = await get_graphiti_client()
            namespace = get_student_namespace(student_id, course, semester)
            
            # Get learning history using search (from Step 06)
            history_results = await client.search(
                query=f"student {student_id} learning experience {current_topic}",
                group_id=namespace,
                limit=10
            )
            
            # Get student struggles and successes
            struggle_results = await client.search(
                query=f"student {student_id} struggled difficulty problem",
                group_id=namespace,
                limit=5
            )
            
            success_results = await client.search(
                query=f"student {student_id} mastered completed success",
                group_id=namespace,
                limit=5
            )
            
            # Get prerequisite information using fact triples (from Step 08)
            prereq_results = await client.search(
                query=f"prerequisite required before {current_topic}",
                group_id=namespace,
                limit=5
            )
            
            # Get student profile information
            profile_results = await client.search(
                query=f"student {student_id} learning style preferences",
                group_id=namespace,
                limit=3
            )
            
            # Build tutoring context using custom types (from Step 03)
            context = TutoringContext(
                student_id=student_id,
                current_topic=current_topic,
                learning_history=[{"fact": r.fact, "score": r.score} for r in history_results],
                mastery_status={},
                learning_preferences={
                    "style": "visual" if profile_results else "adaptive",
                    "pace": "normal"
                },
                recent_struggles=[r.fact for r in struggle_results],
                recent_successes=[r.fact for r in success_results],
                prerequisite_status={},
                recommended_approach=_generate_tutoring_approach(struggle_results, success_results, current_topic),
                engagement_tips=_generate_engagement_tips(profile_results, struggle_results),
                context_timestamp=datetime.now()
            )
            
            logger.info(f"Generated tutoring context for {student_id} on {current_topic}")
            return context.model_dump()
            
        except Exception as e:
            logger.error(f"Error generating tutoring context: {e}")
            return {"error": str(e)}

    @mcp.tool()
    async def analyze_learning_gaps(
        student_id: str,
        target_concept: str,
        course: str = "default",
        semester: str = "current"
    ) -> List[Dict[str, Any]]:
        """Identify knowledge gaps preventing mastery of target concept
        
        Args:
            student_id: Student identifier
            target_concept: Concept student wants to learn
            course: Course identifier
            semester: Semester identifier
        """
        try:
            client = await get_graphiti_client()
            namespace = get_student_namespace(student_id, course, semester)
            
            # Find prerequisites for target concept using search (from Step 06)
            prereq_results = await client.search(
                query=f"prerequisite required before {target_concept}",
                group_id=namespace,
                limit=10
            )
            
            # Check student's mastery of prerequisites
            mastery_results = await client.search(
                query=f"student {student_id} mastered completed",
                group_id=namespace,
                limit=15
            )
            
            gaps = []
            for prereq in prereq_results:
                # Simple gap detection logic
                prereq_mastered = any(prereq.fact.lower() in mastery.fact.lower() 
                                    for mastery in mastery_results)
                if not prereq_mastered:
                    gaps.append({
                        "missing_prerequisite": prereq.fact,
                        "importance": "high",
                        "recommendation": f"Complete {prereq.fact} before attempting {target_concept}",
                        "confidence": prereq.score
                    })
            
            # If no specific gaps found, check for general readiness
            if not gaps:
                # Check if student has any mastery in related areas
                related_mastery = [m for m in mastery_results 
                                 if any(word in m.fact.lower() 
                                       for word in target_concept.lower().split())]
                
                if not related_mastery:
                    gaps.append({
                        "missing_prerequisite": f"Basic knowledge in {target_concept} area",
                        "importance": "medium",
                        "recommendation": f"Start with foundational concepts before {target_concept}",
                        "confidence": 0.6
                    })
            
            logger.info(f"Identified {len(gaps)} learning gaps for {student_id}")
            return gaps
            
        except Exception as e:
            logger.error(f"Error analyzing learning gaps: {e}")
            return [{"error": str(e)}]

    @mcp.tool()
    async def get_learning_readiness(
        student_id: str,
        target_concepts: str,
        course: str = "default",
        semester: str = "current"
    ) -> Dict[str, Any]:
        """Assess student's readiness to learn specific concepts
        
        Args:
            student_id: Student identifier
            target_concepts: Comma-separated list of concepts to assess
            course: Course identifier
            semester: Semester identifier
        """
        try:
            client = await get_graphiti_client()
            namespace = get_student_namespace(student_id, course, semester)
            
            concepts = [c.strip() for c in target_concepts.split(",")]
            readiness_assessment = {}
            
            for concept in concepts:
                # Check prerequisites
                gaps = await analyze_learning_gaps(student_id, concept, course, semester)
                
                # Get student's current level in related areas
                related_results = await client.search(
                    query=f"student {student_id} {concept}",
                    group_id=namespace,
                    limit=5
                )
                
                # Calculate readiness score
                gap_penalty = len([g for g in gaps if g.get("importance") == "high"]) * 0.3
                related_bonus = min(len(related_results) * 0.1, 0.4)
                readiness_score = max(0.0, min(1.0, 0.5 - gap_penalty + related_bonus))
                
                readiness_assessment[concept] = {
                    "readiness_score": readiness_score,
                    "status": _get_readiness_status(readiness_score),
                    "gaps_count": len(gaps),
                    "related_experience": len(related_results),
                    "recommendation": _get_readiness_recommendation(readiness_score, gaps)
                }
            
            logger.info(f"Assessed learning readiness for {student_id}: {concepts}")
            return {
                "student_id": student_id,
                "assessment_date": datetime.now().isoformat(),
                "concepts_assessed": readiness_assessment,
                "overall_readiness": sum(r["readiness_score"] for r in readiness_assessment.values()) / len(readiness_assessment)
            }
            
        except Exception as e:
            logger.error(f"Error assessing learning readiness: {e}")
            return {"error": str(e)}

def _generate_tutoring_approach(struggles, successes, topic):
    """Generate recommended tutoring approach based on student history"""
    if struggles and len(struggles) > len(successes):
        return f"Use gentle, step-by-step approach for {topic}. Student has faced challenges recently."
    elif successes:
        return f"Build on recent successes. Student is gaining confidence with {topic}."
    else:
        return f"Use adaptive approach for {topic}. Assess understanding as you go."

def _generate_engagement_tips(profile_results, struggle_results):
    """Generate engagement tips based on student profile and history"""
    tips = ["Check understanding frequently", "Use concrete examples"]
    
    if profile_results:
        # Extract learning style hints from profile
        for result in profile_results:
            if "visual" in result.fact.lower():
                tips.append("Use diagrams and visual aids")
            elif "hands-on" in result.fact.lower() or "kinesthetic" in result.fact.lower():
                tips.append("Provide interactive exercises")
    
    if struggle_results:
        tips.append("Be patient and encouraging - student has faced recent challenges")
    
    return tips

def _get_readiness_status(score):
    """Convert readiness score to status"""
    if score >= 0.8:
        return "Ready"
    elif score >= 0.6:
        return "Nearly Ready"
    elif score >= 0.4:
        return "Needs Preparation"
    else:
        return "Not Ready"

def _get_readiness_recommendation(score, gaps):
    """Generate recommendation based on readiness score and gaps"""
    if score >= 0.8:
        return "Student is ready to begin learning this concept"
    elif score >= 0.6:
        return "Review prerequisites briefly, then proceed"
    elif gaps:
        return f"Address {len(gaps)} prerequisite gaps before proceeding"
    else:
        return "Build foundational knowledge before attempting this concept"