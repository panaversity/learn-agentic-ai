# Nate - Team Calendar Agent (CrewAI) 👥

**Team coordination specialist built with CrewAI framework for collaborative scheduling**

> **🎯 Learning Objective**: Build a sophisticated team calendar agent using CrewAI framework that excels at multi-person coordination and integrates seamlessly with A2A protocol for cross-framework collaboration.

## 🧠 Learning Sciences Foundation

### **Collaborative Intelligence Theory**

- **Team Dynamics**: Understanding group scheduling complexity and coordination patterns
- **Framework Diversity**: Learning CrewAI's unique approach to agent development
- **Cross-Framework Integration**: Connecting CrewAI agents with A2A standard protocol

### **Group Coordination Psychology**

- **Social Scheduling**: Managing competing priorities and group preferences
- **Consensus Building**: Finding scheduling solutions that work for entire teams
- **Conflict Resolution**: Handling scheduling conflicts across multiple team members

## 🎯 What You'll Learn

### **Core Concepts**

- **CrewAI Agent Architecture** - Multi-agent crews and role-based coordination
- **Team Calendar Logic** - Group scheduling, consensus building, and coordination
- **A2A-CrewAI Integration** - Bridging CrewAI framework with A2A protocol
- **Collaborative Decision Making** - AI-powered group scheduling optimization

### **Practical Skills**

- Build team calendar agent with CrewAI framework
- Implement group scheduling algorithms and conflict resolution
- Integrate CrewAI agents with A2A messaging protocol
- Handle complex team coordination scenarios

### **Strategic Understanding**

- How CrewAI's collaborative approach differs from other frameworks
- Team scheduling challenges that require specialized AI approaches
- Cross-framework agent coordination in enterprise environments

## 📋 Prerequisites

✅ **Completed**: Host agent and Carly (ADK) understanding  
✅ **Knowledge**: A2A protocol and multi-agent coordination patterns  
✅ **Framework**: Basic understanding of CrewAI concepts  
✅ **Tools**: UV package manager, Python 3.10+, CrewAI framework

## 🎯 Nate's Team Coordination Specialization

### **Core Team Calendar Skills**

```
👥 Team Coordination Expertise
├── analyze_team_availability: Multi-member availability analysis
├── find_consensus_time: AI-powered group consensus building
├── resolve_scheduling_conflicts: Intelligent conflict resolution
├── optimize_meeting_cadence: Team meeting rhythm optimization
├── coordinate_recurring_events: Complex recurring meeting management
└── manage_team_preferences: Learn and apply team scheduling preferences
```

### **Table Tennis Team Coordination**

```
🏓 Team Sports Scheduling
├── coordinate_player_schedules: Multi-player availability coordination
├── balance_skill_levels: Ensure balanced game matchups
├── manage_team_tournaments: Complex tournament bracket scheduling
├── optimize_court_usage: Efficient court time allocation across teams
├── handle_weather_contingencies: Backup scheduling for weather issues
└── track_team_statistics: Performance and participation analytics
```

## 🏗️ CrewAI Implementation

### **Nate Team Agent Structure**

