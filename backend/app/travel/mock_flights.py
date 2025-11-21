"""
Mock Flight Search API

Generates realistic flight data for testing and demos without external API calls.
Returns randomized but consistent flight options including multi-leg itineraries.
"""

import random
from datetime import datetime, timedelta
from typing import List, Optional

from ..models import FlightResult, FlightSearchParams, FlightSegment


# Mock airline data
AIRLINES = [
    "United Airlines",
    "Delta Air Lines",
    "American Airlines",
    "Southwest Airlines",
    "JetBlue Airways",
    "Alaska Airlines",
    "Spirit Airlines",
    "Frontier Airlines",
]

# Common airport codes with city names
AIRPORTS = {
    "JFK": "New York",
    "LAX": "Los Angeles",
    "ORD": "Chicago",
    "ATL": "Atlanta",
    "DFW": "Dallas",
    "DEN": "Denver",
    "SFO": "San Francisco",
    "SEA": "Seattle",
    "MIA": "Miami",
    "LAS": "Las Vegas",
    "MCO": "Orlando",
    "BOS": "Boston",
    "PHX": "Phoenix",
    "IAH": "Houston",
}

# Airport coordinates (Lat, Lon)
AIRPORT_COORDINATES = {
    "JFK": [40.6413, -73.7781],
    "LAX": [33.9416, -118.4085],
    "ORD": [41.9742, -87.9073],
    "ATL": [33.6407, -84.4277],
    "DFW": [32.8998, -97.0403],
    "DEN": [39.8561, -104.6737],
    "SFO": [37.6213, -122.3790],
    "SEA": [47.4502, -122.3088],
    "MIA": [25.7959, -80.2870],
    "LAS": [36.0840, -115.1537],
    "MCO": [28.4312, -81.3081],
    "BOS": [42.3656, -71.0096],
    "PHX": [33.4341, -112.0080],
    "IAH": [29.9902, -95.3368],
    "LHR": [51.4700, -0.4543],  # London Heathrow
    "CDG": [49.0097, 2.5479],   # Paris Charles de Gaulle
    "HND": [35.5494, 139.7798], # Tokyo Haneda
    "NRT": [35.7653, 140.3864], # Tokyo Narita
    "DXB": [25.2532, 55.3657],  # Dubai
    "SYD": [-33.9399, 151.1753], # Sydney
    "SIN": [1.3644, 103.9915],  # Singapore
    "HKG": [22.3080, 113.9185], # Hong Kong
    "FRA": [50.0379, 8.5622],   # Frankfurt
    "AMS": [52.3105, 4.7683],   # Amsterdam
}

# Common layover cities for multi-leg flights
LAYOVER_HUBS = ["ORD", "ATL", "DFW", "DEN", "LHR", "CDG", "DXB", "SIN"]

# Cabin class price multipliers
CABIN_MULTIPLIERS = {
    "economy": 1.0,
    "premium_economy": 1.5,
    "business": 3.0,
    "first": 5.0,
}


def parse_date_safe(date_str: Optional[str], default_days: int = 30) -> datetime:
    """Parse date string safely, falling back to default if invalid."""
    try:
        if date_str:
            return datetime.fromisoformat(date_str)
    except ValueError:
        pass
    return datetime.now() + timedelta(days=default_days)


def generate_flight_number(airline: str, seed: int) -> str:
    """Generate a realistic flight number."""
    prefix = airline.split()[0][:2].upper()
    number = (seed % 9000) + 1000
    return f"{prefix}{number}"


import math

def calculate_distance(origin: str, destination: str) -> float:
    """Calculate distance in km between two airports using Haversine formula."""
    # Get coordinates or default to approximate US center
    coord1 = AIRPORT_COORDINATES.get(origin, [39.8, -98.6])
    coord2 = AIRPORT_COORDINATES.get(destination, [39.8, -98.6])
    
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    R = 6371  # Earth radius in km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    
    return d

def calculate_duration(origin: str, destination: str) -> int:
    """Calculate approximate flight duration in minutes based on distance."""
    distance = calculate_distance(origin, destination)
    
    # Average speed ~800 km/h + 30 min taxi/takeoff/landing
    duration = int((distance / 800) * 60 + 30)
    
    return duration

