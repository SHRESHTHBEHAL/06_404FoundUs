"""
User Preference Learning Service.

Extracts and manages user preferences from conversation,
applying them to future searches.
"""

import time
import json
import re
from typing import Optional
from ..models import (
    UserPreferences, 
    PreferenceItem, 
    FlightSearchParams, 
    HotelSearchParams
)
from ..llm import generate_text


def extract_preferences(message: str, existing_prefs: UserPreferences) -> UserPreferences:
    """
    Extract user preferences from a message using pattern matching and LLM.
    
    Args:
        message: User's message text
        existing_prefs: Current user preferences
    
    Returns:
        Updated preferences
    """
    message_lower = message.lower()
    new_items = []
    
    # Pattern-based extraction (fast path)
    patterns = {
        # Flight time preferences
        r'\b(prefer|like|want|always|usually|taking).*(morning|early morning|dawn|sunrise).*(flight|flights)': ('flight_time', 'morning'),
        r'\b(prefer|like|want|always|usually|taking).*(afternoon|midday|lunch).*(flight|flights)': ('flight_time', 'afternoon'),
        r'\b(prefer|like|want|always|usually|taking).*(evening|night|late|sunset).*(flight|flights)': ('flight_time', 'evening'),
        
        # Cabin class preferences
        r'\b(prefer|like|want|always|usually).*(business class|business)': ('cabin_class', 'business'),
        r'\b(prefer|like|want|always|usually).*(first class|first)': ('cabin_class', 'first'),
        r'\b(prefer|like|want|always|usually).*(economy|coach)': ('cabin_class', 'economy'),
        
        # Flight preferences
        r'\b(prefer|like|want|only).*(direct flight|nonstop|no stop)': ('max_stops', '0'),
        r'\b(don\'t like|hate|avoid|never).*(layover|connection|stop)': ('max_stops', '0'),
        
        # Hotel ratings
        r'\b(prefer|like|want|always).*(4[ -]star|four[ -]star|4\*)': ('min_hotel_rating', '4.0'),
        r'\b(prefer|like|want|always).*(5[ -]star|five[ -]star|5\*|luxury hotel)': ('min_hotel_rating', '5.0'),
        r'\b(prefer|like|want|always).*(3[ -]star|three[ -]star|3\*)': ('min_hotel_rating', '3.0'),
        
        # Budget preferences
        r'\b(prefer|like|want|always).*(budget|cheap|affordable|inexpensive)': ('hotel_budget', 'budget'),
        r'\b(prefer|like|want|always).*(luxury|high[ -]end|expensive|premium)': ('hotel_budget', 'luxury'),
        
        # Amenities
        r'\b(need|want|must have|prefer).*(wifi|wi-fi|internet)': ('amenity', 'WiFi'),
        r'\b(need|want|must have|prefer).*(pool|swimming)': ('amenity', 'Pool'),
        r'\b(need|want|must have|prefer).*(gym|fitness)': ('amenity', 'Gym'),
    }
    
    for pattern, (category, value) in patterns.items():
        if re.search(pattern, message_lower):
            new_items.append(PreferenceItem(
                category=category,
                value=value,
                confidence=0.9,  # High confidence for pattern matches
                source_message=message[:100],  # Keep first 100 chars
                timestamp=time.time()
            ))
    
    # LLM-based extraction for complex preferences
    if any(word in message_lower for word in ['prefer', 'like', 'always', 'usually', 'typically', 'never', 'hate']):
        llm_prefs = _extract_preferences_llm(message)
        new_items.extend(llm_prefs)
    
    # Merge new preferences with existing
    updated_prefs = merge_preferences(existing_prefs, new_items)
    
    return updated_prefs


def _extract_preferences_llm(message: str) -> list[PreferenceItem]:
    """
    Use LLM to extract preferences from message.
    
    Args:
        message: User message
    
    Returns:
        List of extracted preference items
    """
    system_prompt = """You are a preference extraction assistant. Analyze the user's message and extract any travel preferences mentioned.
Return ONLY a JSON array of preferences with this structure:
[
  {"category": "flight_time", "value": "morning", "confidence": 0.8},
  {"category": "cabin_class", "value": "business", "confidence": 0.9}
]

Valid categories: flight_time, cabin_class, airline, max_stops, min_hotel_rating, hotel_budget, amenity, budget_range
Valid values depend on category. Use strings for all values.

If no clear preferences are expressed, return an empty array: []"""

    try:
        response = generate_text(system_prompt, message, temperature=0.3)
        
        # Clean response
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()
        
        prefs_data = json.loads(response)
        
        items = []
        for pref in prefs_data:
            items.append(PreferenceItem(
                category=pref.get("category", "unknown"),
                value=pref.get("value", ""),
                confidence=pref.get("confidence", 0.7),
                source_message=message[:100],
                timestamp=time.time()
            ))
        
        return items
    
    except Exception as e:
        print(f"Error in LLM preference extraction: {e}")
        return []


