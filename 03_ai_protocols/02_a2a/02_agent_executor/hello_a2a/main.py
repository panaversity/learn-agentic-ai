from fastapi import FastAPI

from a2a.server.apps import A2AFastAPIApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.events import InMemoryQueueManager
from basic_executor import SimpleCalendarExecutor

from basic_discovery import agent_card

request_handler = DefaultRequestHandler(
    agent_executor=SimpleCalendarExecutor(),  # Your agent logic
    task_store=InMemoryTaskStore(),          # Memory for tasks
    queue_manager=InMemoryQueueManager()
)

# Create the A2A-compliant server
server = A2AFastAPIApplication(
    agent_card=agent_card,  # Your agent's business card
    http_handler=request_handler     # Your request processor
)

app: FastAPI = server.build()