def calculate_base_price(duration_minutes: int, stops: int) -> float:
    """Calculate base price based on duration and stops."""
    # Base formula: $0.15 per minute + base fee
    # Short flights are more expensive per minute
    base_fare = 50
    minute_rate = 0.8 if duration_minutes < 120 else 0.5
    
    price = base_fare + (duration_minutes * minute_rate)
    
    # Stops usually make it cheaper (unless it's a hack)
    # But for this mock, let's say stops add a small tax but the overall fare might be lower due to routing
    # Let's just make it simple:
    if stops > 0:
        price *= 0.85  # 15% cheaper for connecting flights
        
    # Add randomization
    variance = random.uniform(0.9, 1.3)
    
    return round(price * variance, 2)


def generate_multi_leg_flight(
    origin: str,
    destination: str,
    depart_datetime: datetime,
    cabin_class: str,
    stops: int,
    flight_index: int
) -> FlightResult:
    """Generate a multi-leg flight with realistic segments and layovers."""
    segments = []
    layovers = []
    
    # Choose layover cities
    layover_cities = random.sample([city for city in LAYOVER_HUBS if city not in [origin, destination]], stops)
    
    # Build the route: origin -> layover1 -> layover2 -> ... -> destination
    route = [origin] + layover_cities + [destination]
    
    current_time = depart_datetime
    total_flight_time = 0
    total_layover_time = 0
    
    for i in range(len(route) - 1):
        seg_origin = route[i]
        seg_destination = route[i + 1]
        
        # Calculate segment duration
        seg_duration = calculate_duration(seg_origin, seg_destination)
        total_flight_time += seg_duration
        
        # Random airline for segment
        airline = random.choice(AIRLINES)
        
        seg_arrival = current_time + timedelta(minutes=seg_duration)
        
        # Create segment
        segment = FlightSegment(
            airline=airline,
            flight_number=generate_flight_number(airline, flight_index + i),
            origin=seg_origin,
            destination=seg_destination,
            departure_time=current_time.isoformat(),
            arrival_time=seg_arrival.isoformat(),
            duration_minutes=seg_duration,
            origin_coordinates=AIRPORT_COORDINATES.get(seg_origin),
            destination_coordinates=AIRPORT_COORDINATES.get(seg_destination),
            aircraft=random.choice(["Boeing 737", "Airbus A320", "Boeing 777", "Airbus A350"])
        )
        segments.append(segment)
        
        # Add layover if not the last segment
        if i < len(route) - 2:
            layover_duration = random.randint(45, 180)  # 45 min to 3 hours
            total_layover_time += layover_duration
            
            layovers.append({
                "city": AIRPORTS.get(seg_destination, seg_destination),
                "airport_code": seg_destination,
                "duration_minutes": layover_duration
            })
            
            current_time = seg_arrival + timedelta(minutes=layover_duration)
        else:
            current_time = seg_arrival
    
    # Total journey time includes flight time and layovers
    total_journey_duration = total_flight_time + total_layover_time
    
    # Calculate price (multi-leg flights are often cheaper)
    base_price = calculate_base_price(total_flight_time, stops)
    cabin_multiplier = CABIN_MULTIPLIERS.get(cabin_class, 1.0)
    # Apply discount for connections
    connection_discount = 0.85 if stops > 0 else 1.0
    final_price = round(base_price * cabin_multiplier * connection_discount, 2)
    
    # Use the first segment's airline as the main airline
    main_airline = segments[0].airline if segments else random.choice(AIRLINES)
    
    return FlightResult(
        id=f"flight_{origin}_{destination}_{flight_index}_multileg",
        airline=main_airline,
        flight_number=segments[0].flight_number if segments else generate_flight_number(main_airline, flight_index),
        origin=origin,
        destination=destination,
        departure_time=depart_datetime.isoformat(),
        arrival_time=current_time.isoformat(),
        duration_minutes=total_flight_time,
        stops=stops,
        price=final_price,
        currency="USD",
        cabin_class=cabin_class,
        booking_link=f"https://example.com/book/{origin}-{destination}-{flight_index}",
        is_partial=False,
        origin_coordinates=AIRPORT_COORDINATES.get(origin),
        destination_coordinates=AIRPORT_COORDINATES.get(destination),
        segments=segments,
        layovers=layovers,
        total_journey_duration=total_journey_duration
    )