def merge_preferences(existing: UserPreferences, new_items: list[PreferenceItem]) -> UserPreferences:
    """
    Merge new preference items into existing preferences.
    
    Args:
        existing: Current user preferences
        new_items: Newly extracted preference items
    
    Returns:
        Updated preferences
    """
    if not new_items:
        return existing
    
    # Update preference items list
    for item in new_items:
        existing.preference_items.append(item)
    
    # Apply preferences to top-level fields
    for item in new_items:
        if item.category == "flight_time":
            existing.preferred_flight_time = item.value
        elif item.category == "cabin_class":
            existing.preferred_cabin_class = item.value
        elif item.category == "airline":
            if item.value not in existing.preferred_airlines:
                existing.preferred_airlines.append(item.value)
        elif item.category == "max_stops":
            existing.max_stops = int(item.value)
        elif item.category == "min_hotel_rating":
            existing.min_hotel_rating = float(item.value)
        elif item.category == "hotel_budget":
            existing.preferred_hotel_budget = item.value
        elif item.category == "amenity":
            if item.value not in existing.preferred_amenities:
                existing.preferred_amenities.append(item.value)
        elif item.category == "budget_range":
            existing.preferred_budget_range = item.value
    
    existing.last_updated = time.time()
    
    return existing


def apply_preferences_to_flight_params(
    params: Optional[FlightSearchParams], 
    prefs: UserPreferences
) -> FlightSearchParams:
    """
    Apply user preferences to flight search parameters if not explicitly set.
    
    Args:
        params: Current flight search parameters (may be None)
        prefs: User preferences
    
    Returns:
        Updated flight search parameters
    """
    if params is None:
        params = FlightSearchParams()
    
    # Apply cabin class preference if not set
    if params.cabin_class == "economy" and prefs.preferred_cabin_class:
        params.cabin_class = prefs.preferred_cabin_class
        print(f"[Preferences] Applied cabin class: {prefs.preferred_cabin_class}")
    
    return params


def apply_preferences_to_hotel_params(
    params: Optional[HotelSearchParams], 
    prefs: UserPreferences
) -> HotelSearchParams:
    """
    Apply user preferences to hotel search parameters if not explicitly set.
    
    Args:
        params: Current hotel search parameters (may be None)
        prefs: User preferences
    
    Returns:
        Updated hotel search parameters
    """
    if params is None:
        params = HotelSearchParams()
    
    # Apply minimum rating preference if not set
    if params.min_rating is None and prefs.min_hotel_rating:
        params.min_rating = prefs.min_hotel_rating
        print(f"[Preferences] Applied min hotel rating: {prefs.min_hotel_rating}")
    
    # Apply budget preference if not set
    if params.budget is None and prefs.preferred_hotel_budget:
        params.budget = prefs.preferred_hotel_budget
        print(f"[Preferences] Applied hotel budget: {prefs.preferred_hotel_budget}")
    
    return params


def get_preference_summary(prefs: UserPreferences) -> str:
    """
    Generate a human-readable summary of user preferences.
    
    Args:
        prefs: User preferences
    
    Returns:
        Formatted summary string
    """
    parts = []
    
    if prefs.preferred_flight_time:
        parts.append(f"Prefers {prefs.preferred_flight_time} flights")
    
    if prefs.preferred_cabin_class and prefs.preferred_cabin_class != "economy":
        parts.append(f"Prefers {prefs.preferred_cabin_class} class")
    
    if prefs.max_stops is not None:
        if prefs.max_stops == 0:
            parts.append("Prefers direct flights")
        else:
            parts.append(f"Accepts up to {prefs.max_stops} stops")
    
    if prefs.min_hotel_rating:
        parts.append(f"Prefers {prefs.min_hotel_rating}+ star hotels")
    
    if prefs.preferred_amenities:
        parts.append(f"Likes amenities: {', '.join(prefs.preferred_amenities[:3])}")
    
    return "; ".join(parts) if parts else "No preferences learned yet"
