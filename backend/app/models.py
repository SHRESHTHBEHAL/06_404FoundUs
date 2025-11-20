"""
Pydantic models and state definitions for the Travel Assistant.

This module contains:
- Conversation models (ConversationTurn)
- Search parameter models (FlightSearchParams, HotelSearchParams)
- Result models (FlightResult, HotelResult)
- LangGraph SharedState model
- Active run tracking models
"""

import asyncio
import time
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================

class Intent(str, Enum):
    """User intent classification."""
    FLIGHT = "flight"
    HOTEL = "hotel"
    COMBINED = "combined"
    REFINE = "refine"
    OTHER = "other"


class AgentType(str, Enum):
    """Agent types in the system."""
    COORDINATOR = "coordinator"
    FLIGHT = "flight"
    HOTEL = "hotel"


# ============================================================================
# Conversation Models
# ============================================================================

class ConversationTurn(BaseModel):
    """Represents a single turn in the conversation."""
    sender: str  # "user" | "assistant" | "system"
    text: str
    timestamp: float
    run_id: Optional[str] = None


class ConversationSummary(BaseModel):
    """Summarized segment of conversation history."""
    summary_text: str
    turn_count: int  # Number of turns summarized
    start_timestamp: float
    end_timestamp: float
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())


class PreferenceItem(BaseModel):
    """Individual user preference with metadata and timestamps."""
    category: str  # "flight_time", "cabin_class", "hotel_rating", "budget", etc.
    value: str  # "morning", "business", "4-star", etc.
    confidence: float = 1.0  # 0.0 to 1.0
    source_message: Optional[str] = None  # Original message that revealed this preference
    timestamp: float = Field(default_factory=lambda: time.time())
    applied_count: int = 0  # How many times this preference was used


class UserPreferences(BaseModel):
    """Collection of learned user preferences."""
    # Flight preferences
    preferred_flight_time: Optional[str] = None  # "morning", "afternoon", "evening"
    preferred_cabin_class: Optional[str] = None  # "economy", "business", "first"
    preferred_airlines: List[str] = []  # List of preferred airlines
    max_stops: Optional[int] = None  # Maximum acceptable stops
    
    # Hotel preferences
    min_hotel_rating: Optional[float] = None  # Minimum star rating
    preferred_hotel_budget: Optional[str] = None  # "budget", "mid", "luxury"
    preferred_amenities: List[str] = []  # Wifi, Pool, Gym, etc.
    
    # General preferences
    preferred_budget_range: Optional[str] = None  # "under_500", "500_1000", "luxury"
    
    # Metadata
    preference_items: List[PreferenceItem] = []  # Detailed tracking
    last_updated: Optional[float] = None


# ============================================================================
# Search Parameter Models
# ============================================================================

class FlightSearchParams(BaseModel):
    """Parameters for flight search."""
    origin: Optional[str] = None
    destination: Optional[str] = None
    depart_date: Optional[str] = None  # ISO format: YYYY-MM-DD
    return_date: Optional[str] = None  # ISO format: YYYY-MM-DD
    passengers: Optional[int] = 1
    cabin_class: Optional[str] = "economy"  # economy, business, first
    max_stops: Optional[int] = None  # Filter by max number of stops (0=direct, 1, 2, etc.)
    
    class Config:
        json_schema_extra = {
            "example": {
                "origin": "NYC",
                "destination": "LAX",
                "depart_date": "2025-12-01",
                "return_date": "2025-12-08",
                "passengers": 2,
                "cabin_class": "economy",
                "max_stops": 1
            }
        }


class HotelSearchParams(BaseModel):
    """Parameters for hotel search."""
    city: Optional[str] = None
    check_in: Optional[str] = None  # ISO format: YYYY-MM-DD
    check_out: Optional[str] = None  # ISO format: YYYY-MM-DD
    guests: Optional[int] = 1
    budget: Optional[Union[str, float]] = None  # "budget", "mid", "luxury" or numeric value
    min_rating: Optional[float] = None  # e.g., 3.5 stars
    
    class Config:
        json_schema_extra = {
            "example": {
                "city": "Los Angeles",
                "check_in": "2025-12-01",
                "check_out": "2025-12-08",
                "guests": 2,
                "budget": "mid",
                "min_rating": 4.0
            }
        }


# ============================================================================
# Result Models
# ============================================================================

class FlightSegment(BaseModel):
    """Represents a single leg/segment of a multi-leg flight."""
    airline: str
    flight_number: Optional[str] = None
    origin: str
    destination: str
    departure_time: str  # ISO format datetime
    arrival_time: str  # ISO format datetime
    duration_minutes: int
    origin_coordinates: Optional[List[float]] = None  # [lat, lon]
    destination_coordinates: Optional[List[float]] = None  # [lat, lon]
    aircraft: Optional[str] = None  # e.g., "Boeing 737"


