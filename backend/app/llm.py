"""
LLM Integration using Google Gemini API.

Provides wrapper functions for:
- Text generation
- Intent classification
- Response summarization
"""

import json
from typing import List, Dict, Optional
import google.generativeai as genai

from .config import GEMINI_API_KEY


# ============================================================================
# Gemini Configuration
# ============================================================================

# Configure Gemini API
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
    except Exception as e:
        model = None
        print(f"Warning: Failed to initialize Gemini: {e}")
else:
    model = None
    print("Warning: GEMINI_API_KEY not set. LLM features will be disabled.")


# ============================================================================
# Prompt Templates
# ============================================================================

COORDINATOR_SYSTEM_PROMPT = """You are a travel planning coordinator assistant with advanced natural language understanding. Your job is to:
1. Understand the user's travel intent
2. Extract relevant search parameters
3. Classify the request type
4. Handle vague dates, currency mentions, and corrections

IMPORTANT: Distinguish between SELECTING (user indicates preference) and BOOKING (explicit confirmation to proceed).

NATURAL LANGUAGE UNDERSTANDING RULES:
1. **Vague Dates** - Convert relative dates to absolute YYYY-MM-DD format:
   - "tomorrow" → calculate next day
   - "next weekend" → next Saturday
   - "in 2 weeks" → date 14 days from now
   - "next month" → first day of next month
   - "Christmas" → 2025-12-25
   - Use current date as: 2025-11-21

2. **Currency Handling** - Normalize all currencies to USD:
   - "€500" or "500 euros" → convert to USD equivalent (~$550)
   - "£300" or "300 pounds" → convert to USD equivalent (~$380)
   - "¥50000" or "50000 yen" → convert to USD equivalent (~$350)
   - Always output budget in USD

3. **Corrections** - Detect when user is correcting previous input:
   - "Actually I meant Paris" → update destination to Paris
   - "No, December" → update month to December
   - "I said economy" → update cabin_class to economy
   - Flag corrections with "is_correction": true

Analyze the user's message and conversation context, then respond with a JSON object containing:
- intent: one of ["flight", "hotel", "combined", "refine", "other"]
- flight_params: {origin, destination, depart_date, return_date, passengers, cabin_class, max_stops} (if applicable)
- hotel_params: {city, check_in, check_out, guests, budget, min_rating} (if applicable)
- selected_item: {type: "flight" or "hotel", identifier: airline/hotel name or price, action: "select" or "book"} (if user is selecting/booking)
- is_correction: true (if user is correcting previous input)

STOPS HANDLING:
- "direct flight" or "non-stop" → max_stops: 0
- "1 stop" or "one stop" → max_stops: 1
- "2 stops" or "with connections" → max_stops: 2
- If not mentioned → max_stops: null (show all)

Examples:
User: "I need a flight from New York to LA next month"
Response: {"intent": "flight", "flight_params": {"origin": "NYC", "destination": "LAX", "depart_date": "2025-12-01"}}

User: "Find flights from NYC to London with 1 stop"
Response: {"intent": "flight", "flight_params": {"origin": "NYC", "destination": "LON", "max_stops": 1}}

User: "Direct flights to Paris tomorrow"
Response: {"intent": "flight", "flight_params": {"destination": "Paris", "depart_date": "2025-11-22", "max_stops": 0}}

User: "Find me hotels in Miami for 2 guests, budget €500"
Response: {"intent": "hotel", "hotel_params": {"city": "Miami", "guests": 2, "budget": "550"}}

User: "Flights to Paris tomorrow"
Response: {"intent": "flight", "flight_params": {"destination": "Paris", "depart_date": "2025-11-22"}}

User: "Actually I meant Tokyo"
Response: {"intent": "refine", "flight_params": {"destination": "Tokyo"}, "is_correction": true}

User: "I'll take the JetBlue flight" or "Select the Delta flight"
Response: {"intent": "other", "selected_item": {"type": "flight", "identifier": "JetBlue", "action": "select"}}

User: "Yes, book it" or "Confirm booking" or "Yes, proceed" (AFTER already selecting)
Response: {"intent": "other", "selected_item": {"type": "flight", "identifier": "confirmed", "action": "book"}}

Only respond with valid JSON. Be concise."""


