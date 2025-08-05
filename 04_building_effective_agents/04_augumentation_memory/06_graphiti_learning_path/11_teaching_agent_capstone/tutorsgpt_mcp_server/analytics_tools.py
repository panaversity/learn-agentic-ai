"""
Learning Analytics Tools for TutorsGPT Memory MCP Server
Leverages search (Step 06), episodes (Step 02), and custom types (Step 03)
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from educational_types import LearningAnalytics

logger = logging.getLogger(__name__)

def setup_analytics_tools(mcp, get_graphiti_client, get_student_namespace):
    """Setup learning analytics and insights tools"""
    
    @mcp.tool()
    async def get_learning_insights(
        student_id: str,
        time_period: str = "last_30_days",
        course: str = "default",
        semester: str = "current"
    ) -> Dict[str, Any]:
        """Generate comprehensive learning analytics and insights for a student
        
        Args:
            student_id: Student identifier
            time_period: Analysis time period (last_7_days, last_30_days, semester)
            course: Course identifier
            semester: Semester identifier
        """
        try:
            client = await get_graphiti_client()
            namespace = get_student_namespace(student_id, course, semester)
            
            # Get all learning episodes using episodes (from Step 02)
            episodes = await client.get_episodes(
                group_id=namespace,
                last_n=100
            )
            
            # Search for mastery and completion facts using search (from Step 06)
            mastery_results = await client.search(
                query=f"student {student_id} mastered completed",
                group_id=namespace,
                limit=50
            )
            
            struggle_results = await client.search(
                query=f"student {student_id} struggled difficulty",
                group_id=namespace,
                limit=20
            )
            
            # Analyze learning patterns
            concepts_mastered = len([r for r in mastery_results if "mastered" in r.fact.lower()])
            concepts_completed = len([r for r in mastery_results if "completed" in r.fact.lower()])
            concepts_struggling = len(struggle_results)
            
            # Calculate learning velocity (concepts per week)
            weeks_active = max(1, len(episodes) // 7)  # Rough estimate
            learning_velocity = concepts_mastered / weeks_active
            
            # Identify strength and improvement areas
            strength_areas = _identify_strength_areas(mastery_results)
            improvement_areas = _identify_improvement_areas(struggle_results)
            
            # Generate learning patterns
            learning_patterns = _analyze_learning_patterns(episodes, mastery_results)
            
            # Create analytics using custom types (from Step 03)
            analytics = LearningAnalytics(
                student_id=student_id,
                analysis_period=time_period,
                total_learning_time_hours=len(episodes) * 0.5,  # Rough estimate
                concepts_mastered=concepts_mastered,
                concepts_in_progress=concepts_completed,
                average_mastery_score=_calculate_average_score(mastery_results),
                learning_velocity=learning_velocity,
                engagement_trends={"weekly_sessions": len(episodes) / weeks_active},
                strength_areas=strength_areas,
                improvement_areas=improvement_areas,
                learning_patterns=learning_patterns,
                recommendations=_generate_recommendations(concepts_mastered, concepts_struggling, learning_velocity),
                generated_at=datetime.now()
            )
            
            logger.info(f"Generated learning insights for {student_id}")
            return analytics.model_dump()
            
        except Exception as e:
            logger.error(f"Error generating learning insights: {e}")
            return {"error": str(e)}

    @mcp.tool()
    async def get_progress_summary(
        student_id: str,
        subject: str = "all",
        course: str = "default",
        semester: str = "current"
    ) -> Dict[str, Any]:
        """Get a summary of student's learning progress
        
        Args:
            student_id: Student identifier
            subject: Specific subject or "all" for overall progress
            course: Course identifier
            semester: Semester identifier
        """
        try:
            client = await get_graphiti_client()
            namespace = get_student_namespace(student_id, course, semester)
            
            # Build search query based on subject
            if subject.lower() == "all":
                search_query = f"student {student_id} progress mastery"
            else:
                search_query = f"student {student_id} {subject} progress mastery"
            
            # Get progress information
            progress_results = await client.search(
                query=search_query,
                group_id=namespace,
                limit=25
            )
            
            # Get recent learning activity
            recent_episodes = await client.get_episodes(
                group_id=namespace,
                last_n=10
            )
            
            # Categorize progress
            mastered_concepts = []
            in_progress_concepts = []
            struggling_concepts = []
            
            for result in progress_results:
                fact = result.fact.lower()
                if "mastered" in fact:
                    mastered_concepts.append(result.fact)
                elif "completed" in fact:
                    in_progress_concepts.append(result.fact)
                elif "struggled" in fact:
                    struggling_concepts.append(result.fact)
            
            # Calculate progress metrics
            total_concepts = len(set(mastered_concepts + in_progress_concepts + struggling_concepts))
            mastery_rate = len(mastered_concepts) / max(1, total_concepts)
            
            summary = {
                "student_id": student_id,
                "subject": subject,
                "summary_date": datetime.now().isoformat(),
                "total_concepts_encountered": total_concepts,
                "concepts_mastered": len(mastered_concepts),
                "concepts_in_progress": len(in_progress_concepts),
                "concepts_struggling": len(struggling_concepts),
                "mastery_rate": mastery_rate,
                "recent_activity_count": len(recent_episodes),
                "latest_achievements": mastered_concepts[-3:] if mastered_concepts else [],
                "areas_needing_attention": struggling_concepts[-3:] if struggling_concepts else [],
                "overall_status": _determine_overall_status(mastery_rate, len(recent_episodes))
            }
            
            logger.info(f"Generated progress summary for {student_id} in {subject}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating progress summary: {e}")
            return {"error": str(e)}

    @mcp.tool()
    async def compare_learning_patterns(
        student_id: str,
        comparison_period: str = "last_month_vs_previous",
        course: str = "default",
        semester: str = "current"
    ) -> Dict[str, Any]:
        """Compare student's learning patterns across different time periods
        
        Args:
            student_id: Student identifier
            comparison_period: Type of comparison to perform
            course: Course identifier
            semester: Semester identifier
        """
        try:
            client = await get_graphiti_client()
            namespace = get_student_namespace(student_id, course, semester)
            
            # Get all episodes for pattern analysis
            all_episodes = await client.get_episodes(
                group_id=namespace,
                last_n=100
            )
            
            # Get all mastery results
            all_mastery = await client.search(
                query=f"student {student_id} mastered completed struggled",
                group_id=namespace,
                limit=50
            )
            
            # Split data into periods (simplified - would use actual dates in production)
            recent_episodes = all_episodes[:len(all_episodes)//2]
            older_episodes = all_episodes[len(all_episodes)//2:]
            
            recent_mastery = all_mastery[:len(all_mastery)//2]
            older_mastery = all_mastery[len(all_mastery)//2:]
            
            # Calculate metrics for each period
            recent_metrics = _calculate_period_metrics(recent_episodes, recent_mastery)
            older_metrics = _calculate_period_metrics(older_episodes, older_mastery)
            
            # Generate comparison
            comparison = {
                "student_id": student_id,
                "comparison_type": comparison_period,
                "comparison_date": datetime.now().isoformat(),
                "recent_period": recent_metrics,
                "previous_period": older_metrics,
                "improvements": _identify_improvements(recent_metrics, older_metrics),
                "concerns": _identify_concerns(recent_metrics, older_metrics),
                "trend_analysis": _analyze_trends(recent_metrics, older_metrics),
                "recommendations": _generate_comparison_recommendations(recent_metrics, older_metrics)
            }
            
            logger.info(f"Generated learning pattern comparison for {student_id}")
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing learning patterns: {e}")
            return {"error": str(e)}

def _identify_strength_areas(mastery_results):
    """Identify areas where student shows strength"""
    strengths = []
    subject_counts = {}
    
    for result in mastery_results:
        if "mastered" in result.fact.lower():
            # Extract subject/topic from fact (simplified)
            words = result.fact.lower().split()
            for word in words:
                if word not in ["student", "mastered", "completed", "with", "score"]:
                    subject_counts[word] = subject_counts.get(word, 0) + 1
    
    # Get top subjects
    sorted_subjects = sorted(subject_counts.items(), key=lambda x: x[1], reverse=True)
    strengths = [subject for subject, count in sorted_subjects[:3] if count > 1]
    
    return strengths if strengths else ["General problem solving"]

def _identify_improvement_areas(struggle_results):
    """Identify areas needing improvement"""
    improvements = []
    struggle_topics = {}
    
    for result in struggle_results:
        # Extract topics from struggle facts
        words = result.fact.lower().split()
        for word in words:
            if word not in ["student", "struggled", "with", "difficulty"]:
                struggle_topics[word] = struggle_topics.get(word, 0) + 1
    
    # Get most struggled topics
    sorted_topics = sorted(struggle_topics.items(), key=lambda x: x[1], reverse=True)
    improvements = [topic for topic, count in sorted_topics[:3]]
    
    return improvements if improvements else ["Time management"]

def _analyze_learning_patterns(episodes, mastery_results):
    """Analyze learning patterns from episodes and mastery data"""
    patterns = {}
    
    # Session frequency pattern
    if len(episodes) > 10:
        patterns["session_frequency"] = "Regular learner"
    elif len(episodes) > 5:
        patterns["session_frequency"] = "Moderate activity"
    else:
        patterns["session_frequency"] = "Infrequent sessions"
    
    # Mastery pattern
    mastery_count = len([r for r in mastery_results if "mastered" in r.fact.lower()])
    if mastery_count > 5:
        patterns["mastery_pattern"] = "Quick to master concepts"
    elif mastery_count > 2:
        patterns["mastery_pattern"] = "Steady progress"
    else:
        patterns["mastery_pattern"] = "Needs more practice"
    
    return patterns

def _calculate_average_score(mastery_results):
    """Calculate average score from mastery results"""
    scores = []
    for result in mastery_results:
        # Try to extract score from fact (simplified)
        words = result.fact.split()
        for i, word in enumerate(words):
            if word.lower() == "score" and i + 1 < len(words):
                try:
                    score = int(words[i + 1])
                    scores.append(score)
                except ValueError:
                    continue
    
    return sum(scores) / len(scores) if scores else 75.0

def _generate_recommendations(mastered_count, struggling_count, velocity):
    """Generate learning recommendations based on analytics"""
    recommendations = []
    
    if mastered_count > struggling_count * 2:
        recommendations.append("Excellent progress! Consider advancing to more challenging topics.")
    elif struggling_count > mastered_count:
        recommendations.append("Focus on reinforcing fundamental concepts before advancing.")
    
    if velocity < 0.5:
        recommendations.append("Consider increasing study frequency for better learning momentum.")
    elif velocity > 2.0:
        recommendations.append("Great learning pace! Ensure understanding is solid before moving on.")
    
    recommendations.append("Continue with current learning approach - showing good progress.")
    
    return recommendations

def _determine_overall_status(mastery_rate, recent_activity):
    """Determine overall learning status"""
    if mastery_rate > 0.8 and recent_activity > 5:
        return "Excellent - High mastery with active engagement"
    elif mastery_rate > 0.6 and recent_activity > 3:
        return "Good - Solid progress with regular activity"
    elif mastery_rate > 0.4:
        return "Developing - Making progress, needs consistency"
    else:
        return "Needs Support - Consider additional help or review"

def _calculate_period_metrics(episodes, mastery_results):
    """Calculate metrics for a specific time period"""
    return {
        "episode_count": len(episodes),
        "mastery_count": len([r for r in mastery_results if "mastered" in r.fact.lower()]),
        "struggle_count": len([r for r in mastery_results if "struggled" in r.fact.lower()]),
        "engagement_score": min(10, len(episodes))
    }

def _identify_improvements(recent, older):
    """Identify improvements between periods"""
    improvements = []
    
    if recent["mastery_count"] > older["mastery_count"]:
        improvements.append("Increased concept mastery")
    if recent["episode_count"] > older["episode_count"]:
        improvements.append("More active learning")
    if recent["struggle_count"] < older["struggle_count"]:
        improvements.append("Fewer struggles with concepts")
    
    return improvements

def _identify_concerns(recent, older):
    """Identify concerns between periods"""
    concerns = []
    
    if recent["mastery_count"] < older["mastery_count"]:
        concerns.append("Decreased mastery rate")
    if recent["episode_count"] < older["episode_count"]:
        concerns.append("Reduced learning activity")
    if recent["struggle_count"] > older["struggle_count"]:
        concerns.append("Increased difficulty with concepts")
    
    return concerns

def _analyze_trends(recent, older):
    """Analyze trends between periods"""
    if not older["episode_count"]:
        return "Insufficient historical data for trend analysis"
    
    activity_change = (recent["episode_count"] - older["episode_count"]) / older["episode_count"]
    
    if activity_change > 0.2:
        return "Increasing engagement trend"
    elif activity_change < -0.2:
        return "Decreasing engagement trend"
    else:
        return "Stable engagement pattern"

def _generate_comparison_recommendations(recent, older):
    """Generate recommendations based on period comparison"""
    recommendations = []
    
    if recent["mastery_count"] < older["mastery_count"]:
        recommendations.append("Consider reviewing recent learning methods")
    if recent["episode_count"] < older["episode_count"]:
        recommendations.append("Encourage more frequent learning sessions")
    if recent["struggle_count"] > older["struggle_count"]:
        recommendations.append("Provide additional support for challenging concepts")
    
    if not recommendations:
        recommendations.append("Continue current learning approach - showing consistent progress")
    
    return recommendations