import asyncio
from typing import Dict, AsyncGenerator, Any
import json
import logging

logger = logging.getLogger(__name__)

class EventManager:
    def __init__(self):
        # Map session_id -> asyncio.Queue
        self._queues: Dict[str, asyncio.Queue] = {}

    def get_queue(self, session_id: str) -> asyncio.Queue:
        """Get or create an event queue for a session."""
        if session_id not in self._queues:
            self._queues[session_id] = asyncio.Queue()
        return self._queues[session_id]

    async def emit(self, session_id: str, event_type: str, data: Any):
        """Emit an event to a session's queue."""
        if session_id in self._queues:
            event = {
                "type": event_type,
                "data": data
            }
            await self._queues[session_id].put(event)
            logger.debug(f"Emitted event {event_type} to session {session_id}")

    async def stream(self, session_id: str) -> AsyncGenerator[str, None]:
        """Yield events from the session's queue as SSE messages."""
        queue = self.get_queue(session_id)
        
        try:
            while True:
                # Wait for next event
                event = await queue.get()
                
                # Format as SSE
                # data: <json_string>\n\n
                yield f"data: {json.dumps(event)}\n\n"
                
                queue.task_done()
                
                # Special event to close stream if needed (optional)
                if event["type"] == "end_stream":
                    break
                    
        except asyncio.CancelledError:
            logger.info(f"Stream cancelled for session {session_id}")
            # Cleanup could happen here, but we might want to keep queue for reconnection
            # For now, we'll just exit
            pass

# Global instance
event_manager = EventManager()
