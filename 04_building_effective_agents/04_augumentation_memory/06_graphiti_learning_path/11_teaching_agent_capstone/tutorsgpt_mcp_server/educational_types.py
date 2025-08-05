"""
Educational Domain Types for TutorsGPT Memory MCP Server
Leverages custom types knowledge from Step 03
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Student(BaseModel):
    """A learner with comprehensive educational profile"""
    student_id: str = Field(..., description="Unique student identifier")
    name: str = Field(..., description="Student's full name")
    learning_style: str = Field(..., description="Visual, Auditory, Kinesthetic, Reading/Writing")
    current_level: str = Field(..., description="Beginner, Intermediate, Advanced")
    preferred_pace: str = Field(..., description="Slow, Normal, Fast")
    grade_level: Optional[str] = Field(None, description="Academic grade level")
    subjects: List[str] = Field(default_factory=list, description="Enrolled subjects")
    learning_goals: List[str] = Field(default_factory=list, description="Current learning objectives")
    special_needs: Optional[str] = Field(None, description="Any special learning accommodations")


class Concept(BaseModel):
    """A learning concept or topic"""
    concept_id: str = Field(..., description="Unique concept identifier")
    name: str = Field(..., description="Concept name")
    subject: str = Field(..., description="Subject area (e.g., Mathematics, Programming)")
    difficulty_level: str = Field(..., description="Beginner, Intermediate, Advanced")
    prerequisites: List[str] = Field(default_factory=list, description="Required prerequisite concepts")
    learning_objectives: List[str] = Field(default_factory=list, description="What students should learn")
    estimated_time_minutes: Optional[int] = Field(None, description="Estimated learning time")


class LearningSession(BaseModel):
    """A specific learning interaction or session"""
    session_id: str = Field(..., description="Unique session identifier")
    student_id: str = Field(..., description="Student participating in session")
    concept: str = Field(..., description="Main concept being learned")
    session_type: str = Field(..., description="Tutorial, Practice, Assessment, Review")
    start_time: datetime = Field(..., description="When session started")
    duration_minutes: int = Field(..., description="Session duration")
    engagement_score: int = Field(..., description="Student engagement level (1-10)")
    difficulty_rating: int = Field(..., description="Student's perceived difficulty (1-10)")
    concepts_covered: List[str] = Field(default_factory=list, description="All concepts touched")
    learning_outcomes: List[str] = Field(default_factory=list, description="What was accomplished")
    notes: Optional[str] = Field(None, description="Additional session notes")


class Assessment(BaseModel):
    """An assessment or evaluation of student knowledge"""
    assessment_id: str = Field(..., description="Unique assessment identifier")
    student_id: str = Field(..., description="Student being assessed")
    concept: str = Field(..., description="Concept being assessed")
    assessment_type: str = Field(..., description="Quiz, Test, Project, Practice, Informal")
    score: int = Field(..., description="Score achieved (0-100)")
    max_score: int = Field(default=100, description="Maximum possible score")
    completion_time_minutes: Optional[int] = Field(None, description="Time taken to complete")
    areas_of_strength: List[str] = Field(default_factory=list, description="What student did well")
    areas_for_improvement: List[str] = Field(default_factory=list, description="What needs work")
    feedback: Optional[str] = Field(None, description="Detailed feedback")
    assessment_date: datetime = Field(..., description="When assessment was taken")


class Mastery(BaseModel):
    """Student's mastery level of a specific concept"""
    student_id: str = Field(..., description="Student identifier")
    concept: str = Field(..., description="Concept mastered")
    proficiency_score: int = Field(..., description="Mastery level (0-100)")
    confidence_level: int = Field(..., description="Student's confidence (1-10)")
    last_assessed: datetime = Field(..., description="When mastery was last evaluated")
    learning_path: str = Field(..., description="How mastery was achieved")
    time_to_mastery_hours: Optional[float] = Field(None, description="Time invested to achieve mastery")
    mastery_evidence: List[str] = Field(default_factory=list, description="Evidence of mastery")


class LearningEvent(BaseModel):
    """A significant learning event or milestone"""
    event_id: str = Field(..., description="Unique event identifier")
    student_id: str = Field(..., description="Student involved")
    event_type: str = Field(..., description="struggle, breakthrough, mastery, confusion, insight")
    concept: str = Field(..., description="Related concept")
    description: str = Field(..., description="What happened")
    emotional_state: str = Field(..., description="frustrated, excited, confused, confident, etc.")
    context: str = Field(..., description="Situational context")
    timestamp: datetime = Field(..., description="When event occurred")
    impact_score: int = Field(..., description="Significance of event (1-10)")


