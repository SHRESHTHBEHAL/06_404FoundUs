# backend/app/main.py
"""
FastAPI backend for Travel Planning Assistant MVP.
Handles session management, chat endpoints, and WebSocket connections.
"""

import asyncio
import time
import uuid
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import (
    ConversationTurn,
    SharedState,
    ActiveRun,
    AgentType,
    Intent,
    FlightResult,
    HotelResult,
)

# Import the compiled graph
from .graph.travel_graph import travel_graph
from .services.event_manager import event_manager


# ============================================================================
# Request/Response Models (specific to endpoints)
# ============================================================================

class MessageIn(BaseModel):
    """Incoming message payload."""
    message: str


class SessionState(BaseModel):
    """State for a single user session."""
    session_id: str
    history: List[ConversationTurn] = []
    shared_state: SharedState = SharedState()  # LangGraph state


# ============================================================================
# In-Memory Storage
# ============================================================================

# Session storage: session_id -> SessionState
sessions: Dict[str, SessionState] = {}

# Active run registry for interruption handling
# Maps session_id -> ActiveRun metadata
active_runs: Dict[str, ActiveRun] = {}

# Maps session_id -> asyncio.Task (cannot be in Pydantic model)
active_tasks: Dict[str, asyncio.Task] = {}


# ============================================================================
# WebSocket Connection Manager
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections per session."""
    
    def __init__(self):
        # session_id -> list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket):
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)
    
    def disconnect(self, session_id: str, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)
            # Clean up empty session lists
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
    
    async def send_json(self, session_id: str, data: dict):
        """Broadcast JSON data to all connections for a session."""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    # Connection might be closed; skip silently
                    print(f"Error sending to websocket: {e}")


manager = ConnectionManager()


# ============================================================================
# Session Helpers
# ============================================================================

def get_or_create_session(session_id: Optional[str]) -> SessionState:
    """
    Get existing session or create a new one.
    If session_id is None, generates a new UUID.
    """
    if session_id is None:
        session_id = uuid.uuid4().hex
    
    if session_id not in sessions:
        sessions[session_id] = SessionState(session_id=session_id, history=[])
        # Initialize session_id in shared state
        sessions[session_id].shared_state.session_id = session_id
    
    return sessions[session_id]


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Travel Assistant API",
    description="Multi-agent travel planning assistant with LangGraph",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Routes
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


async def run_graph_background(session_id: str, request_id: str):
    """
    Background task to run the LangGraph agent.
    """
    print(f"[Background] Starting run for session {session_id}, request {request_id}")
    session = get_or_create_session(session_id)
    
    try:
        # Compress conversation history if needed (before processing)
        from .services.summarization import compress_history
        session.shared_state = compress_history(session.shared_state)
        
        # Send status update
        await manager.send_json(session_id, {
            "type": "status",
            "status": "processing",
            "session_id": session_id
        })
        
        # Execute the graph with async invoke
        # LangGraph nodes are now async, so we use ainvoke
        result_state = await travel_graph.ainvoke(session.shared_state)
        
        # LangGraph returns a dict, convert back to SharedState
        if isinstance(result_state, dict):
            session.shared_state = SharedState(**result_state)
        else:
            session.shared_state = result_state
        
        # Check if this run was interrupted by comparing run IDs
        # If current_run_id changed, this run is stale
        if session.shared_state.current_run_id != request_id:
            print(f"[Background] Run {request_id} was superseded by {session.shared_state.current_run_id}, skipping broadcast")
            return
        
        # Check the interrupted flag as well
        if session.shared_state.is_interrupted:
            print(f"[Background] Run was interrupted, skipping result broadcast")
            await manager.send_json(session_id, {
                "type": "status",
                "status": "cancelled",
                "session_id": session_id
            })
            return
        
        # Get the latest assistant response from conversation history
        assistant_messages = [
            turn for turn in session.shared_state.conversation_history 
            if turn.sender == "assistant"
        ]
        
        if assistant_messages:
            latest_response = assistant_messages[-1]
            
            # Broadcast assistant response
            await manager.send_json(session_id, {
                "type": "message",
                "sender": "assistant",
                "text": latest_response.text,
                "session_id": session_id,
                "request_id": request_id
            })
            
            # Broadcast results based on intent to manage UI state
            current_intent = session.shared_state.current_intent
            
            # Handle Flight Results
            if current_intent in [Intent.FLIGHT, Intent.COMBINED]:
                # Show flights
                if session.shared_state.flight_results:
                    await manager.send_json(session_id, {
                        "type": "flight_results",
                        "results": [f.model_dump() for f in session.shared_state.flight_results],
                        "session_id": session_id
                    })
            elif current_intent == Intent.HOTEL:
                # Explicitly hide flights when switching to hotel view
                await manager.send_json(session_id, {
                    "type": "flight_results",
                    "results": [],
                    "session_id": session_id
                })
            
            # Handle Hotel Results
            if current_intent in [Intent.HOTEL, Intent.COMBINED]:
                # Show hotels
                if session.shared_state.hotel_results:
                    await manager.send_json(session_id, {
                        "type": "hotel_results",
                        "results": [h.model_dump() for h in session.shared_state.hotel_results],
                        "session_id": session_id
                    })
            elif current_intent == Intent.FLIGHT:
                # Explicitly hide hotels when switching to flight view
                await manager.send_json(session_id, {
                    "type": "hotel_results",
                    "results": [],
                    "session_id": session_id
                })
            
            # Broadcast preference updates if new preferences were learned
            if session.shared_state.user_preferences.preference_items:
                latest_pref = session.shared_state.user_preferences.preference_items[-1]
                # Check if this preference was just added (within last 2 seconds)
                if time.time() - latest_pref.timestamp < 2:
                    await manager.send_json(session_id, {
                        "type": "preference_update",
                        "preference": {
                            "category": latest_pref.category,
                            "value": latest_pref.value
                        },
                        "session_id": session_id
                    })
                    print(f"[Preferences] Broadcasted new preference: {latest_pref.category}={latest_pref.value}")
                
            # Note: For Intent.OTHER or Intent.REFINE, we do not send empty lists.
            # This allows the frontend to preserve its current state (e.g. showing results while asking questions),
            # or respect the user's manual clearing (e.g. after clicking "Select").
        
        # Send completion status
        await manager.send_json(session_id, {
            "type": "status",
            "status": "completed",
            "session_id": session_id
        })
        
    except asyncio.CancelledError:
        print(f"[Background] Run cancelled for session {session_id}")
        await manager.send_json(session_id, {
            "type": "status",
            "status": "cancelled",
            "session_id": session_id
        })
        # Re-raise to ensure task is marked as cancelled
        raise
        
    except Exception as e:
        print(f"[Background] Error executing graph: {e}")
        await manager.send_json(session_id, {
            "type": "error",
            "error": str(e),
            "session_id": session_id
        })
    finally:
        # Cleanup active run
        if session_id in active_runs:
            del active_runs[session_id]
        if session_id in active_tasks:
            del active_tasks[session_id]
        print(f"[Background] Run finished for session {session_id}")


@app.post("/chat/{session_id}/message")
async def post_message(session_id: str, payload: MessageIn):
    """
    Receive a user message and queue agent orchestration.
    
    This endpoint:
    - Appends the message to session history
    - Triggers LangGraph execution
    - Broadcasts results to WebSocket clients
    - Returns 202 Accepted
    """
    # Get or create session
    session = get_or_create_session(session_id)
    
    # Create conversation turn for user message
    user_turn = ConversationTurn(
        sender="user",
        text=payload.message,
        timestamp=time.time()
    )
    session.history.append(user_turn)
    session.shared_state.conversation_history.append(user_turn)
    
    # Generate request ID for tracking
    request_id = uuid.uuid4().hex
    
    # Broadcast user message to WebSocket clients
    await manager.send_json(session_id, {
        "type": "message",
        "sender": "user",
        "text": payload.message,
        "session_id": session_id,
        "request_id": request_id
    })
    
    # Check for active run and handle interruption
    if session_id in active_runs:
        print(f"[Interruption] Active run found for session {session_id}. Cancelling previous run.")
        
        # Mark the session state as interrupted
        session.shared_state.is_interrupted = True
        
        # Clear old results to prevent context pollution
        # This ensures the new request starts fresh
        # BUT preserve user selections and booking state
        session.shared_state.flight_results = []
        session.shared_state.hotel_results = []
        session.shared_state.flight_params = None
        session.shared_state.hotel_params = None
        # NOTE: We intentionally preserve:
        # - selected_flight_id, selected_hotel_id
        # - pending_flight_booking, pending_hotel_booking
        # This allows users to continue their booking flow across interruptions
        
        # Notify frontend of cancellation
        await manager.send_json(session_id, {
            "type": "status",
            "status": "cancelling_previous",
            "session_id": session_id
        })
        
        # Cancel the existing task
        if session_id in active_tasks:
            existing_task = active_tasks[session_id]
            existing_task.cancel()
            
            # Wait for cancellation to complete (with timeout)
            try:
                await asyncio.wait_for(existing_task, timeout=2.0)
            except asyncio.CancelledError:
                print(f"[Interruption] Previous task cancelled successfully")
            except asyncio.TimeoutError:
                print(f"[Interruption] Timeout waiting for task cancellation")
            except Exception as e:
                print(f"[Interruption] Error during cancellation: {e}")
    
    # Reset interruption flag for new run
    session.shared_state.is_interrupted = False
    session.shared_state.current_run_id = request_id
    
    # Create new active run metadata
    run_id = uuid.uuid4().hex
    active_run = ActiveRun(
        run_id=run_id,
        agent_type=AgentType.COORDINATOR, # Initial agent
        started_at=time.time(),
        session_id=session_id
    )
    active_runs[session_id] = active_run
    
    # Start background task
    task = asyncio.create_task(run_graph_background(session_id, request_id))
    active_tasks[session_id] = task
    
    # Return 202 Accepted
    return Response(
        content='{"status": "accepted", "session_id": "' + session_id + '", "request_id": "' + request_id + '"}',
        media_type="application/json"
    )


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates per session."""
    await manager.connect(session_id, websocket)
    print(f"WebSocket connected for session {session_id}")
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received WebSocket message from {session_id}: {data}")
            await websocket.send_json({
                "type": "echo",
                "data": data,
            })
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)
        print(f"WebSocket disconnected for session {session_id}")


