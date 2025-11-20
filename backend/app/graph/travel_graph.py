"""
LangGraph-based multi-agent orchestration for Travel Assistant.

This module defines the agent graph with:
- Coordinator node (intent routing)
- Flight Agent node (flight search)
- Hotel Agent node (hotel search)
- Response node (natural language generation)
"""

import asyncio
from typing import Literal
from langgraph.graph import StateGraph, END
from ..models import SharedState, Intent, AgentType, FlightSearchParams, HotelSearchParams
from ..tools import lookup_flights, lookup_hotels
from ..config import USE_MOCK
from ..llm import classify_intent, generate_response_summary
from ..services.event_manager import event_manager


# ============================================================================
# Agent Node Implementations (Async)
# ============================================================================

async def coordinator_node(state: SharedState) -> SharedState:
    """
    Coordinator Agent: Routes user intent and manages context.
    
    Responsibilities:
    - Classify user intent (flight, hotel, combined, refine)
    - Extract and normalize search parameters
    - Set routing flags for which agents to invoke
    - Extract user preferences from messages
    - Apply learned preferences to search parameters
    
    Uses Gemini LLM for intent classification and parameter extraction.
    """
    print(f"[Coordinator] Processing intent...")
    if state.session_id:
        await event_manager.emit(state.session_id, "agent_status", {
            "agent": "Coordinator",
            "status": "Understanding your request...",
            "step": "intent_classification"
        })
    
    # Check for interruption
    if state.is_interrupted:
        print(f"[Coordinator] Run interrupted, skipping")
        return state
    
    # Get latest user message
    last_message = ""
    if state.conversation_history:
        user_messages = [t for t in state.conversation_history if t.sender == "user"]
        if user_messages:
            last_message = user_messages[-1].text
    
    # Extract preferences from user message
    from ..services.preferences import extract_preferences, apply_preferences_to_flight_params, apply_preferences_to_hotel_params
    if last_message:
        state.user_preferences = extract_preferences(last_message, state.user_preferences)
        if state.user_preferences.preference_items:
            latest_pref = state.user_preferences.preference_items[-1]
            print(f"[Coordinator] Learned preference: {latest_pref.category}={latest_pref.value}")
            if state.session_id:
                await event_manager.emit(state.session_id, "agent_status", {
                    "agent": "Coordinator",
                    "status": f"Learned preference: {latest_pref.value}",
                    "step": "preference_learning"
                })
    
    # Convert conversation history to dict format for LLM
    history_dict = [
        {"sender": turn.sender, "text": turn.text}
        for turn in state.conversation_history[-5:]  # Last 5 turns
    ]
    
    # Use Gemini to classify intent and extract parameters
    intent_result = classify_intent(last_message, history_dict)
    
    # Update intent
    intent_str = intent_result.get("intent", "other")
    try:
        state.current_intent = Intent(intent_str)
    except:
        state.current_intent = Intent.OTHER
    
    # Extract flight parameters if present
    if "flight_params" in intent_result and intent_result["flight_params"]:
        fp = intent_result["flight_params"]
        state.flight_params = FlightSearchParams(
            origin=fp.get("origin"),
            destination=fp.get("destination"),
            depart_date=fp.get("depart_date"),
            return_date=fp.get("return_date"),
            passengers=fp.get("passengers", 1),
            cabin_class=fp.get("cabin_class", "economy"),
            max_stops=fp.get("max_stops")
        )
        print(f"[Coordinator] Extracted flight params: origin={state.flight_params.origin}, dest={state.flight_params.destination}, max_stops={state.flight_params.max_stops}")
    
    # Extract hotel parameters if present
    if "hotel_params" in intent_result and intent_result["hotel_params"]:
        hp = intent_result["hotel_params"]
        state.hotel_params = HotelSearchParams(
            city=hp.get("city"),
            check_in=hp.get("check_in"),
            check_out=hp.get("check_out"),
            guests=hp.get("guests", 1),
            budget=hp.get("budget"),
            min_rating=hp.get("min_rating")
        )
    
    # Apply learned preferences to parameters
    if state.flight_params:
        state.flight_params = apply_preferences_to_flight_params(state.flight_params, state.user_preferences)
    if state.hotel_params:
        state.hotel_params = apply_preferences_to_hotel_params(state.hotel_params, state.user_preferences)
    
    # Handle selected items (for booking/selection)
    if "selected_item" in intent_result and intent_result["selected_item"]:
        selected = intent_result["selected_item"]
        action = selected.get("action", "select")  # Default to select
        identifier = selected.get("identifier", "")
        
        if selected.get("type") == "flight":
            if action == "select":
                # Check if user is re-selecting the same pending flight (treat as confirmation)
                # Check both directions for substring matching to be more robust
                is_same_flight = False
                if state.pending_flight_booking and identifier:
                    pending_lower = state.pending_flight_booking.lower()
                    identifier_lower = identifier.lower()
                    # Check if either is a substring of the other
                    is_same_flight = (identifier_lower in pending_lower) or (pending_lower in identifier_lower)
                    print(f"[Coordinator] Checking flight match: pending='{state.pending_flight_booking}', new='{identifier}', match={is_same_flight}")
                
                if is_same_flight:
                    # User clicked the same option again - treat as confirmation
                    state.selected_flight_id = state.pending_flight_booking
                    print(f"[Coordinator] User re-selected pending flight (treating as confirmation): {state.pending_flight_booking}")
                    state.pending_flight_booking = None  # Clear pending
                else:
                    # User is making a new selection - mark as pending booking
                    state.selected_flight_id = identifier
                    state.pending_flight_booking = identifier
                    print(f"[Coordinator] User selecting flight: {identifier} (pending confirmation)")
            elif action == "book" or identifier == "confirmed":
                # User is confirming - complete the booking
                if state.pending_flight_booking:
                    state.selected_flight_id = state.pending_flight_booking
                    print(f"[Coordinator] User confirmed flight booking: {state.pending_flight_booking}")
                    state.pending_flight_booking = None  # Clear pending
                else:
                    print(f"[Coordinator] User confirming booking (no pending flight)")
        elif selected.get("type") == "hotel":
            if action == "select":
                # Check if user is re-selecting the same pending hotel (treat as confirmation)
                # Check both directions for substring matching to be more robust
                is_same_hotel = False
                if state.pending_hotel_booking and identifier:
                    pending_lower = state.pending_hotel_booking.lower()
                    identifier_lower = identifier.lower()
                    # Check if either is a substring of the other
                    is_same_hotel = (identifier_lower in pending_lower) or (pending_lower in identifier_lower)
                    print(f"[Coordinator] Checking hotel match: pending='{state.pending_hotel_booking}', new='{identifier}', match={is_same_hotel}")
                
                if is_same_hotel:
                    # User clicked the same option again - treat as confirmation
                    state.selected_hotel_id = state.pending_hotel_booking
                    print(f"[Coordinator] User re-selected pending hotel (treating as confirmation): {state.pending_hotel_booking}")
                    state.pending_hotel_booking = None  # Clear pending
                else:
                    # User is making a new selection - mark as pending booking
                    state.selected_hotel_id = identifier
                    state.pending_hotel_booking = identifier
                    print(f"[Coordinator] User selecting hotel: {identifier} (pending confirmation)")
            elif action == "book" or identifier == "confirmed":
                if state.pending_hotel_booking:
                    state.selected_hotel_id = state.pending_hotel_booking
                    print(f"[Coordinator] User confirmed hotel booking: {state.pending_hotel_booking}")
                    state.pending_hotel_booking = None
                else:
                    print(f"[Coordinator] User confirming booking (no pending hotel)")
    
    state.last_agent = AgentType.COORDINATOR
    
    print(f"[Coordinator] Detected intent: {state.current_intent}")
    if state.session_id:
        await event_manager.emit(state.session_id, "agent_status", {
            "agent": "Coordinator",
            "status": f"Intent: {state.current_intent.value}",
            "step": "routing"
        })

    if state.flight_params:
        print(f"[Coordinator] Flight params: {state.flight_params.origin} → {state.flight_params.destination}")
    if state.hotel_params:
        print(f"[Coordinator] Hotel params: {state.hotel_params.city}")
    
    return state


