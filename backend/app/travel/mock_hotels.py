"""
Mock Hotel Search API

Generates realistic hotel data for testing and demos without external API calls.
Returns randomized but consistent hotel options.
"""

import random
from datetime import datetime, timedelta
from typing import List, Optional

from ..models import HotelResult, HotelSearchParams


# Mock hotel chains and types
HOTEL_CHAINS = [
    "Hilton",
    "Marriott",
    "Hyatt",
    "Holiday Inn",
    "Best Western",
    "Sheraton",
    "Westin",
    "Radisson",
]

HOTEL_TYPES = [
    "Hotel",
    "Resort",
    "Suites",
    "Inn",
    "Grand Hotel",
]

# Common amenities
AMENITIES_POOL = [
    "WiFi",
    "Pool",
    "Gym",
    "Spa",
    "Restaurant",
    "Bar",
    "Room Service",
    "Parking",
    "Business Center",
    "Airport Shuttle",
    "Pet Friendly",
    "Breakfast Included",
]

# Budget categories with price ranges
BUDGET_RANGES = {
    "budget": (60, 120),
    "mid": (120, 250),
    "luxury": (250, 600),
}


# City coordinates (Lat, Lon)
CITY_COORDINATES = {
    "New York": [40.7128, -74.0060],
    "Los Angeles": [34.0522, -118.2437],
    "Chicago": [41.8781, -87.6298],
    "San Francisco": [37.7749, -122.4194],
    "London": [51.5074, -0.1278],
    "Paris": [48.8566, 2.3522],
    "Tokyo": [35.6762, 139.6503],
    "Dubai": [25.2048, 55.2708],
    "Miami": [25.7617, -80.1918],
    "Las Vegas": [36.1699, -115.1398],
    "Orlando": [28.5383, -81.3792],
    "Boston": [42.3601, -71.0589],
}

# Hotel images from Unsplash
HOTEL_IMAGES = [
    "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1455587734955-081b22074882?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1564501049412-61c2a3083791?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?auto=format&fit=crop&w=800&q=80",
]


def parse_date_safe(date_str: Optional[str], default_days: int = 0) -> datetime:
    """Parse date string safely, falling back to default if invalid."""
    try:
        if date_str:
            return datetime.fromisoformat(date_str)
    except ValueError:
        pass
    return datetime.now() + timedelta(days=default_days)


def generate_hotel_name(city: str, chain: str, hotel_type: str) -> str:
    """Generate a realistic hotel name."""
    return f"{chain} {city} {hotel_type}"


def generate_address(city: str, seed: int) -> str:
    """Generate a mock address."""
    street_num = (seed % 9000) + 100
    streets = ["Main St", "Park Ave", "Ocean Blvd", "Downtown Dr", "Harbor Way", "Airport Rd"]
    street = streets[seed % len(streets)]
    return f"{street_num} {street}, {city}"


def calculate_price_per_night(star_rating: float, budget: Optional[str]) -> float:
    """Calculate price per night based on rating and budget."""
    # Determine budget range
    if budget and budget in BUDGET_RANGES:
        min_price, max_price = BUDGET_RANGES[budget]
    else:
        # Default to mid-range
        min_price, max_price = BUDGET_RANGES["mid"]
    
    # Adjust based on star rating (3.0-5.0 scale)
    rating_factor = (star_rating - 3.0) / 2.0  # 0.0 to 1.0
    price = min_price + (max_price - min_price) * rating_factor
    
    # Add randomization
    variance = random.uniform(0.9, 1.1)
    
    return round(price * variance, 2)


def search_hotels(params: Optional[HotelSearchParams] = None) -> List[HotelResult]:
    """
    Search for hotels based on parameters.
    
    Returns 5-10 mock hotel options with randomized but realistic data.
    """
    if params is None:
        params = HotelSearchParams()
    
    # Use params or defaults
    city = params.city or "Los Angeles"
    
    # Safely parse dates
    check_in_date = parse_date_safe(params.check_in, 0)
    check_out_date = parse_date_safe(params.check_out, 7)
    
    # Ensure check-out is after check-in
    if check_out_date <= check_in_date:
        check_out_date = check_in_date + timedelta(days=1)
        
    nights = (check_out_date - check_in_date).days
    
    guests = params.guests or 1
    budget = params.budget
    min_rating = params.min_rating or 3.0
    
    # Seed randomization based on city for consistency
    random.seed(hash(city))
    
    # Generate 5-10 hotel options
    num_hotels = random.randint(5, 10)
    hotels = []
    
    # Get city coordinates
    city_coords = CITY_COORDINATES.get(city, [34.0522, -118.2437])  # Default to LA
    
    for i in range(num_hotels):
        # Random hotel details
        chain = random.choice(HOTEL_CHAINS)
        hotel_type = random.choice(HOTEL_TYPES)
        name = generate_hotel_name(city, chain, hotel_type)
        
        # Star rating (weighted toward 3-4 stars)
        star_rating = random.choices(
            [2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
            weights=[5, 15, 25, 30, 20, 5]
        )[0]
        
        # Skip if below minimum rating
        if star_rating < min_rating:
            continue
        
        # Review score (correlated with star rating)
        review_score = round(star_rating * 1.7 + random.uniform(-0.5, 0.5), 1)
        review_score = max(1.0, min(10.0, review_score))
        
        # Review count (higher-rated hotels tend to have more reviews)
        review_count = random.randint(50, 500) + int(star_rating * 100)
        
        # Price per night
        price_per_night = calculate_price_per_night(star_rating, budget)
        total_price = round(price_per_night * nights, 2)
        
        # Random amenities (3-8 amenities)
        num_amenities = random.randint(3, 8)
        amenities = random.sample(AMENITIES_POOL, num_amenities)
        
        # Select random images
        hotel_images = random.sample(HOTEL_IMAGES, 3)
        
        # Generate coordinates with small random offset from city center
        # Approx 0.01 degrees is ~1km
        lat_offset = random.uniform(-0.05, 0.05)
        lon_offset = random.uniform(-0.05, 0.05)
        hotel_coords = [city_coords[0] + lat_offset, city_coords[1] + lon_offset]
        
        hotel = HotelResult(
            id=f"hotel_{city.replace(' ', '_')}_{i}",
            name=name,
            city=city,
            address=generate_address(city, i + hash(city)),
            star_rating=star_rating,
            review_score=review_score,
            review_count=review_count,
            price_per_night=price_per_night,
            currency="USD",
            total_price=total_price,
            amenities=sorted(amenities),
            image_url=hotel_images[0],
            images=hotel_images,
            booking_link=f"https://example.com/book/hotel-{city}-{i}",
            is_partial=False,
            coordinates=hotel_coords
        )
        
        hotels.append(hotel)
    
    # Sort by value (review score / price ratio, descending)
    hotels.sort(key=lambda h: h.review_score / (h.price_per_night / 100), reverse=True)
    
    # Reset random seed
    random.seed()
    
    return hotels[:10]  # Return max 10 results


def search_hotels_streaming(params: Optional[HotelSearchParams] = None) -> List[HotelResult]:
    """
    Variant that simulates streaming results in batches.
    
    This is useful for testing partial result handling during interruptions.
    Returns the same results as search_hotels but can be used with asyncio.sleep
    to simulate gradual result arrival.
    """
    # For now, just return all at once
    # In actual implementation with asyncio, this would yield batches
    return search_hotels(params)