RESPONSE_SYSTEM_PROMPT = """You are a friendly travel assistant. Generate a natural, conversational response that:
1. Summarizes the search results clearly
2. Highlights the best 2-3 options with specific details (airline/hotel name, price)
3. For selections: Confirm their choice and ASK if they want to proceed with booking
4. For booking confirmations: Only then confirm the booking
5. For general questions: Answer helpfully and guide next steps
6. Maintain context from the conversation

CRITICAL RULES:
- NEVER book automatically when user says "I'll take this flight"
- ALWAYS ask "Would you like me to proceed with booking?" or "Shall I book this for you?" after a selection
- ONLY confirm a booking when user explicitly says "yes", "confirm", "book it", "proceed" AFTER you've asked
- For first-time selections: Confirm the choice + Ask for permission to book
- For booking confirmations: State the booking is complete

Guidelines:
- When presenting options: Be specific with names and prices
- When user selects: "Great choice! [Flight details]. Shall I proceed with booking?"
- When user confirms: "Perfect! Your booking is confirmed for [details]."
- Keep responses concise (2-4 sentences) but informative
- Be helpful, enthusiastic, and conversational"""


# ============================================================================
# Core LLM Functions
# ============================================================================

def generate_text(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.7
) -> str:
    """
    Generate text using Gemini.
    
    Args:
        system_prompt: System instructions for the model
        user_message: User's input message
        temperature: Sampling temperature (0.0-1.0)
    
    Returns:
        Generated text response
    """
    if model is None:
        return "LLM not configured (missing API key)"
    
    try:
        # Combine system prompt and user message
        full_prompt = f"{system_prompt}\n\nUser: {user_message}\n\nAssistant:"
        
        # Generate response
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
            )
        )
        
        return response.text.strip()
    
    except Exception as e:
        print(f"Error generating text: {e}")
        return f"Error: {str(e)}"


# ============================================================================
# Specialized LLM Functions
# ============================================================================

def classify_intent(
    user_message: str,
    conversation_history: List[Dict[str, str]] = None
) -> Dict:
    """
    Classify user intent and extract parameters using Gemini.
    
    Args:
        user_message: Latest user message
        conversation_history: Optional list of previous conversation turns
    
    Returns:
        Dict with intent and extracted parameters
    """
    if model is None:
        # Fallback to keyword-based classification
        return _fallback_intent_classification(user_message)
    
    try:
        # Add conversation context if available
        context = ""
        if conversation_history:
            recent_history = conversation_history[-3:]  # Last 3 turns
            context = "\n".join([
                f"{turn['sender']}: {turn['text']}" 
                for turn in recent_history
            ])
            context = f"Recent conversation:\n{context}\n\n"
        
        prompt = f"{context}Current user message: {user_message}"
        
        response_text = generate_text(
            COORDINATOR_SYSTEM_PROMPT,
            prompt,
            temperature=0.3  # Lower temperature for structured output
        )
        
        # Parse JSON response
        # Clean markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        return result
    
    except Exception as e:
        print(f"Error in intent classification: {e}")
        # Fallback to keyword-based
        return _fallback_intent_classification(user_message)


def _fallback_intent_classification(user_message: str) -> Dict:
    """Fallback keyword-based intent classification."""
    message_lower = user_message.lower().strip()
    
    result = {"intent": "other"}
    
    # Very short affirmative responses = likely confirmation
    if message_lower in ["yes", "yeah", "sure", "ok", "yep", "yup", "confirm", "proceed", "book it", "go ahead"]:
        result["intent"] = "other"
        result["selected_item"] = {
            "type": "flight",  # Will be determined by context
            "identifier": "confirmed",
            "action": "book"
        }
        return result
    
    # Check for explicit booking keywords
    if "book it" in message_lower or "confirm" in message_lower or "proceed" in message_lower:
        result["intent"] = "other"
        result["selected_item"] = {
            "type": "flight",
            "identifier": "confirmed",
            "action": "book"
        }
        return result
    
    # Check for selection keywords (user is choosing an option)
    selection_keywords = ["i'll take", "i will take", "select", "choose", "take the", "take that"]
    airline_keywords = ["delta", "united", "american", "southwest", "jetblue", "alaska", "spirit", "frontier", "major airline"]
    
    # Check if user is selecting a flight
    if any(keyword in message_lower for keyword in selection_keywords):
        if "flight" in message_lower or any(airline in message_lower for airline in airline_keywords):
            result["intent"] = "other"
            result["selected_item"] = {
                "type": "flight", 
                "identifier": user_message,
                "action": "select"
            }
            return result
        elif "hotel" in message_lower:
            result["intent"] = "other"
            result["selected_item"] = {
                "type": "hotel", 
                "identifier": user_message,
                "action": "select"
            }
            return result
    
    # Standalone airline/hotel name = selection
    if any(airline in message_lower for airline in airline_keywords) and len(message_lower.split()) <= 4:
        result["intent"] = "other"
        result["selected_item"] = {
            "type": "flight",
            "identifier": user_message,
            "action": "select"
        }
        return result
    
    # Check if user wants to search
    if "flight" in message_lower or "fly" in message_lower or "flying" in message_lower:
        result["intent"] = "flight"
    elif "hotel" in message_lower or "stay" in message_lower or "accommodation" in message_lower:
        result["intent"] = "hotel"
    elif ("flight" in message_lower and "hotel" in message_lower) or "trip" in message_lower or "plan" in message_lower:
        result["intent"] = "combined"
    
    return result