@app.get("/chat/{session_id}/stream")
async def stream_events(session_id: str):
    """
    Server-Sent Events (SSE) endpoint for real-time updates.
    Streams agent status, tokens, and results.
    """
    return StreamingResponse(
        event_manager.stream(session_id),
        media_type="text/event-stream"
    )


@app.get("/chat/{session_id}/history")
async def get_conversation_history(session_id: str):
    """
    Retrieve full conversation history including summaries.
    
    Returns:
        JSON with conversation history and summaries
    """
    session = get_or_create_session(session_id)
    
    return {
        "session_id": session_id,
        "conversation_history": [
            {
                "sender": turn.sender,
                "text": turn.text,
                "timestamp": turn.timestamp,
                "run_id": turn.run_id
            }
            for turn in session.shared_state.conversation_history
        ],
        "conversation_summaries": [
            {
                "summary": summary.summary,
                "turn_count": summary.turn_count,
                "start_timestamp": summary.start_timestamp,
                "end_timestamp": summary.end_timestamp
            }
            for summary in session.shared_state.conversation_summaries
        ]
    }


@app.get("/chat/{session_id}/preferences")
async def get_user_preferences(session_id: str):
    """
    Get current user preferences for a session.
    
    Returns:
        JSON with learned preferences
    """
    session = get_or_create_session(session_id)
    prefs = session.shared_state.user_preferences
    
    from .services.preferences import get_preference_summary
    
    return {
        "session_id": session_id,
        "preferences": {
            "preferred_flight_time": prefs.preferred_flight_time,
            "preferred_cabin_class": prefs.preferred_cabin_class,
            "preferred_airlines": prefs.preferred_airlines,
            "max_stops": prefs.max_stops,
            "min_hotel_rating": prefs.min_hotel_rating,
            "preferred_hotel_budget": prefs.preferred_hotel_budget,
            "preferred_amenities": prefs.preferred_amenities,
            "preferred_budget_range": prefs.preferred_budget_range,
            "last_updated": prefs.last_updated
        },
        "preference_items": [
            {
                "category": item.category,
                "value": item.value,
                "confidence": item.confidence,
                "source_message": item.source_message if hasattr(item, 'source_message') else None,
                "timestamp": item.timestamp
            }
            for item in prefs.preference_items
        ],
        "summary": get_preference_summary(prefs)
    }


