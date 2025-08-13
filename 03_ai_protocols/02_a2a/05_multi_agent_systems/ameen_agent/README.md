# Carly - Calendar Agent (ADK) 📅

**Specialized calendar management agent built with Google's Agent Development Kit**

> **🎯 Learning Objective**: Build a production-ready calendar agent using ADK framework that integrates seamlessly with A2A protocol for multi-agent coordination.

## 🧠 Learning Sciences Foundation

### **Specialization Learning Theory**

- **Domain Expertise**: Deep focus on calendar and scheduling domain knowledge
- **Framework Mastery**: Advanced ADK patterns and best practices
- **Integration Skills**: Connecting domain logic with standardized A2A communication

### **Professional Agent Development**

- **Production Patterns**: Building agents that work in enterprise environments
- **API Integration**: Connecting with real calendar services (Google, Outlook)
- **Error Handling**: Robust calendar operations with graceful failure handling

## 🎯 What You'll Learn

### **Core Concepts**

- **ADK Agent Architecture** - Professional agent structure and patterns
- **Calendar Domain Logic** - Scheduling, availability, and conflict resolution
- **A2A Integration** - Seamless protocol integration with ADK
- **Production Readiness** - Error handling, logging, and monitoring

### **Practical Skills**

- Build production calendar agent with ADK framework
- Integrate with real calendar APIs (Google Calendar, Outlook)
- Implement complex scheduling logic and conflict resolution
- Handle edge cases and error scenarios gracefully

### **Strategic Understanding**

- How specialized agents contribute to multi-agent ecosystems
- ADK framework advantages for production agent development
- Calendar agent patterns that apply across business domains

## 📋 Prerequisites

✅ **Completed**: Host agent foundation understanding  
✅ **Knowledge**: ADK framework basics and A2A protocol  
✅ **API Access**: Google Calendar API credentials (optional but recommended)  
✅ **Tools**: UV package manager, Python 3.10+, ADK SDK

## 🎯 Carly's Specialized Capabilities

### **Core Calendar Skills**

```
📅 Calendar Agent Expertise
├── check_availability: Find free time slots for individuals/groups
├── schedule_meeting: Book meetings with conflict detection
├── find_optimal_time: AI-powered optimal scheduling
├── get_busy_times: Extract busy periods from calendars
├── suggest_alternatives: Propose alternative meeting times
└── manage_recurring: Handle recurring meeting patterns
```

### **Table Tennis Scheduling Specialization**

```
🏓 Table Tennis-Specific Features
├── check_player_availability: Multi-player scheduling
├── find_court_time_slots: Integrate with court booking systems
├── weather_aware_scheduling: Consider outdoor court conditions
├── tournament_coordination: Complex multi-game scheduling
├── equipment_availability: Track paddle and ball availability
└── skill_level_matching: Schedule appropriate skill-level games
```

## 🏗️ ADK Implementation

### **Carly Agent Structure**

