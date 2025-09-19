# ambient_actor/agents/engine_adapter.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

@dataclass
class AgenticEngineAdapter(ABC):
    """Abstract adapter for any agentic engine"""
    
    @abstractmethod
    async def initialize(self, agent_name: str, agent_instructions: str, agent_tools: list[Any], model: str | Any) -> None:
        """Initialize the engine with configuration"""
        pass
    
    @abstractmethod
    async def process_input(
        self, 
        input_text: str | list[dict[str, str]],
        run_method: Literal["run", "run_sync", 'stream'],
        context: dict[str, object] | None = None,
    ) -> dict[str, object]:
        """Process input through the engine"""
        pass