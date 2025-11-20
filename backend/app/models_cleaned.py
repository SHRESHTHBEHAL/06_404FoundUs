"""Pydantic models and state definitions for Travel Assistant."""

import time
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class Intent(str, Enum):
    FLIGHT = "flight"
    HOTEL = "hotel"
    COMBINED = "combined"
    REFINE = "refine"
    OTHER = "other"


class AgentType(str, Enum):
    COORDINATOR = "coordinator"
    FLIGHT = "flight"
    HOTEL = "hotel"


class ConversationTurn(BaseModel):
    sender: str
    text: str
    timestamp: float
    run_id: Optional[str] = None


class ConversationSummary(BaseModel):
    summary_text: str
    turn_count: int
    start_timestamp: float
    end_timestamp: float
    created_at: float = Field(default_factory=lambda: datetime.now().timestamp())


class PreferenceItem(BaseModel):
    category: str
    value: str
    confidence: float = 1.0
    source_message: Optional[str] = None
    timestamp: float = Field(default_factory=lambda: time.time())
    applied_count: int = 0


class UserPreferences(BaseModel):
    preferred_flight_time: Optional[str] = None
    preferred_cabin_class: Optional[str] = None
    preferred_airlines: List[str] = []
    max_stops: Optional[int] = None
    min_hotel_rating: Optional[float] = None
    preferred_hotel_budget: Optional[str] = None
    preferred_amenities: List[str] = []
    preferred_budget_range: Optional[str] = None
    preference_items: List[PreferenceItem] = []
    last_updated: Optional[float] = None


class FlightSearchParams(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    depart_date: Optional[str] = None
    return_date: Optional[str] = None
    passengers: Optional[int] = 1
    cabin_class: Optional[str] = "economy"


class HotelSearchParams(BaseModel):
    city: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    guests: Optional[int] = 1
    budget: Optional[Union[str, float]] = None
    min_rating: Optional[float] = None


class FlightSegment(BaseModel):
    """Single leg of a multi-segment flight."""
    airline: str
    flight_number: Optional[str] = None
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    origin_coordinates: Optional[List[float]] = None
    destination_coordinates: Optional[List[float]] = None
    aircraft: Optional[str] = None


class FlightResult(BaseModel):
    id: str = Field(default_factory=lambda: f"flight_{datetime.now().timestamp()}")
    airline: str
    flight_number: Optional[str] = None
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    stops: int = 0
    price: float
    currency: str = "USD"
    cabin_class: str = "economy"
    booking_link: Optional[str] = None
    is_partial: bool = False
    origin_coordinates: Optional[List[float]] = None
    destination_coordinates: Optional[List[float]] = None
    segments: List[FlightSegment] = []
    layovers: List[Dict[str, Any]] = []
    total_journey_duration: Optional[int] = None


class HotelResult(BaseModel):
    id: str = Field(default_factory=lambda: f"hotel_{datetime.now().timestamp()}")
    name: str
    city: str
    address: Optional[str] = None
    star_rating: Optional[float] = None
    review_score: Optional[float] = None
    review_count: Optional[int] = None
    price_per_night: float
    currency: str = "USD"
    total_price: Optional[float] = None
    amenities: List[str] = []
    image_url: Optional[str] = None
    images: List[str] = []
    booking_link: Optional[str] = None
    is_partial: bool = False
    coordinates: Optional[List[float]] = None


class SharedState(BaseModel):
    """LangGraph state shared across all agent nodes."""
    session_id: Optional[str] = None
    conversation_history: List[ConversationTurn] = []
    conversation_summaries: List[ConversationSummary] = []
    user_preferences: UserPreferences = UserPreferences()
    current_intent: Intent = Intent.OTHER
    flight_params: Optional[FlightSearchParams] = None
    hotel_params: Optional[HotelSearchParams] = None
    flight_results: List[FlightResult] = []
    hotel_results: List[HotelResult] = []
    last_agent: Optional[AgentType] = None
    interrupted_run_ids: List[str] = []
    is_interrupted: bool = False
    current_run_id: Optional[str] = None
    selected_flight_id: Optional[str] = None
    selected_hotel_id: Optional[str] = None
    pending_flight_booking: Optional[str] = None
    pending_hotel_booking: Optional[str] = None
    booking_passenger_info: Optional[Dict[str, Any]] = None
    booking_seat: Optional[str] = None
    booking_payment_info: Optional[Dict[str, Any]] = None
    confirmed_booking_reference: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


class ActiveRun(BaseModel):
    """Tracks active agent run for interruption handling."""
    run_id: str
    session_id: str
    start_time: float
    agent_type: Optional[AgentType] = None
    
    class Config:
        arbitrary_types_allowed = True
