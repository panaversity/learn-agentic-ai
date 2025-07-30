"""
In-memory event store for demonstrating resumability functionality.

This is a simple implementation intended for examples and testing,
not for production use where a persistent storage solution would be more appropriate.
"""

import logging
from collections import deque
from dataclasses import dataclass
from uuid import uuid4

from mcp.server.streamable_http import (
    EventCallback,
    EventId,
    EventMessage,
    EventStore,
    StreamId,
)
from mcp.types import JSONRPCMessage

logger = logging.getLogger(__name__)


@dataclass
class EventEntry:
    """
    Represents an event entry in the event store.
    """

    event_id: EventId
    stream_id: StreamId
    message: JSONRPCMessage


class InMemoryEventStore(EventStore):
    """
    Simple in-memory implementation of the EventStore interface for resumability.
    This is primarily intended for examples and testing, not for production use
    where a persistent storage solution would be more appropriate.

    This implementation keeps only the last N events per stream for memory efficiency.
    """

    def __init__(self, max_events_per_stream: int = 100):
        """Initialize the event store.

        Args:
            max_events_per_stream: Maximum number of events to keep per stream
        """
        self.max_events_per_stream = max_events_per_stream
        # for maintaining last N events per stream
        self.streams: dict[StreamId, deque[EventEntry]] = {}
        # event_id -> EventEntry for quick lookup
        self.event_index: dict[EventId, EventEntry] = {}

    async def store_event(
        self, stream_id: StreamId, message: JSONRPCMessage
    ) -> EventId:
        """Stores an event with a generated event ID."""
        event_id = str(uuid4())
        event_entry = EventEntry(
            event_id=event_id, 
            stream_id=stream_id, 
            message=message
        )

        # Get or create deque for this stream
        if stream_id not in self.streams:
            self.streams[stream_id] = deque(maxlen=self.max_events_per_stream)

        # If deque is full, the oldest event will be automatically removed
        # We need to remove it from the event_index as well
        if len(self.streams[stream_id]) == self.max_events_per_stream:
            oldest_event = self.streams[stream_id][0]
            self.event_index.pop(oldest_event.event_id, None)

        # Add new event
        self.streams[stream_id].append(event_entry)
        self.event_index[event_id] = event_entry

        print(f"🏪 Stored event {event_id} in stream {stream_id}")
        return event_id

    async def replay_events_after(
        self,
        last_event_id: EventId,
        send_callback: EventCallback,
    ) -> StreamId | None:
        """Replays events that occurred after the specified event ID across ALL streams."""
        print(f"🔄 Replaying events after {last_event_id}")
        if last_event_id not in self.event_index:
            logger.warning(f"Event ID {last_event_id} not found in store")
            return None

        # Get the last known event
        last_event = self.event_index[last_event_id]
        print(f"🔄 Last event stream: {last_event.stream_id}")

        # Search across ALL streams for events that came after the last event
        events_to_replay = []
        
        for stream_id, stream_events in self.streams.items():
            print(f"🔄 Checking stream {stream_id} with {len(stream_events)} events")
            
            # If this is the same stream as the last event, find events after it
            if stream_id == last_event.stream_id:
                found_last = False
                for event in stream_events:
                    if found_last:
                        events_to_replay.append(event)
                        print(f"🔄 Found event to replay: {event.event_id} in same stream {stream_id}")
                    elif event.event_id == last_event_id:
                        found_last = True
            else:
                # Different stream - include ALL events (they all came after initialization)
                for event in stream_events:
                    events_to_replay.append(event)
                    print(f"🔄 Found event to replay: {event.event_id} in different stream {stream_id}")

        print(f"🔄 Found {len(events_to_replay)} events to replay")

        # Send all events
        for event in events_to_replay:
            print(f"🔄 Sending event: {event.event_id} from stream {event.stream_id}")
            await send_callback(EventMessage(event.message, event.event_id))

        # Return the original stream ID for compatibility
        return last_event.stream_id