class PreferenceUpdate(BaseModel):
    """Model for preference update requests."""
    category: str
    value: str


@app.post("/chat/{session_id}/preferences")
async def update_user_preferences(session_id: str, pref: PreferenceUpdate):
    """
    Manually update a user preference.
    
    Args:
        session_id: Session ID
        pref: Preference to update
    
    Returns:
        Updated preferences
    """
    session = get_or_create_session(session_id)
    
    from .models import PreferenceItem
    from .services.preferences import merge_preferences
    
    # Create preference item
    item = PreferenceItem(
        category=pref.category,
        value=pref.value,
        confidence=1.0,  # Manual updates have high confidence
        source_message="Manual update",
        timestamp=time.time()
    )
    
    # Merge into preferences
    session.shared_state.user_preferences = merge_preferences(
        session.shared_state.user_preferences,
        [item]
    )
    
    # Broadcast preference update to WebSocket clients
    await manager.send_json(session_id, {
        "type": "preference_update",
        "preference": {
            "category": pref.category,
            "value": pref.value
        },
        "session_id": session_id
    })
    
    return {"status": "updated", "preference": pref.model_dump()}


@app.delete("/chat/{session_id}/preferences")
async def clear_user_preferences(session_id: str):
    """
    Clear all learned preferences for a session.
    
    Returns:
        Status confirmation
    """
    session = get_or_create_session(session_id)
    
    from .models import UserPreferences
    
    # Reset preferences
    session.shared_state.user_preferences = UserPreferences()
    
    # Broadcast to WebSocket clients
    await manager.send_json(session_id, {
        "type": "preferences_cleared",
        "session_id": session_id
    })
    
    return {"status": "cleared", "session_id": session_id}