```python
from google.adk import Agent, Skill, Context, Tool
from google.calendar import CalendarService
from a2a import AgentCard, AgentSkill
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

class CarlyCalendarAgent(Agent):
    """Specialized calendar agent using ADK framework"""

    def __init__(self):
        super().__init__(
            agent_id="carly-calendar",
            name="Carly Calendar Agent",
            description="Specialized calendar and scheduling management"
        )

        # Initialize calendar service
        self.calendar_service = CalendarService()
        self.logger = logging.getLogger(__name__)

        # Configure A2A integration
        self.configure_a2a_integration()

    def configure_a2a_integration(self):
        """Configure A2A protocol integration"""
        self.agent_card = AgentCard(
            agent_id=self.agent_id,
            name=self.name,
            description=self.description,
            skills=[
                AgentSkill(
                    name="check_availability",
                    description="Check calendar availability for specified time periods",
                    parameters={
                        "start_time": "ISO 8601 datetime string",
                        "end_time": "ISO 8601 datetime string",
                        "participants": "List of email addresses"
                    }
                ),
                AgentSkill(
                    name="schedule_meeting",
                    description="Schedule a meeting with conflict detection",
                    parameters={
                        "title": "Meeting title",
                        "start_time": "ISO 8601 datetime string",
                        "duration_minutes": "Meeting duration in minutes",
                        "participants": "List of email addresses"
                    }
                ),
                AgentSkill(
                    name="find_optimal_time",
                    description="Find optimal meeting time for all participants",
                    parameters={
                        "participants": "List of email addresses",
                        "duration_minutes": "Meeting duration in minutes",
                        "preferred_times": "Preferred time ranges",
                        "deadline": "Latest acceptable meeting date"
                    }
                )
            ]
        )

    @Skill(name="check_availability")
    async def check_availability(
        self,
        context: Context,
        start_time: str,
        end_time: str,
        participants: List[str]
    ) -> Dict[str, Any]:
        """Check calendar availability for specified participants and time"""

        try:
            self.logger.info(f"Checking availability for {len(participants)} participants")

            # Convert time strings to datetime objects
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

            # Query calendar service for each participant
            availability_results = {}

            for participant in participants:
                try:
                    busy_times = await self.calendar_service.get_busy_times(
                        participant, start_dt, end_dt
                    )

                    free_slots = self._calculate_free_slots(
                        start_dt, end_dt, busy_times
                    )

                    availability_results[participant] = {
                        "available": len(free_slots) > 0,
                        "free_slots": free_slots,
                        "busy_times": busy_times,
                        "total_free_hours": sum(
                            slot['duration_hours'] for slot in free_slots
                        )
                    }

                except Exception as e:
                    self.logger.error(f"Error checking {participant}: {e}")
                    availability_results[participant] = {
                        "available": False,
                        "error": str(e)
                    }

            # Find common availability
            common_slots = self._find_common_availability(availability_results)

            return {
                "success": True,
                "availability": availability_results,
                "common_slots": common_slots,
                "recommendation": self._generate_availability_recommendation(
                    common_slots
                ),
                "checked_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Availability check failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "checked_at": datetime.utcnow().isoformat()
            }

    @Skill(name="find_optimal_time")
    async def find_optimal_time(
        self,
        context: Context,
        participants: List[str],
        duration_minutes: int,
        preferred_times: Optional[List[str]] = None,
        deadline: Optional[str] = None
    ) -> Dict[str, Any]:
        """Find optimal meeting time using AI-powered scheduling"""

        try:
            # Set search window
            search_start = datetime.utcnow()
            search_end = datetime.fromisoformat(deadline) if deadline else (
                search_start + timedelta(days=14)
            )

            self.logger.info(
                f"Finding optimal time for {len(participants)} participants, "
                f"{duration_minutes} minutes, deadline: {deadline}"
            )

            # Get availability for all participants
            availability = await self.check_availability(
                context,
                search_start.isoformat(),
                search_end.isoformat(),
                participants
            )

            if not availability["success"]:
                return availability

            # Apply AI optimization
            optimal_slots = await self._optimize_scheduling(
                availability["common_slots"],
                duration_minutes,
                preferred_times,
                participants
            )

            return {
                "success": True,
                "optimal_slots": optimal_slots,
                "recommendation": optimal_slots[0] if optimal_slots else None,
                "alternatives": optimal_slots[1:5] if len(optimal_slots) > 1 else [],
                "optimization_factors": {
                    "participant_preferences": "analyzed",
                    "time_zone_optimization": "applied",
                    "meeting_length_efficiency": "optimized",
                    "calendar_fragmentation": "minimized"
                },
                "confidence_score": self._calculate_confidence_score(optimal_slots)
            }

        except Exception as e:
            self.logger.error(f"Optimal time finding failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @Tool(name="calendar_integration")
    async def _optimize_scheduling(
        self,
        common_slots: List[Dict[str, Any]],
        duration_minutes: int,
        preferred_times: Optional[List[str]],
        participants: List[str]
    ) -> List[Dict[str, Any]]:
        """Apply AI optimization to scheduling decisions"""

        scored_slots = []

        for slot in common_slots:
            slot_start = datetime.fromisoformat(slot["start_time"])
            slot_duration = slot["duration_hours"] * 60  # Convert to minutes

            # Skip slots too short for meeting
            if slot_duration < duration_minutes:
                continue

            # Calculate optimization score
            score = 0

            # Time preference scoring
            if preferred_times:
                for pref_time in preferred_times:
                    if self._time_matches_preference(slot_start, pref_time):
                        score += 10

            # Business hours scoring (9 AM - 5 PM gets higher score)
            hour = slot_start.hour
            if 9 <= hour <= 17:
                score += 5

            # Participant count efficiency
            score += min(len(participants), 5)  # Cap at 5 points

            # Morning meetings get slight preference
            if hour < 12:
                score += 2

            # Avoid fragmentation (prefer longer slots)
            if slot_duration > duration_minutes * 2:
                score += 3

            scored_slots.append({
                **slot,
                "score": score,
                "meeting_start": slot_start.isoformat(),
                "meeting_end": (slot_start + timedelta(minutes=duration_minutes)).isoformat(),
                "duration_minutes": duration_minutes
            })

        # Sort by score descending
        scored_slots.sort(key=lambda x: x["score"], reverse=True)

        return scored_slots

    def _calculate_free_slots(
        self,
        start_dt: datetime,
        end_dt: datetime,
        busy_times: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Calculate free time slots from busy times"""

        # Convert busy times to datetime objects
        busy_periods = []
        for busy in busy_times:
            busy_start = datetime.fromisoformat(busy["start"])
            busy_end = datetime.fromisoformat(busy["end"])
            busy_periods.append((busy_start, busy_end))

        # Sort busy periods by start time
        busy_periods.sort(key=lambda x: x[0])

        free_slots = []
        current_time = start_dt

        for busy_start, busy_end in busy_periods:
            # Add free slot before this busy period
            if current_time < busy_start:
                duration = busy_start - current_time
                free_slots.append({
                    "start_time": current_time.isoformat(),
                    "end_time": busy_start.isoformat(),
                    "duration_hours": duration.total_seconds() / 3600
                })

            current_time = max(current_time, busy_end)

        # Add final free slot after last busy period
        if current_time < end_dt:
            duration = end_dt - current_time
            free_slots.append({
                "start_time": current_time.isoformat(),
                "end_time": end_dt.isoformat(),
                "duration_hours": duration.total_seconds() / 3600
            })

        return free_slots
```