def generate_response_summary(
    intent: str,
    flight_results: list = None,
    hotel_results: list = None,
    user_message: str = "",
    context: dict = None
) -> str:
    """
    Generate natural language summary of search results.
    
    Args:
        intent: User's intent (flight, hotel, combined)
        flight_results: List of flight results
        hotel_results: List of hotel results
        user_message: Original user message for context
        context: Additional context like selected items
    
    Returns:
        Natural language response
    """
    if model is None:
        # Fallback to template-based response
        return _fallback_response_generation(intent, flight_results, hotel_results, context)
    
    try:
        # Build context for LLM
        context_parts = []
        
        if user_message:
            context_parts.append(f"User request: {user_message}")
        
        # Handle selections and bookings
        if context and (context.get("selected_flight") or context.get("pending_flight")):
            action = context.get("action", "select")
            flight_id = context.get("pending_flight") or context.get("selected_flight")
            
            if action == "select" and context.get("pending_flight"):
                # User just selected, ask for confirmation
                context_parts.append(f"User is SELECTING (not booking yet): {flight_id}")
                context_parts.append("IMPORTANT: Response MUST ask 'Would you like me to proceed with booking this flight?' Do NOT confirm booking yet.")
            elif action == "book":
                # User confirmed booking
                context_parts.append(f"User has CONFIRMED BOOKING for: {flight_id}")
                context_parts.append("IMPORTANT: Response MUST confirm booking is complete. Say 'Your booking is confirmed' or similar.")
            
            # If we have matching flights, show them
            if context.get("matching_flights"):
                matching = context["matching_flights"]
                match_summary = "\n".join([
                    f"- {f.get('airline', 'N/A')} {f.get('flight_number', '')}: ${f.get('price', 'N/A')}"
                    for f in matching[:3]
                ])
                context_parts.append(f"Matching available flights:\n{match_summary}")
        
        if context and (context.get("selected_hotel") or context.get("pending_hotel")):
            action = context.get("action", "select")
            hotel_id = context.get("pending_hotel") or context.get("selected_hotel")
            
            if action == "select" and context.get("pending_hotel"):
                context_parts.append(f"User is SELECTING hotel: {hotel_id}")
                context_parts.append("IMPORTANT: Response MUST ask 'Would you like me to proceed with booking this hotel?' Do NOT confirm booking yet.")
            elif action == "book":
                context_parts.append(f"User has CONFIRMED hotel booking: {hotel_id}")
                context_parts.append("IMPORTANT: Response MUST confirm the booking is complete. Say 'Your hotel booking is confirmed' or similar.")
            
            # If we have matching hotels, show them
            if context.get("matching_hotels"):
                matching = context["matching_hotels"]
                match_summary = "\n".join([
                    f"- {h.get('name', 'N/A')}: ${h.get('price_per_night', 'N/A')}/night ({h.get('star_rating', 'N/A')}★)"
                    for h in matching[:3]
                ])
                context_parts.append(f"Matching available hotels:\n{match_summary}")
        
        # Mention confirmed bookings even if we don't have current results
        if context and context.get("selected_flight") and not context.get("pending_flight") and not context.get("matching_flights"):
            # User has a confirmed flight but no current flight results
            context_parts.append(f"User has previously confirmed flight booking: {context['selected_flight']}")
            context_parts.append("Acknowledge this booking in your response if relevant to the current query.")
        
        if context and context.get("selected_hotel") and not context.get("pending_hotel") and not context.get("matching_hotels"):
            # User has a confirmed hotel but no current hotel results
            context_parts.append(f"User has previously confirmed hotel booking: {context['selected_hotel']}")
            context_parts.append("Acknowledge this booking in your response if relevant to the current query.")
        
        if flight_results:
            # Summarize top 3 flights
            top_flights = flight_results[:3]
            flights_summary = "\n".join([
                f"- {f.get('airline', 'N/A')} {f.get('flight_number', '')}: ${f.get('price', 'N/A')} ({f.get('stops', 0)} stops, {f.get('departure_time', '').split('T')[1][:5] if 'T' in f.get('departure_time', '') else 'N/A'})"
                for f in top_flights
            ])
            context_parts.append(f"Available flights ({len(flight_results)} total):\n{flights_summary}")
        
        if hotel_results:
            # Summarize top 3 hotels
            top_hotels = hotel_results[:3]
            hotels_summary = "\n".join([
                f"- {h.get('name', 'N/A')}: ${h.get('price_per_night', 'N/A')}/night ({h.get('star_rating', 'N/A')}★, {h.get('review_score', 'N/A')}/10 rating)"
                for h in top_hotels
            ])
            context_parts.append(f"Available hotels ({len(hotel_results)} total):\n{hotels_summary}")
        
        context_str = "\n\n".join(context_parts)
        
        prompt = f"{context_str}\n\nGenerate a helpful, friendly response to the user."
        
        response = generate_text(
            RESPONSE_SYSTEM_PROMPT,
            prompt,
            temperature=0.8  # Higher temperature for more natural language
        )
        
        return response
    
    except Exception as e:
        print(f"Error generating response: {e}")
        return _fallback_response_generation(intent, flight_results, hotel_results, context)