# ============================================================================
# Booking Endpoints
# ============================================================================

class BookingRequest(BaseModel):
    """Request to complete a booking."""
    flight_id: Optional[str] = None
    hotel_id: Optional[str] = None
    passenger_info: Dict[str, str]  # {first_name, last_name, email, phone}
    seat: Optional[str] = None
    payment_info: Dict[str, str]  # Mock payment details
    # Hotel-specific fields
    room_type: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    guests: Optional[str] = None


@app.post("/chat/{session_id}/book")
async def complete_booking(session_id: str, booking: BookingRequest):
    """
    Complete a booking and generate itinerary.
    
    Args:
        session_id: Session ID
        booking: Booking details
    
    Returns:
        Booking confirmation with itinerary HTML
    """
    session = get_or_create_session(session_id)
    
    # Generate booking reference
    booking_ref = f"TRV{uuid.uuid4().hex[:8].upper()}"
    
    # Find the selected flight or hotel
    flight_data = None
    hotel_data = None
    
    if booking.flight_id:
        # Find flight in results
        for flight in session.shared_state.flight_results:
            if flight.id == booking.flight_id:
                flight_data = flight.model_dump()
                break
    
    if booking.hotel_id:
        # Find hotel in results
        for hotel in session.shared_state.hotel_results:
            if hotel.id == booking.hotel_id:
                hotel_data = hotel.model_dump()
                break
    
    # Generate itinerary HTML
    from .services.booking_service import generate_itinerary_html, send_mock_email
    
    # Only pass the relevant booking data (flight OR hotel, not both)
    booking_details = {
        "booking_reference": booking_ref,
        "passenger": booking.passenger_info,
        "payment": booking.payment_info,
    }
    
    # Add flight-specific details if booking a flight
    if booking.flight_id and flight_data:
        booking_details["flight"] = flight_data
        booking_details["seat"] = booking.seat or "Any"
    
    # Add hotel-specific details if booking a hotel
    if booking.hotel_id and hotel_data:
        booking_details["hotel"] = hotel_data
        booking_details["room_type"] = booking.room_type
        booking_details["check_in"] = booking.check_in
        booking_details["check_out"] = booking.check_out
        booking_details["guests"] = booking.guests
    
    itinerary_html = generate_itinerary_html(booking_details)
    
    # Send mock email
    passenger_email = "user@example.com"
    if booking.passenger_info:
        passenger_email = booking.passenger_info.get("email", "user@example.com")
    
    send_mock_email(
        to_email=passenger_email,
        subject=f"Booking Confirmation - {booking_ref}",
        body=itinerary_html
    )
    
    # Update session state
    session.shared_state.confirmed_booking_reference = booking_ref
    session.shared_state.booking_passenger_info = booking.passenger_info
    session.shared_state.booking_seat = booking.seat
    
    # Broadcast to WebSocket
    await manager.send_json(session_id, {
        "type": "booking_confirmed",
        "booking_reference": booking_ref,
        "session_id": session_id
    })
    
    return {
        "status": "confirmed",
        "booking_reference": booking_ref,
        "itinerary_html": itinerary_html
    }