async def flight_agent_node(state: SharedState) -> SharedState:
    """
    Flight Agent: Searches for flights based on parameters.
    
    Responsibilities:
    - Read flight_params from state
    - Call mock flight search (or real API)
    - Append results to state.flight_results
    - Support partial results streaming
    """
    print(f"[Flight Agent] Searching flights...")
    if state.session_id:
        await event_manager.emit(state.session_id, "agent_status", {
            "agent": "Flight Agent",
            "status": f"Searching flights to {state.flight_params.destination if state.flight_params else 'destination'}...",
            "step": "search_start"
        })
    
    # Check for interruption
    if state.is_interrupted:
        print(f"[Flight Agent] Run interrupted, skipping search")
        return state
    
    # Use flight_params from state or create defaults
    if state.flight_params is None:
        # Try to extract from last message or use defaults
        state.flight_params = FlightSearchParams(
            origin="JFK",
            destination="LAX",
            passengers=1
        )
    
    # Only search for NEW flights if we don't have results already
    # or if the search parameters have changed significantly
    should_search = (
        len(state.flight_results) == 0 or 
        (state.flight_params and len(state.flight_results) > 0 and 
         state.flight_results[0].destination != state.flight_params.destination)
    )
    
    if should_search:
        # Use async streaming search with partial results support
        from ..tools import lookup_flights
        import asyncio # Import asyncio for sleep
        
        # Prepare flight parameters for the search
        flight_params = state.flight_params
        
        # Execute search
        if state.session_id:
            await event_manager.emit(state.session_id, "agent_status", {
                "agent": "Flight Agent",
                "status": f"Searching flights from {flight_params.origin} to {flight_params.destination}...",
                "step": "search_executing"
            })

        search_result = await asyncio.to_thread(
            lookup_flights,
            origin=flight_params.origin or "JFK",
            destination=flight_params.destination or "LAX",
            depart_date=flight_params.depart_date,
            return_date=flight_params.return_date,
            passengers=flight_params.passengers or 1,
            cabin_class=flight_params.cabin_class or "economy"
        )
        
        if state.session_id:
            count = len(search_result.get("results", []))
            await event_manager.emit(state.session_id, "agent_status", {
                "agent": "Flight Agent",
                "status": f"Found {count} flights. Filtering and sorting...",
                "step": "search_processing"
            })
            # Simulate a brief pause for "filtering" visual effect
            await asyncio.sleep(0.5)
        
        # Convert dict results to FlightResult objects
        from ..models import FlightResult
        state.flight_results = [
            FlightResult(**flight) if isinstance(flight, dict) else flight
            for flight in search_result["results"]
        ]
        
        print(f"[Flight Agent] Found {len(state.flight_results)} flights (source: {search_result['source']})")
        if state.session_id:
            await event_manager.emit(state.session_id, "agent_status", {
                "agent": "Flight Agent",
                "status": f"Found {len(state.flight_results)} flights",
                "step": "search_complete"
            })
    else:
        print(f"[Flight Agent] Reusing existing {len(state.flight_results)} flights")
    
    state.last_agent = AgentType.FLIGHT
    
    return state


