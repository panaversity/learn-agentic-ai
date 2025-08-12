import asyncio
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.server.events import EventQueue, InMemoryQueueManager
from a2a.types import AgentCard, AgentCapabilities, Part, TextPart, TaskState

class BasicStreamingExecutor(AgentExecutor):
    """Demonstrates A2A streaming with TaskStatusUpdateEvent and TaskArtifactUpdateEvent."""

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # Step 1: Set up TaskUpdater for streaming
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)

        # Step 2: Start the task (creates initial Task event)
        if not context.current_task:
            await updater.submit()  # Streams: {"kind": "task", "id": "task-123"}
        await updater.start_work()  # Changes state to "working"

        user_input = context.get_user_input()
        print(f"🎯 Processing: {user_input}")

        # Step 3: Stream progress updates (TaskStatusUpdateEvent)
        progress_steps = [
            "🚀 Initializing...",
            "📊 Processing your request...",
            "🔍 Analyzing data...",
            "📝 Generating response..."
        ]

        for i, step in enumerate(progress_steps):
            # This streams a TaskStatusUpdateEvent
            await updater.update_status(
                TaskState.working,
                message=updater.new_agent_message([
                    Part(root=TextPart(text=f"{step} ({i+1}/{len(progress_steps)})"))
                ])
            )
            await asyncio.sleep(1)  # Simulate work

        # Step 4: Create and stream the final result (TaskArtifactUpdateEvent)
        result_text = f"✅ Completed processing: '{user_input}'\n\nProcessed at: {asyncio.get_event_loop().time()}"

        await updater.add_artifact(
            [Part(root=TextPart(text=result_text))],
            name="processing_result"
        )

        # Step 5: Complete the task (final TaskStatusUpdateEvent with final=true)
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.update_status(
            TaskState.canceled,
            message=updater.new_agent_message([
                Part(root=TextPart(text="❌ Task was cancelled"))
            ])
        )

# Agent Card with streaming enabled
agent_card = AgentCard(
    name="Basic Streaming Agent",
    description="Demonstrates A2A streaming with real-time updates",
    url="http://localhost:8001/",
    version="1.0.0",
    capabilities=AgentCapabilities(
        streaming=True,  # REQUIRED for A2A streaming
        push_notifications=False,
        state_transition_history=False
    ),
    skills=[],
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport="JSONRPC"
)

if __name__ == "__main__":
    # Create the A2A server with streaming support
    request_handler = DefaultRequestHandler(
        agent_executor=BasicStreamingExecutor(),
        task_store=InMemoryTaskStore(),
        queue_manager=InMemoryQueueManager()
    )

    server = A2AFastAPIApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )

    print("🚀 Starting Basic Streaming Agent on port 8001...")
    print("🔗 Agent Card: http://localhost:8001/.well-known/agent-card.json")
    print("📮 A2A Endpoint: http://localhost:8001")

    import uvicorn
    uvicorn.run(server.build(), host="localhost", port=8001)