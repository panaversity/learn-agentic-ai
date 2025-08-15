import asyncio
import httpx

from datetime import datetime

from a2a.server.apps import A2AFastAPIApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.server.events import EventQueue, InMemoryQueueManager
from a2a.server.tasks import InMemoryPushNotificationConfigStore, BasePushNotificationSender
from a2a.types import (
    AgentCard, AgentCapabilities, Part, TextPart, TaskState
)

class LongRunningExecutor(AgentExecutor):
    """Simple agent that demonstrates webhook notifications."""

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Cancel the current task."""
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.update_status(
            TaskState.failed,
            message=updater.new_agent_message([
                Part(root=TextPart(text="❌ Task cancelled"))
            ])
        )
        
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        
        try:
            # Initialize task
            if not context.current_task:
                await updater.submit()
            await updater.start_work()
            
            user_input = context.get_user_input()
            
            # Simple notification that webhook might be configured
            await updater.update_status(
                TaskState.working,
                message=updater.new_agent_message([
                    Part(root=TextPart(text="📡 Starting long task - webhook notifications supported!"))
                ])
            )
            
            # Simulate long-running work
            await self._handle_long_task(user_input, updater)
                
        except Exception as e:
            await updater.update_status(
                TaskState.failed,
                message=updater.new_agent_message([
                    Part(root=TextPart(text=f"❌ Task failed: {str(e)}"))
                ])
            )
    
    async def _handle_long_task(self, user_input: str, updater: TaskUpdater):
        """Handle long task with progress updates."""
        
        await updater.update_status(
            TaskState.working,
            message=updater.new_agent_message([
                Part(root=TextPart(text="🚀 Starting long task (20 seconds)..."))
            ])
        )
        
        # Simulate work with progress updates
        for i in range(4):
            print(f"🔄 Processing step {i+1}/4...")
            progress = ((i + 1) / 4) * 100
            
            await updater.update_status(
                TaskState.working,
                message=updater.new_agent_message([
                    Part(root=TextPart(text=f"⚙️ Processing step {i+1}/4 ({progress:.0f}% complete)"))
                ])
            )
        
        # Complete with results
        result = f"✅ Task completed!\n\nInput: '{user_input}'\nCompleted at: {datetime.now().isoformat()}"
        
        await updater.add_artifact(
            [Part(root=TextPart(text=result))],
            name="task_result"
        )
        
        await updater.complete()

# Simple agent card
agent_card = AgentCard(
    name="Long-Running Task Agent",
    description="Demonstrates A2A push notifications",
    url="http://localhost:8001/",
    version="1.0.0",
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=True,
        state_transition_history=True
    ),
    skills=[],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport="JSONRPC"
)

if __name__ == "__main__":
    # Set up push notification components
    client = httpx.AsyncClient(timeout=30.0)
    push_config_store = InMemoryPushNotificationConfigStore()
    push_sender = BasePushNotificationSender(httpx_client=client, config_store=push_config_store)
    
    request_handler = DefaultRequestHandler(
        agent_executor=LongRunningExecutor(),
        task_store=InMemoryTaskStore(),
        queue_manager=InMemoryQueueManager(),
        push_config_store=push_config_store,
        push_sender=push_sender
    )
    
    server = A2AFastAPIApplication(agent_card=agent_card, http_handler=request_handler)
    
    print("🚀 Starting Long-Running Task Agent on port 8001...")
    print("📡 Push Notifications: Enabled")
    
    import uvicorn
    uvicorn.run(server.build(), host="localhost", port=8001)