class FlightResult(BaseModel):
    """Represents a single flight option (can be multi-leg)."""
    id: str = Field(default_factory=lambda: f"flight_{datetime.now().timestamp()}")
    airline: str
    flight_number: Optional[str] = None
    origin: str
    destination: str
    departure_time: str  # ISO format datetime
    arrival_time: str  # ISO format datetime
    duration_minutes: int
    stops: int = 0
    price: float
    currency: str = "USD"
    cabin_class: str = "economy"
    booking_link: Optional[str] = None
    is_partial: bool = False  # Indicates if from interrupted run
    origin_coordinates: Optional[List[float]] = None  # [lat, lon]
    destination_coordinates: Optional[List[float]] = None  # [lat, lon]
    
    # Multi-leg support
    segments: List[FlightSegment] = []  # Empty for direct flights, populated for multi-leg
    layovers: List[Dict[str, Any]] = []  # Connection info: {city, duration_minutes}
    total_journey_duration: Optional[int] = None  # Total time including layovers
    
    class Config:
        json_schema_extra = {
            "example": {
                "airline": "United Airlines",
                "flight_number": "UA1234",
                "origin": "JFK",
                "destination": "LAX",
                "departure_time": "2025-12-01T08:00:00",
                "arrival_time": "2025-12-01T11:30:00",
                "duration_minutes": 330,
                "stops": 0,
                "price": 299.99,
                "currency": "USD",
                "cabin_class": "economy",
                "origin_coordinates": [40.6413, -73.7781],
                "destination_coordinates": [33.9416, -118.4085],
                "segments": [],
                "layovers": [],
                "total_journey_duration": 330
            }
        }


class HotelResult(BaseModel):
    """Represents a single hotel option."""
    id: str = Field(default_factory=lambda: f"hotel_{datetime.now().timestamp()}")
    name: str
    city: str
    address: Optional[str] = None
    star_rating: Optional[float] = None
    review_score: Optional[float] = None
    review_count: Optional[int] = None  # Number of reviews
    price_per_night: float
    currency: str = "USD"
    total_price: Optional[float] = None
    amenities: List[str] = []
    image_url: Optional[str] = None
    images: List[str] = []  # List of image URLs
    booking_link: Optional[str] = None
    is_partial: bool = False  # Indicates if from interrupted run
    coordinates: Optional[List[float]] = None  # [lat, lon]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Hilton Los Angeles",
                "city": "Los Angeles",
                "address": "123 Main St, Los Angeles, CA",
                "star_rating": 4.0,
                "review_score": 8.5,
                "price_per_night": 189.00,
                "currency": "USD",
                "total_price": 1323.00,
                "amenities": ["WiFi", "Pool", "Gym"]
            }
        }


# ============================================================================
# LangGraph Shared State
# ============================================================================

class SharedState(BaseModel):
    """
    Shared state passed between LangGraph nodes.
    
    This state object maintains:
    - Conversation history
    - Current user intent
    - Search parameters for flights and hotels
    - Search results (including partial results from interruptions)
    - Agent execution metadata
    - User preferences (learned over time)
    - Conversation summaries (for long sessions)
    """
    # Conversation context
    session_id: Optional[str] = None
    conversation_history: List[ConversationTurn] = []
    conversation_summaries: List[ConversationSummary] = []  # Summarized older conversations
    
    # User preferences (learned)
    user_preferences: UserPreferences = UserPreferences()
    
    # Intent and routing
    current_intent: Intent = Intent.OTHER
    
    # Search parameters
    flight_params: Optional[FlightSearchParams] = None
    hotel_params: Optional[HotelSearchParams] = None
    
    # Results
    flight_results: List[FlightResult] = []
    hotel_results: List[HotelResult] = []
    
    # Agent metadata
    last_agent: Optional[AgentType] = None
    interrupted_run_ids: List[str] = []
    
    # Interruption control
    is_interrupted: bool = False
    current_run_id: Optional[str] = None
    
    # Selected items (for booking simulation or context transfer)
    selected_flight_id: Optional[str] = None
    selected_hotel_id: Optional[str] = None
    
    # Pending booking state (waiting for user confirmation)
    pending_flight_booking: Optional[str] = None
    pending_hotel_booking: Optional[str] = None
    
    # Booking details (for checkout flow)
    booking_passenger_info: Optional[Dict[str, Any]] = None  # {first_name, last_name, email, phone}
    booking_seat: Optional[str] = None  # e.g., "12A"
    booking_payment_info: Optional[Dict[str, Any]] = None  # Mock payment details
    confirmed_booking_reference: Optional[str] = None  # Generated after "payment"
    
    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# Active Run Registry Models
# ============================================================================

class ActiveRun(BaseModel):
    """
    Tracks an active agent run for interruption handling.
    
    Note: asyncio.Task cannot be serialized by Pydantic, so we store
    it separately in a plain dict. This model is for metadata only.
    """
    run_id: str
    agent_type: AgentType
    started_at: float  # UNIX timestamp
    session_id: str
    
    class Config:
        arbitrary_types_allowed = True


# Note: The actual task handle (asyncio.Task) is stored in a separate
# in-memory dict in main.py:
# active_tasks: Dict[str, asyncio.Task] = {}
# active_runs: Dict[str, ActiveRun] = {}