```python
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from a2a import AgentCard, AgentSkill, A2AMessageHandler
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

class NateTeamCalendarAgent:
    """Team calendar coordination agent using CrewAI framework"""

    def __init__(self):
        self.agent_id = "nate-team-calendar"
        self.logger = logging.getLogger(__name__)

        # Initialize CrewAI components
        self.setup_crew_agents()
        self.setup_a2a_integration()

    def setup_crew_agents(self):
        """Setup specialized CrewAI agents for team coordination"""

        # Calendar Analyst Agent
        self.calendar_analyst = Agent(
            role="Calendar Analyst",
            goal="Analyze team calendars and identify scheduling patterns",
            backstory="Expert at analyzing complex team schedules and finding optimal meeting times",
            tools=[self.analyze_team_calendars, self.find_common_availability],
            verbose=True
        )

        # Conflict Resolver Agent
        self.conflict_resolver = Agent(
            role="Scheduling Conflict Resolver",
            goal="Resolve scheduling conflicts and find alternative solutions",
            backstory="Specialist in negotiating scheduling conflicts and finding win-win solutions",
            tools=[self.resolve_conflicts, self.suggest_alternatives],
            verbose=True
        )

        # Consensus Builder Agent
        self.consensus_builder = Agent(
            role="Team Consensus Builder",
            goal="Build consensus around team scheduling decisions",
            backstory="Expert at facilitating group decisions and building team agreement",
            tools=[self.build_consensus, self.optimize_group_preferences],
            verbose=True
        )

        # Create coordination crew
        self.coordination_crew = Crew(
            agents=[self.calendar_analyst, self.conflict_resolver, self.consensus_builder],
            process=Process.hierarchical,
            manager_llm="gpt-4",
            verbose=True
        )

    def setup_a2a_integration(self):
        """Configure A2A protocol integration for CrewAI"""

        self.agent_card = AgentCard(
            agent_id=self.agent_id,
            name="Nate Team Calendar Agent",
            description="Specialized team calendar coordination using CrewAI multi-agent approach",
            skills=[
                AgentSkill(
                    name="coordinate_team_schedule",
                    description="Coordinate scheduling across multiple team members",
                    parameters={
                        "team_members": "List of team member email addresses",
                        "meeting_type": "Type of meeting or event to schedule",
                        "duration_minutes": "Meeting duration in minutes",
                        "constraints": "Scheduling constraints and preferences"
                    }
                ),
                AgentSkill(
                    name="resolve_team_conflicts",
                    description="Resolve scheduling conflicts across team calendars",
                    parameters={
                        "conflicting_events": "List of conflicting calendar events",
                        "priority_levels": "Priority levels for different events",
                        "flexibility_options": "Available flexibility for rescheduling"
                    }
                ),
                AgentSkill(
                    name="build_team_consensus",
                    description="Build consensus around team scheduling decisions",
                    parameters={
                        "proposed_times": "List of proposed meeting times",
                        "team_preferences": "Individual team member preferences",
                        "decision_criteria": "Criteria for making final decision"
                    }
                )
            ]
        )

        # A2A message handler
        self.a2a_handler = A2AMessageHandler(self.agent_card)
        self.a2a_handler.register_skill_handler(
            "coordinate_team_schedule",
            self.coordinate_team_schedule
        )
        self.a2a_handler.register_skill_handler(
            "resolve_team_conflicts",
            self.resolve_team_conflicts
        )
        self.a2a_handler.register_skill_handler(
            "build_team_consensus",
            self.build_team_consensus
        )

    async def coordinate_team_schedule(
        self,
        team_members: List[str],
        meeting_type: str,
        duration_minutes: int,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Coordinate scheduling across team members using CrewAI crew"""

        try:
            self.logger.info(f"Coordinating {meeting_type} for {len(team_members)} team members")

            # Create coordination task
            coordination_task = Task(
                description=f"""
                Coordinate a {meeting_type} meeting for {duration_minutes} minutes
                across team members: {', '.join(team_members)}.

                Constraints: {constraints or 'None specified'}

                Your task is to:
                1. Analyze each team member's calendar availability
                2. Identify potential scheduling conflicts
                3. Find optimal meeting times that work for everyone
                4. Build consensus around the best option
                5. Provide detailed recommendation with alternatives
                """,
                agent=self.calendar_analyst,
                expected_output="Detailed scheduling recommendation with consensus analysis"
            )

            # Execute coordination through CrewAI crew
            result = self.coordination_crew.kickoff(tasks=[coordination_task])

            # Parse and structure the result
            return {
                "success": True,
                "meeting_type": meeting_type,
                "team_members": team_members,
                "duration_minutes": duration_minutes,
                "recommendation": self._parse_crew_recommendation(result),
                "consensus_analysis": self._extract_consensus_analysis(result),
                "alternatives": self._extract_alternatives(result),
                "coordination_method": "CrewAI multi-agent collaboration",
                "processed_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Team coordination failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "meeting_type": meeting_type,
                "team_members": team_members
            }

    @tool("Analyze team calendars for availability patterns")
    def analyze_team_calendars(self, team_members: List[str]) -> Dict[str, Any]:
        """Analyze team member calendars to identify availability patterns"""

        # Simulate calendar analysis (in production, integrate with real calendar APIs)
        availability_analysis = {}

        for member in team_members:
            # Simulate getting calendar data
            availability_analysis[member] = {
                "typical_free_hours": "9 AM - 5 PM weekdays",
                "preferred_meeting_times": ["10 AM - 12 PM", "2 PM - 4 PM"],
                "recurring_conflicts": ["Monday 9 AM - 10 AM", "Friday 3 PM - 5 PM"],
                "time_zone": "UTC-8",
                "meeting_load": "moderate"  # light, moderate, heavy
            }

        return {
            "team_size": len(team_members),
            "availability_patterns": availability_analysis,
            "team_synchronization_score": 0.85,  # How well-aligned the team schedules are
            "optimal_meeting_windows": [
                {"start": "10:00", "end": "11:30", "days": ["Tuesday", "Wednesday", "Thursday"]},
                {"start": "14:00", "end": "15:30", "days": ["Monday", "Tuesday", "Wednesday"]}
            ]
        }

    @tool("Find common availability across team members")
    def find_common_availability(
        self,
        team_analysis: Dict[str, Any],
        duration_minutes: int
    ) -> List[Dict[str, Any]]:
        """Find time slots available to all team members"""

        common_slots = []

        # Simulate finding common availability
        optimal_windows = team_analysis.get("optimal_meeting_windows", [])

        for window in optimal_windows:
            for day in window["days"]:
                common_slots.append({
                    "day": day,
                    "start_time": window["start"],
                    "end_time": window["end"],
                    "available_duration": 90,  # minutes
                    "team_agreement_score": 0.9,
                    "can_accommodate_duration": 90 >= duration_minutes
                })

        return sorted(common_slots, key=lambda x: x["team_agreement_score"], reverse=True)

    @tool("Resolve scheduling conflicts intelligently")
    def resolve_conflicts(
        self,
        conflicts: List[Dict[str, Any]],
        priorities: Dict[str, int]
    ) -> Dict[str, Any]:
        """Resolve scheduling conflicts using intelligent prioritization"""

        resolution_strategies = []

        for conflict in conflicts:
            # Analyze conflict and propose solutions
            strategy = {
                "conflict_id": conflict.get("id", "unknown"),
                "conflict_type": conflict.get("type", "time_overlap"),
                "affected_members": conflict.get("members", []),
                "resolution_options": [
                    {
                        "option": "reschedule_lower_priority",
                        "description": "Move lower priority meeting to alternative time",
                        "feasibility": 0.8,
                        "impact_score": 0.3
                    },
                    {
                        "option": "shorten_meetings",
                        "description": "Reduce meeting durations to eliminate overlap",
                        "feasibility": 0.6,
                        "impact_score": 0.5
                    },
                    {
                        "option": "split_participants",
                        "description": "Have subset attend each meeting",
                        "feasibility": 0.4,
                        "impact_score": 0.7
                    }
                ]
            }
            resolution_strategies.append(strategy)

        return {
            "total_conflicts": len(conflicts),
            "resolution_strategies": resolution_strategies,
            "recommended_approach": "reschedule_lower_priority",
            "estimated_resolution_time": "15 minutes",
            "success_probability": 0.85
        }

    @tool("Build consensus around scheduling decisions")
    def build_consensus(
        self,
        proposed_times: List[Dict[str, Any]],
        team_preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build team consensus around scheduling decisions"""

        consensus_analysis = []

        for time_option in proposed_times:
            # Calculate consensus score for each option
            consensus_score = 0
            member_feedback = {}

            for member, preferences in team_preferences.items():
                # Simulate preference matching
                member_score = 0.7  # Base acceptance

                # Adjust based on preferences
                if time_option.get("start_time", "") in preferences.get("preferred_times", []):
                    member_score += 0.2

                if time_option.get("day", "") in preferences.get("preferred_days", []):
                    member_score += 0.1

                member_feedback[member] = {
                    "acceptance_score": min(1.0, member_score),
                    "concerns": preferences.get("concerns", []),
                    "suggestions": preferences.get("suggestions", [])
                }

                consensus_score += member_score

            # Average consensus score
            consensus_score = consensus_score / len(team_preferences)

            consensus_analysis.append({
                "time_option": time_option,
                "consensus_score": consensus_score,
                "member_feedback": member_feedback,
                "unanimous": all(
                    feedback["acceptance_score"] > 0.8
                    for feedback in member_feedback.values()
                )
            })

        # Sort by consensus score
        consensus_analysis.sort(key=lambda x: x["consensus_score"], reverse=True)

        return {
            "consensus_options": consensus_analysis,
            "recommended_option": consensus_analysis[0] if consensus_analysis else None,
            "team_alignment_score": consensus_analysis[0]["consensus_score"] if consensus_analysis else 0,
            "consensus_building_strategy": "preference_weighted_voting"
        }

    def _parse_crew_recommendation(self, crew_result: str) -> Dict[str, Any]:
        """Parse CrewAI crew result into structured recommendation"""

        # In production, this would parse the actual CrewAI output
        # For demo purposes, return structured example
        return {
            "recommended_time": "Tuesday 10:00 AM - 11:00 AM",
            "confidence_score": 0.92,
            "team_agreement": "High",
            "reasoning": "Optimal time based on team availability analysis and preference matching"
        }

    def _extract_consensus_analysis(self, crew_result: str) -> Dict[str, Any]:
        """Extract consensus analysis from crew result"""

        return {
            "consensus_method": "CrewAI collaborative decision making",
            "agreement_level": "Strong consensus",
            "dissenting_opinions": 0,
            "compromise_factors": ["Time zone accommodation", "Meeting duration optimization"]
        }

    def _extract_alternatives(self, crew_result: str) -> List[Dict[str, Any]]:
        """Extract alternative options from crew result"""

        return [
            {
                "option": "Wednesday 2:00 PM - 3:00 PM",
                "consensus_score": 0.85,
                "trade_offs": ["Later in week", "Post-lunch timing"]
            },
            {
                "option": "Thursday 10:30 AM - 11:30 AM",
                "consensus_score": 0.78,
                "trade_offs": ["Slightly later start", "End of week timing"]
            }
        ]
```