async def hotel_agent_node(state: SharedState) -> SharedState:
    """
    Hotel Agent: Searches for hotels based on parameters.
    
    Responsibilities:
    - Read hotel_params from state (or derive from flight_params)
    - Call mock hotel search (or real API)
    - Append results to state.hotel_results
    - Support partial results streaming
    """
    print(f"[Hotel Agent] Searching hotels...")
    if state.session_id:
        await event_manager.emit(state.session_id, "agent_status", {
            "agent": "Hotel Agent",
            "status": f"Searching hotels in {state.hotel_params.city if state.hotel_params else 'city'}...",
            "step": "search_start"
        })
    
    # Check for interruption
    if state.is_interrupted:
        print(f"[Hotel Agent] Run interrupted, skipping search")
        return state
    
    # Derive hotel params from flight destination if not set
    if state.hotel_params is None:
        if state.flight_params and state.flight_params.destination:
            state.hotel_params = HotelSearchParams(
                city=state.flight_params.destination,
                check_in=state.flight_params.depart_date,
                check_out=state.flight_params.return_date,
                guests=state.flight_params.passengers
            )
        else:
            # Use defaults
            state.hotel_params = HotelSearchParams(
                city="Los Angeles",
                guests=1
            )
    
    # Only search for NEW hotels if we don't have results already
    # or if the search parameters have changed
    should_search = (
        len(state.hotel_results) == 0 or 
        (state.hotel_params and len(state.hotel_results) > 0 and 
         state.hotel_results[0].city != state.hotel_params.city)
    )
    
    if should_search:
        # Use async streaming search with partial results support
        from ..travel.mock_hotels import search_hotels_streaming
        
        # Run search (supports cancellation via asyncio)
        search_result = await asyncio.to_thread(
            lookup_hotels,
            city=state.hotel_params.city or "Los Angeles",
            check_in=state.hotel_params.check_in,
            check_out=state.hotel_params.check_out,
            guests=state.hotel_params.guests or 1,
            budget=state.hotel_params.budget,
            min_rating=state.hotel_params.min_rating
        )
        
        # Convert dict results to HotelResult objects
        from ..models import HotelResult
        state.hotel_results = [
            HotelResult(**hotel) if isinstance(hotel, dict) else hotel
            for hotel in search_result["results"]
        ]
        
        print(f"[Hotel Agent] Found {len(state.hotel_results)} hotels (source: {search_result['source']})")
        if state.session_id:
            await event_manager.emit(state.session_id, "agent_status", {
                "agent": "Hotel Agent",
                "status": f"Found {len(state.hotel_results)} hotels",
                "step": "search_complete"
            })
    else:
        print(f"[Hotel Agent] Reusing existing {len(state.hotel_results)} hotels")
    
    state.last_agent = AgentType.HOTEL
    
    return state