def generate_response_stream(
    intent: str,
    flight_results: list = None,
    hotel_results: list = None,
    user_message: str = "",
    context: dict = None
):
    """
    Generate natural language summary of search results (Streaming).
    
    Yields:
        Chunks of generated text
    """
    if model is None:
        # Fallback to template-based response (yield as single chunk)
        yield _fallback_response_generation(intent, flight_results, hotel_results, context)
        return
    
    try:
        # Build context for LLM (Reuse logic from generate_response_summary)
        # ... (Ideally we'd refactor this context building into a helper, but for now we duplicate/inline for safety)
        context_parts = []
        
        if user_message:
            context_parts.append(f"User request: {user_message}")
        
        # Handle selections and bookings
        if context and (context.get("selected_flight") or context.get("pending_flight")):
            action = context.get("action", "select")
            flight_id = context.get("pending_flight") or context.get("selected_flight")
            
            if action == "select" and context.get("pending_flight"):
                context_parts.append(f"User is SELECTING (not booking yet): {flight_id}")
                context_parts.append("IMPORTANT: Response MUST ask 'Would you like me to proceed with booking this flight?' Do NOT confirm booking yet.")
            elif action == "book":
                context_parts.append(f"User has CONFIRMED BOOKING for: {flight_id}")
                context_parts.append("IMPORTANT: Response MUST confirm booking is complete. Say 'Your booking is confirmed' or similar.")
            
            if context.get("matching_flights"):
                matching = context["matching_flights"]
                match_summary = "\n".join([
                    f"- {f.get('airline', 'N/A')} {f.get('flight_number', '')}: ${f.get('price', 'N/A')}"
                    for f in matching[:3]
                ])
                context_parts.append(f"Matching available flights:\n{match_summary}")
        
        if context and (context.get("selected_hotel") or context.get("pending_hotel")):
            action = context.get("action", "select")
            hotel_id = context.get("pending_hotel") or context.get("selected_hotel")
            
            if action == "select" and context.get("pending_hotel"):
                context_parts.append(f"User is SELECTING hotel: {hotel_id}")
                context_parts.append("IMPORTANT: Response MUST ask 'Would you like me to proceed with booking this hotel?' Do NOT confirm booking yet.")
            elif action == "book":
                context_parts.append(f"User has CONFIRMED hotel booking: {hotel_id}")
                context_parts.append("IMPORTANT: Response MUST confirm the booking is complete. Say 'Your hotel booking is confirmed' or similar.")
            
            if context.get("matching_hotels"):
                matching = context["matching_hotels"]
                match_summary = "\n".join([
                    f"- {h.get('name', 'N/A')}: ${h.get('price_per_night', 'N/A')}/night ({h.get('star_rating', 'N/A')}★)"
                    for h in matching[:3]
                ])
                context_parts.append(f"Matching available hotels:\n{match_summary}")
        
        # Mention confirmed bookings even if we don't have current results
        if context and context.get("selected_flight") and not context.get("pending_flight") and not context.get("matching_flights"):
            context_parts.append(f"User has previously confirmed flight booking: {context['selected_flight']}")
            context_parts.append("Acknowledge this booking in your response if relevant to the current query.")
        
        if context and context.get("selected_hotel") and not context.get("pending_hotel") and not context.get("matching_hotels"):
            context_parts.append(f"User has previously confirmed hotel booking: {context['selected_hotel']}")
            context_parts.append("Acknowledge this booking in your response if relevant to the current query.")
        
        if flight_results:
            top_flights = flight_results[:3]
            flights_summary = "\n".join([
                f"- {f.get('airline', 'N/A')} {f.get('flight_number', '')}: ${f.get('price', 'N/A')} ({f.get('stops', 0)} stops, {f.get('departure_time', '').split('T')[1][:5] if 'T' in f.get('departure_time', '') else 'N/A'})"
                for f in top_flights
            ])
            context_parts.append(f"Available flights ({len(flight_results)} total):\n{flights_summary}")
        
        if hotel_results:
            top_hotels = hotel_results[:3]
            hotels_summary = "\n".join([
                f"- {h.get('name', 'N/A')}: ${h.get('price_per_night', 'N/A')}/night ({h.get('star_rating', 'N/A')}★, {h.get('review_score', 'N/A')}/10 rating)"
                for h in top_hotels
            ])
            context_parts.append(f"Available hotels ({len(hotel_results)} total):\n{hotels_summary}")
        
        context_str = "\n\n".join(context_parts)
        prompt = f"{context_str}\n\nGenerate a helpful, friendly response to the user."
        
        # Generate streaming response
        full_prompt = f"{RESPONSE_SYSTEM_PROMPT}\n\nUser: {prompt}\n\nAssistant:"
        
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.8,
            ),
            stream=True
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
    
    except Exception as e:
        print(f"Error generating streaming response: {e}")
        yield _fallback_response_generation(intent, flight_results, hotel_results, context)