## 🎮 Testing Scenarios

### **Scenario 1: Team Meeting Coordination**

```bash
# Test team scheduling coordination
curl -X POST http://localhost:8003/message/send \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "agent_id": "nate-team-calendar",
      "message": {
        "role": "user",
        "content": "Coordinate a team Table Tennis practice for alice@team.com, bob@team.com, charlie@team.com tomorrow for 90 minutes"
      }
    },
    "id": "team-coord-123"
  }'
```

### **Scenario 2: Complex Conflict Resolution**

```bash
# Test conflict resolution capabilities
curl -X POST http://localhost:8003/resolve/conflicts \
  -H "Content-Type: application/json" \
  -d '{
    "conflicts": [
      {"id": "conf1", "type": "overlap", "members": ["alice", "bob"]},
      {"id": "conf2", "type": "priority", "members": ["charlie", "dave"]}
    ],
    "priorities": {"meeting1": 5, "meeting2": 3}
  }'
```

## 🌟 Motivation & Relevance

### **Real-World Connection**

```
👥 Enterprise Team Coordination
"Nate represents sophisticated team coordination AI that
handles complex group dynamics - essential for modern
remote and hybrid work environments."
```

### **Personal Relevance**

```
🚀 Multi-Agent Framework Skills
"Learning CrewAI demonstrates how different frameworks
approach agent collaboration. This multi-framework
knowledge is valuable for choosing the right tool."
```