def search_flights(params: Optional[FlightSearchParams] = None) -> List[FlightResult]:
    """
    Search for flights based on parameters.
    
    Returns 5-10 mock flight options with randomized but realistic data.
    Includes both direct and multi-leg flights with connection details.
    """
    if params is None:
        params = FlightSearchParams()
    
    # Use params or defaults
    origin = params.origin or "JFK"
    destination = params.destination or "LAX"
    # Safely parse date
    depart_datetime = parse_date_safe(params.depart_date, 30)
    depart_date = depart_datetime.strftime("%Y-%m-%d")
    
    cabin_class = params.cabin_class or "economy"
    
    # Seed randomization based on origin/destination for consistency
    random.seed(hash(origin + destination))
    
    # Generate 5-10 flight options
    num_flights = random.randint(5, 10)
    flights = []
    
    print(f"[Flight Search] Generating {num_flights} flights from {origin} to {destination}, max_stops filter: {params.max_stops if params and params.max_stops is not None else 'None (all)'}")
    
    base_duration = calculate_duration(origin, destination)
    
    for i in range(num_flights):
        # Random airline
        airline = random.choice(AIRLINES)
        
        # Force a mix of stops to ensure variety
        # i % 3 == 0 -> Direct (0 stops)
        # i % 3 == 1 -> 1 Stop
        # i % 3 == 2 -> 2 Stops
        if i == 0:
            stops = 1 # Force first flight to have 1 stop for debugging
        elif i % 3 == 0:
            stops = 0
        elif i % 3 == 1:
            stops = 1
        else:
            stops = 2
            
        print(f"[Flight Search] Flight {i}: Initial stops={stops}")

        # Override if max_stops is set and lower than generated
        if params.max_stops is not None and stops > params.max_stops:
             print(f"[Flight Search] Flight {i}: Reducing stops from {stops} to max {params.max_stops}")
             stops = random.randint(0, params.max_stops)
        
        print(f"[Flight Search] Flight {i}: Final stops={stops}")
        
        # Random departure time (spread throughout the day)
        
        # Random departure time (spread throughout the day)
        # Add index to ensure different times for each flight
        hour = (random.randint(5, 22) + i) % 18 + 5  # Ensures variety, keeps in 5-22 range
        minute = random.choice([0, 15, 30, 45])
        
        # Use the parsed datetime as base
        flight_depart_datetime = depart_datetime.replace(hour=hour, minute=minute)
        
        # Generate multi-leg flight if it has stops
        if stops > 0:
            flight = generate_multi_leg_flight(
                origin, destination, flight_depart_datetime, cabin_class, stops, i
            )
        else:
            # Direct flight (no segments)
            duration = base_duration
            arrival_datetime = flight_depart_datetime + timedelta(minutes=duration)
            
            # Calculate price
            base_price = calculate_base_price(duration, stops)
            cabin_multiplier = CABIN_MULTIPLIERS.get(cabin_class, 1.0)
            final_price = round(base_price * cabin_multiplier, 2)
            
            flight = FlightResult(
                id=f"flight_{origin}_{destination}_{i}",
                airline=airline,
                flight_number=generate_flight_number(airline, i + hash(origin)),
                origin=origin,
                destination=destination,
                departure_time=flight_depart_datetime.isoformat(),
                arrival_time=arrival_datetime.isoformat(),
                duration_minutes=duration,
                stops=0,
                price=final_price,
                currency="USD",
                cabin_class=cabin_class,
                booking_link=f"https://example.com/book/{origin}-{destination}-{i}",
                is_partial=False,
                origin_coordinates=AIRPORT_COORDINATES.get(origin),
                destination_coordinates=AIRPORT_COORDINATES.get(destination),
                segments=[],
                layovers=[],
                total_journey_duration=duration
            )
        
        flights.append(flight)
    
    print(f"[Flight Search] Generated {len(flights)} flights before filtering")
    
    # Filter by max_stops if specified
    if params.max_stops is not None:
        flights = [f for f in flights if f.stops <= params.max_stops]
        print(f"[Flight Search] After max_stops filter ({params.max_stops}): {len(flights)} flights remaining")
    
    # Sort by price (cheapest first)
    flights.sort(key=lambda f: f.price)
    
    # Reset random seed
    random.seed()
    
    return flights


def search_flights_streaming(params: Optional[FlightSearchParams] = None) -> List[FlightResult]:
    """
    Variant that simulates streaming results in batches.
    
    This is useful for testing partial result handling during interruptions.
    Returns the same results as search_flights but can be used with asyncio.sleep
    to simulate gradual result arrival.
    """
    # For now, just return all at once
    # In actual implementation with asyncio, this would yield batches
    return search_flights(params)
