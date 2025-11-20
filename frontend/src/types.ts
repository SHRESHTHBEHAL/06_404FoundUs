// Type definitions for chat messages and WebSocket events

export interface Message {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: number;
}

export interface FlightSegment {
  airline: string;
  flight_number?: string;
  origin: string;
  destination: string;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  origin_coordinates?: [number, number];
  destination_coordinates?: [number, number];
  aircraft?: string;
}

export interface FlightLayover {
  city: string;
  duration_minutes: number;
}

export interface FlightResult {
  id: string;
  airline: string;
  flight_number: string;
  origin: string;
  destination: string;
  departure_time: string;
  arrival_time: string;
  duration_minutes: number;
  stops: number;
  price: number;
  currency: string;
  booking_link?: string;
  is_partial?: boolean;
  origin_coordinates?: [number, number];
  destination_coordinates?: [number, number];
  segments?: FlightSegment[];
  layovers?: FlightLayover[];
  total_journey_duration?: number;
}

export interface HotelResult {
  id: string;
  name: string;
  city: string;
  star_rating: number;
  review_score: number;
  review_count: number;
  price_per_night: number;
  currency: string;
  amenities: string[];
  booking_link?: string;
  is_partial?: boolean;
  coordinates?: [number, number];
  images?: string[];
  image_url?: string;
}

export interface ConversationSummary {
  summary: string;
  turn_count: number;
  start_timestamp: number;
  end_timestamp: number;
}

export interface PreferenceItem {
  category: string;
  value: string;
  confidence: number;
  source_message?: string;
  timestamp: number;
}

export interface UserPreferences {
  preferred_flight_time?: string;
  preferred_cabin_class?: string;
  preferred_airlines: string[];
  max_stops?: number;
  min_hotel_rating?: number;
  preferred_hotel_budget?: string;
  preferred_amenities: string[];
  preferred_budget_range?: string;
  last_updated?: number;
}

export interface PreferencesResponse {
  session_id: string;
  preferences: UserPreferences;
  preference_items: PreferenceItem[];
  summary: string;
}

export type WebSocketEvent =
  | { type: 'status'; status: string; session_id: string }
  | { type: 'message'; sender: 'user' | 'assistant'; text: string; session_id: string; request_id?: string }
  | { type: 'flight_results'; results: FlightResult[]; session_id: string }
  | { type: 'hotel_results'; results: HotelResult[]; session_id: string }
  | { type: 'error'; error: string; session_id: string }
  | { type: 'preference_update'; preference: { category: string; value: string }; session_id: string }
  | { type: 'preferences_cleared'; session_id: string }
  | { type: 'echo'; data: string };