async def response_node(state: SharedState) -> SharedState:
    """
    Response Node: Generates natural language summary of results.
    
    Responsibilities:
    - Combine flight and hotel results into readable format
    - Use LLM to generate conversational response
    - Update conversation history
    
    Uses Gemini for natural language generation.
    """
    print(f"[Response] Generating response...")
    if state.session_id:
        await event_manager.emit(state.session_id, "agent_status", {
            "agent": "Responder",
            "status": "Generating response...",
            "step": "generation_start"
        })
    
    # Check for interruption
    if state.is_interrupted:
        print(f"[Response] Run interrupted, skipping response generation")
        return state
    
    # Get latest user message for context
    user_message = ""
    if state.conversation_history:
        user_messages = [t for t in state.conversation_history if t.sender == "user"]
        if user_messages:
            user_message = user_messages[-1].text
    
    # Convert results to dict format
    flight_results_dict = [f.dict() for f in state.flight_results] if state.flight_results else None
    hotel_results_dict = [h.dict() for h in state.hotel_results] if state.hotel_results else None
    
    # Build context for response including selections and validation
    context_info = {
        "selected_flight": state.selected_flight_id,
        "selected_hotel": state.selected_hotel_id,
        "pending_flight": state.pending_flight_booking,
        "pending_hotel": state.pending_hotel_booking,
        "action": "select"  # Default action
    }
    
    # Determine action based on pending state
    if state.pending_flight_booking:
        # We have a pending flight booking, waiting for confirmation
        context_info["action"] = "select"
        context_info["selected_flight"] = state.pending_flight_booking
    elif state.selected_flight_id and not state.pending_flight_booking:
        # Booking was just confirmed (pending was cleared)
        context_info["action"] = "book"
        context_info["selected_flight"] = state.selected_flight_id
    
    if state.pending_hotel_booking:
        context_info["action"] = "select"
        context_info["selected_hotel"] = state.pending_hotel_booking
    elif state.selected_hotel_id and not state.pending_hotel_booking:
        context_info["action"] = "book"
        context_info["selected_hotel"] = state.selected_hotel_id
    
    # If user selected a flight, verify it exists in current results
    if state.selected_flight_id and state.flight_results:
        selected_identifier = state.selected_flight_id.lower()
        # Check if the selection matches any available flight
        matching_flights = [
            f for f in state.flight_results 
            if (selected_identifier in f.airline.lower() or 
                selected_identifier in f.flight_number.lower() if f.flight_number else False or
                str(f.price) in selected_identifier)
        ]
        context_info["matching_flights"] = [f.dict() for f in matching_flights] if matching_flights else None
    
    # If user selected a hotel, verify it exists in current results
    if state.selected_hotel_id and state.hotel_results:
        selected_identifier = state.selected_hotel_id.lower()
        # Check if the selection matches any available hotel
        matching_hotels = [
            h for h in state.hotel_results 
            if (selected_identifier in h.name.lower() or 
                str(h.price_per_night) in selected_identifier)
        ]
        context_info["matching_hotels"] = [h.dict() for h in matching_hotels] if matching_hotels else None
    
    # Generate response using Gemini (Streaming)
    from ..llm import generate_response_stream
    
    response_text = ""
    
    # Stream tokens if session_id is available
    if state.session_id:
        try:
            for token in generate_response_stream(
                intent=state.current_intent.value,
                flight_results=flight_results_dict,
                hotel_results=hotel_results_dict,
                user_message=user_message,
                context=context_info
            ):
                response_text += token
                # Emit token event
                # We use a fire-and-forget approach or await if we can
                # Since this is an async node, we can await
                await event_manager.emit(state.session_id, "token", {
                    "text": token,
                    "full_text": response_text  # Optional: send full text so far for easier UI handling
                })
        except Exception as e:
            print(f"[Response] Error streaming: {e}")
            # Fallback to non-streaming if streaming fails
            response_text = generate_response_summary(
                intent=state.current_intent.value,
                flight_results=flight_results_dict,
                hotel_results=hotel_results_dict,
                user_message=user_message,
                context=context_info
            )
    else:
        # Non-streaming fallback
        response_text = generate_response_summary(
            intent=state.current_intent.value,
            flight_results=flight_results_dict,
            hotel_results=hotel_results_dict,
            user_message=user_message,
            context=context_info
        )
    
    # Add to conversation history
    from ..models import ConversationTurn
    import time
    
    assistant_turn = ConversationTurn(
        sender="assistant",
        text=response_text,
        timestamp=time.time()
    )
    state.conversation_history.append(assistant_turn)
    
    print(f"[Response] Generated: {response_text}")
    
    if state.session_id:
        await event_manager.emit(state.session_id, "agent_status", {
            "agent": "Responder",
            "status": "Response complete",
            "step": "generation_complete"
        })
    
    return state