def _fallback_response_generation(
    intent: str,
    flight_results: Optional[List] = None,
    hotel_results: Optional[List] = None,
    context: Optional[Dict] = None
) -> str:
    """Fallback template-based response generation with alternative suggestions."""
    parts = []
    
    # Handle selections
    if context:
        if context.get("selected_flight"):
            if context.get("matching_flights") and len(context["matching_flights"]) > 0:
                flight = context["matching_flights"][0]
                parts.append(f"Perfect! I found {flight.get('airline')} flight {flight.get('flight_number', '')} for ${flight.get('price')}. Shall I proceed with booking?")
            else:
                parts.append(f"I'd love to help you book {context['selected_flight']}, but let me confirm the details from the available options. Which specific flight would you like?")
            return " ".join(parts)
        if context.get("selected_hotel"):
            parts.append(f"Excellent! I'll help you book {context['selected_hotel']}. Ready to confirm?")
            return " ".join(parts)
    
    # Handle no results with alternative suggestions
    if intent == "flight" and (not flight_results or len(flight_results) == 0):
        parts.append("I couldn't find any flights matching your exact criteria. Here are some suggestions:")
        parts.append("\n• Try flexible dates (±3 days can save money)")
        parts.append("\n• Consider nearby airports")
        parts.append("\n• Check if connecting flights are available")
        parts.append("\n\nWould you like me to search with different parameters?")
        return " ".join(parts)
    
    if intent == "hotel" and (not hotel_results or len(hotel_results) == 0):
        parts.append("I couldn't find any hotels matching your criteria. Here are some alternatives:")
        parts.append("\n• Expand your budget range")
        parts.append("\n• Consider nearby neighborhoods")
        parts.append("\n• Try different check-in dates")
        parts.append("\n• Lower the minimum star rating")
        parts.append("\n\nWould you like me to search with adjusted filters?")
        return " ".join(parts)
    
    if flight_results:
        cheapest = min(flight_results, key=lambda f: f.get('price', float('inf')))
        parts.append(
            f"I found {len(flight_results)} flights for you! "
            f"The cheapest option is ${cheapest.get('price', 'N/A')} with {cheapest.get('airline', 'an airline')}."
        )
    
    if hotel_results:
        best_value = hotel_results[0] if hotel_results else None
        if best_value:
            parts.append(
                f"I also found {len(hotel_results)} hotels. "
                f"Check out {best_value.get('name', 'this hotel')} at ${best_value.get('price_per_night', 'N/A')}/night "
                f"({best_value.get('star_rating', 'N/A')}★ rating)."
            )
    
    if not parts:
        parts.append("I'm ready to help you search for flights and hotels. What are you looking for?")
    
    return " ".join(parts)
