from a2a.types import AgentCapabilities, AgentCard, AgentSkill

# 🎯 CONCEPT 3: Agent Skills (What You Advertise to Others)
agent_skills = [
    AgentSkill(
        id="check_availability",           # Unique identifier
        name="Check Availability",        # Human-readable name
        description="Check free time slots for given dates and times",  # What it does
        # Categories for discovery
        tags=["calendar", "availability", "scheduling"],
        examples=[  # Help other agents/users understand usage
            "Am I free tomorrow at 9 PM?",
            "What's my availability this week?",
            "Check if Tuesday afternoon is open"
        ]
    )
]

# 🎯 CONCEPT 4: Agent Card (Your Digital Business Card)
agent_card = AgentCard(
    # Basic Identity
    name="Personal Agent",
    description="Manages scheduling, availability, and calendar coordination using A2A SDK",
    url="http://localhost:8000",        # Where to find this agent
    version="1.0.0",                     # Version for compatibility

    # Communication Formats (What languages this agent speaks)
    # What it can receive
    default_input_modes=["text/plain", "application/json"],
    default_output_modes=["application/json",
                          "text/plain"],  # What it can send

    # Technical Capabilities (Advanced features)
    capabilities=AgentCapabilities(
        streaming=False,                 # Can send real-time updates?
        push_notifications=True,          # Can send alerts?
        state_transition_history=False     # Tracks conversation history?
    ),

    # Available Skills (What this agent can do)
    skills=agent_skills,
    preferred_transport="JSONRPC"
)