### **Immediate Reward**

```
⚡ Team Intelligence
"See Nate's CrewAI agents collaborate to solve complex
team scheduling problems that involve multiple competing
priorities and preferences!"
```

## 📊 Success Metrics

### **Technical Validation**

- [ ] CrewAI framework properly integrated with A2A protocol
- [ ] Multi-agent crew coordination working effectively
- [ ] Complex team scheduling logic handling group dynamics
- [ ] Cross-framework communication with host agent

### **Team Coordination Intelligence**

- [ ] Effective analysis of multi-member availability patterns
- [ ] Intelligent conflict resolution with win-win solutions
- [ ] Consensus building that respects individual preferences
- [ ] Graceful handling of complex team dynamics

## 📖 Learning Resources

### **Primary Resources**

- [CrewAI Framework Documentation](https://github.com/joaomdmoura/crewAI)
- [CrewAI Agent Coordination Patterns](https://docs.crewai.com/concepts/agents)
- [A2A-CrewAI Integration Guide](https://google-a2a.github.io/A2A/latest/sdk/crewai/)

### **Extension Resources**

- Team coordination psychology and best practices
- Group decision making algorithms and consensus building
- Enterprise team scheduling optimization strategies

---

## 🚀 Ready to Build Nate?

**Next Action**: Implement the team coordination specialist with CrewAI framework!

```bash
# Setup Nate's CrewAI environment
pip install crewai langchain-openai
python3 setup_nate.py
```

**Remember**: Nate showcases how CrewAI's collaborative approach excels at team coordination problems. The multi-agent crew patterns you build here demonstrate the power of agent collaboration within a single framework! 👥
