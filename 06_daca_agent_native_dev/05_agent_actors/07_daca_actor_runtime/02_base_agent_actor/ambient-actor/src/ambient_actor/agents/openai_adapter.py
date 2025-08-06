from typing import Literal
from dataclasses import dataclass
import os

from agents import Agent, Runner, Tool, RunResult, RunResultStreaming
from ambient_actor.agents.engine_adapter import AgenticEngineAdapter
from agents.extensions.models.litellm_model import LitellmModel

@dataclass
class OpenAIEngineAdapter(AgenticEngineAdapter):
    agent: Agent | None = None

    async def initialize(self, agent_name: str, agent_instructions: str, agent_tools: list[Tool], model: str) -> None:
        self.agent = Agent(
            name=agent_name,
            instructions=agent_instructions,
            tools=agent_tools,
            model=LitellmModel(model=model, api_key=os.getenv("GEMINI_API_KEY"))
        )
    
    async def process_input(
        self, 
        input_text: str | list[dict[str, str]],
        run_method: Literal["run", "run_sync", 'stream'],
        context: dict[str, object] | None = None,
    ) -> dict[str, object]:  # Changed return type to match base class
        result: RunResult | RunResultStreaming | None = None
        if self.agent is None or run_method is None:
            raise ValueError("Agent not initialized")

        if run_method == "run":
            result = await Runner.run(
                self.agent,
                input=input_text,
                context=context
            )
        elif run_method == "run_sync":
            result = Runner.run_sync(
                self.agent,
                input=input_text,
                context=context
            )
        elif run_method == "stream":
            raise NotImplementedError("Streaming is not supported for OpenAI")
            # result = Runner.run_streamed(
            #     self.agent,
            #     input=input_text,
            #     context=context
            # )
        
        return {
            "conversation": result.to_input_list(),
            "run_method": run_method,
            "final_output": result.final_output
        }