# ============================================================================
# Routing Logic
# ============================================================================

def route_after_coordinator(state: SharedState) -> Literal["flight_agent", "hotel_agent", "response"]:
    """
    Determine which agent(s) to invoke after coordinator.
    
    Returns the next node name based on intent.
    """
    if state.current_intent == Intent.FLIGHT:
        return "flight_agent"
    elif state.current_intent == Intent.HOTEL:
        return "hotel_agent"
    elif state.current_intent == Intent.COMBINED:
        # For combined, we'll go to flight first, then hotel
        return "flight_agent"
    else:
        # For OTHER or unknown, skip to response
        return "response"


def route_after_flight(state: SharedState) -> Literal["hotel_agent", "response"]:
    """
    Determine next step after flight agent.
    
    If intent is COMBINED, continue to hotel search.
    Otherwise, go to response.
    """
    if state.current_intent == Intent.COMBINED:
        return "hotel_agent"
    else:
        return "response"


# ============================================================================
# Graph Construction
# ============================================================================

def create_travel_graph() -> StateGraph:
    """
    Create and compile the LangGraph travel assistant graph.
    
    Graph flow:
    START -> coordinator -> [flight_agent | hotel_agent | response]
    flight_agent -> [hotel_agent | response]
    hotel_agent -> response
    response -> END
    """
    # Initialize graph with SharedState
    graph = StateGraph(SharedState)
    
    # Add nodes
    graph.add_node("coordinator", coordinator_node)
    graph.add_node("flight_agent", flight_agent_node)
    graph.add_node("hotel_agent", hotel_agent_node)
    graph.add_node("response", response_node)
    
    # Set entry point
    graph.set_entry_point("coordinator")
    
    # Add conditional edges from coordinator
    graph.add_conditional_edges(
        "coordinator",
        route_after_coordinator,
        {
            "flight_agent": "flight_agent",
            "hotel_agent": "hotel_agent",
            "response": "response"
        }
    )
    
    # Add conditional edges from flight_agent
    graph.add_conditional_edges(
        "flight_agent",
        route_after_flight,
        {
            "hotel_agent": "hotel_agent",
            "response": "response"
        }
    )
    
    # Hotel agent always goes to response
    graph.add_edge("hotel_agent", "response")
    
    # Response is the final node
    graph.add_edge("response", END)
    
    # Compile the graph
    compiled_graph = graph.compile()
    
    print("[Graph] Travel assistant graph compiled successfully")
    
    return compiled_graph


# ============================================================================
# Graph Instance
# ============================================================================

# Create the compiled graph instance
travel_graph = create_travel_graph()