class Prerequisite(BaseModel):
    """Prerequisite relationship between concepts"""
    prerequisite_concept: str = Field(..., description="Required concept")
    target_concept: str = Field(..., description="Concept that requires prerequisite")
    relationship_type: str = Field(..., description="Required, Recommended, Helpful")
    strength: str = Field(..., description="Strong, Moderate, Weak")
    explanation: str = Field(..., description="Why this prerequisite is needed")


class LearningResource(BaseModel):
    """A learning resource or material"""
    resource_id: str = Field(..., description="Unique resource identifier")
    title: str = Field(..., description="Resource title")
    resource_type: str = Field(..., description="Video, Article, Practice, Interactive, Book")
    concept: str = Field(..., description="Primary concept covered")
    difficulty_level: str = Field(..., description="Beginner, Intermediate, Advanced")
    learning_style_match: List[str] = Field(default_factory=list, description="Suitable learning styles")
    estimated_time_minutes: int = Field(..., description="Time to complete")
    url: Optional[str] = Field(None, description="Resource URL if available")
    description: str = Field(..., description="Resource description")
    quality_rating: Optional[float] = Field(None, description="Quality rating (1-5)")


class TutoringContext(BaseModel):
    """Rich context for AI tutoring sessions"""
    student_id: str = Field(..., description="Student identifier")
    current_topic: str = Field(..., description="Topic being tutored")
    learning_history: List[Dict[str, Any]] = Field(default_factory=list, description="Relevant learning history")
    mastery_status: Dict[str, int] = Field(default_factory=dict, description="Concept mastery scores")
    learning_preferences: Dict[str, Any] = Field(default_factory=dict, description="How student learns best")
    recent_struggles: List[str] = Field(default_factory=list, description="Recent difficulties")
    recent_successes: List[str] = Field(default_factory=list, description="Recent achievements")
    prerequisite_status: Dict[str, bool] = Field(default_factory=dict, description="Prerequisite completion")
    recommended_approach: str = Field(..., description="Suggested tutoring approach")
    engagement_tips: List[str] = Field(default_factory=list, description="How to keep student engaged")
    context_timestamp: datetime = Field(..., description="When context was generated")


class LearningAnalytics(BaseModel):
    """Learning analytics and insights for a student"""
    student_id: str = Field(..., description="Student identifier")
    analysis_period: str = Field(..., description="Time period analyzed")
    total_learning_time_hours: float = Field(..., description="Total time spent learning")
    concepts_mastered: int = Field(..., description="Number of concepts mastered")
    concepts_in_progress: int = Field(..., description="Number of concepts being learned")
    average_mastery_score: float = Field(..., description="Average mastery across all concepts")
    learning_velocity: float = Field(..., description="Concepts mastered per week")
    engagement_trends: Dict[str, float] = Field(default_factory=dict, description="Engagement over time")
    strength_areas: List[str] = Field(default_factory=list, description="Student's strongest areas")
    improvement_areas: List[str] = Field(default_factory=list, description="Areas needing attention")
    learning_patterns: Dict[str, Any] = Field(default_factory=dict, description="Identified learning patterns")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    generated_at: datetime = Field(..., description="When analytics were generated")


# Relationship types for fact triples (from Step 08)
class EducationalRelationships:
    """Standard relationship types for educational fact triples"""
    
    # Student relationships
    ENROLLED_IN = "ENROLLED_IN"
    COMPLETED = "COMPLETED"
    MASTERED = "MASTERED"
    STRUGGLED_WITH = "STRUGGLED_WITH"
    INTERESTED_IN = "INTERESTED_IN"
    PREFERS = "PREFERS"
    
    # Concept relationships  
    PREREQUISITE_FOR = "PREREQUISITE_FOR"
    BUILDS_ON = "BUILDS_ON"
    RELATED_TO = "RELATED_TO"
    PART_OF = "PART_OF"
    APPLIES_TO = "APPLIES_TO"
    
    # Assessment relationships
    ASSESSES = "ASSESSES"
    SCORED = "SCORED"
    DEMONSTRATES = "DEMONSTRATES"
    REQUIRES = "REQUIRES"
    
    # Learning relationships
    LEARNED_THROUGH = "LEARNED_THROUGH"
    TAUGHT_BY = "TAUGHT_BY"
    PRACTICED_WITH = "PRACTICED_WITH"
    REINFORCED_BY = "REINFORCED_BY"