## 🎮 Testing Scenarios

### **Scenario 1: Simple Availability Check**

```bash
# Test Carly's availability checking
curl -X POST http://localhost:8002/message/send \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "agent_id": "carly-calendar",
      "message": {
        "role": "user",
        "content": "Check availability tomorrow 2-4 PM for john@example.com and jane@example.com"
      }
    },
    "id": "availability-123"
  }'
```

### **Scenario 2: Optimal Time Finding**

```bash
# Test AI-powered optimal scheduling
curl -X POST http://localhost:8002/schedule/optimal \
  -H "Content-Type: application/json" \
  -d '{
    "participants": ["alice@example.com", "bob@example.com", "charlie@example.com"],
    "duration_minutes": 60,
    "preferred_times": ["morning", "afternoon"],
    "deadline": "2024-12-31T23:59:59Z"
  }'
```

## 🌟 Motivation & Relevance

### **Real-World Connection**

```
📅 Enterprise Calendar Intelligence
"Carly represents real enterprise calendar AI - systems that
coordinate hundreds of employees, conference rooms, and
resources across global time zones automatically."
```

### **Personal Relevance**

```
🚀 Domain Expertise Skills
"Building specialized agents like Carly teaches you to
combine domain knowledge with AI frameworks - essential
for creating valuable business applications."
```

### **Immediate Reward**

```
⚡ Smart Scheduling
"See Carly intelligently solve complex scheduling problems
that would take humans hours to figure out manually!"
```

## 📊 Success Metrics

### **Technical Validation**

- [ ] ADK framework properly integrated with A2A protocol
- [ ] Calendar API integration working with real data
- [ ] Complex scheduling logic handling edge cases
- [ ] Performance meets multi-agent coordination requirements

### **Calendar Intelligence**

- [ ] Accurate availability checking across multiple participants
- [ ] AI-powered optimal time finding with preference learning
- [ ] Conflict detection and resolution recommendations
- [ ] Graceful handling of calendar API failures

## 📖 Learning Resources

### **Primary Resources**

- [ADK Agent Development Guide](https://google-adk.github.io/docs/agents/)
- [Google Calendar API Documentation](https://developers.google.com/calendar/api)
- [A2A-ADK Integration Patterns](https://google-a2a.github.io/A2A/latest/sdk/adk/)

### **Extension Resources**

- Enterprise calendar integration patterns
- AI-powered scheduling optimization techniques
- Multi-calendar coordination strategies

---

## 🚀 Ready to Build Carly?

**Next Action**: Implement the specialized calendar agent with ADK framework!

```bash
# Setup Carly's environment
pip install google-adk google-calendar-api
python3 setup_carly.py
```

**Remember**: Carly demonstrates how specialized agents excel in specific domains while seamlessly integrating with multi-agent systems. The calendar intelligence you build here showcases the power of focused AI expertise! 📅
