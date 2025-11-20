"""
Booking Service for generating itineraries and handling mock notifications.
"""
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

def generate_itinerary_html(booking_details: Dict[str, Any]) -> str:
    """
    Generate a beautiful HTML itinerary for the booking.
    Supports both flight and hotel bookings.
    """
    flight = booking_details.get("flight")
    hotel = booking_details.get("hotel")
    passenger = booking_details.get("passenger", {})
    seat = booking_details.get("seat", "Any")
    booking_ref = booking_details.get("booking_reference", "Unknown")
    room_type = booking_details.get("room_type", "Standard")
    check_in = booking_details.get("check_in", "")
    check_out = booking_details.get("check_out", "")
    guests = booking_details.get("guests", "1")
    
    # Determine if it's a flight or hotel booking
    is_flight = flight is not None
    
    if is_flight:
        # Flight booking HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Flight Itinerary - {booking_ref}</title>
            <style>
                body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; line-height: 1.6; background-color: #f4f4f4; padding: 20px; }}
                .ticket {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; letter-spacing: 1px; }}
                .header p {{ margin: 5px 0 0; opacity: 0.9; }}
                .content {{ padding: 30px; }}
                .flight-route {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-bottom: 2px dashed #eee; padding-bottom: 20px; }}
                .airport {{ text-align: center; }}
                .code {{ font-size: 36px; font-weight: 800; color: #1e293b; display: block; }}
                .city {{ font-size: 14px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }}
                .plane-icon {{ font-size: 24px; color: #3b82f6; transform: rotate(90deg); }}
                .details-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
                .detail-item label {{ display: block; font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }}
                .detail-item span {{ font-size: 16px; font-weight: 600; color: #0f172a; }}
                .footer {{ background: #f8fafc; padding: 20px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
                .barcode {{ height: 40px; background: repeating-linear-gradient(90deg, #333 0, #333 2px, transparent 2px, transparent 4px); width: 200px; margin: 0 auto; opacity: 0.8; }}
            </style>
        </head>
        <body>
            <div class="ticket">
                <div class="header">
                    <h1>✈️ Boarding Pass</h1>
                    <p>Booking Reference: {booking_ref}</p>
                </div>
                <div class="content">
                    <div class="flight-route">
                        <div class="airport">
                            <span class="code">{flight.get('origin', '???')}</span>
                            <span class="city">Origin</span>
                        </div>
                        <div class="plane-icon">✈</div>
                        <div class="airport">
                            <span class="code">{flight.get('destination', '???')}</span>
                            <span class="city">Destination</span>
                        </div>
                    </div>
                    
                    <div class="details-grid">
                        <div class="detail-item">
                            <label>Passenger</label>
                            <span>{passenger.get('first_name', '')} {passenger.get('last_name', '')}</span>
                        </div>
                        <div class="detail-item">
                            <label>Flight</label>
                            <span>{flight.get('airline', '')} {flight.get('flight_number', '')}</span>
                        </div>
                        <div class="detail-item">
                            <label>Date</label>
                            <span>{flight.get('departure_time', '').split('T')[0]}</span>
                        </div>
                        <div class="detail-item">
                            <label>Time</label>
                            <span>{flight.get('departure_time', '').split('T')[1][:5]}</span>
                        </div>
                        <div class="detail-item">
                            <label>Seat</label>
                            <span>{seat}</span>
                        </div>
                        <div class="detail-item">
                            <label>Class</label>
                            <span>{flight.get('cabin_class', 'Economy').title()}</span>
                        </div>
                    </div>
                    
                    <div class="barcode"></div>
                </div>
                <div class="footer">
                    <p>Thank you for choosing Travel Assistant. Have a safe flight!</p>
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    else:
        # Hotel booking HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Hotel Reservation - {booking_ref}</title>
            <style>
                body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #333; line-height: 1.6; background-color: #f4f4f4; padding: 20px; }}
                .ticket {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; letter-spacing: 1px; }}
                .header p {{ margin: 5px 0 0; opacity: 0.9; }}
                .content {{ padding: 30px; }}
                .hotel-info {{ text-align: center; margin-bottom: 30px; border-bottom: 2px dashed #eee; padding-bottom: 20px; }}
                .hotel-name {{ font-size: 28px; font-weight: 800; color: #1e293b; margin-bottom: 8px; }}
                .hotel-city {{ font-size: 16px; color: #64748b; }}
                .details-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 30px; }}
                .detail-item label {{ display: block; font-size: 12px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }}
                .detail-item span {{ font-size: 16px; font-weight: 600; color: #0f172a; }}
                .full-width {{ grid-column: 1 / -1; }}
                .footer {{ background: #f8fafc; padding: 20px; text-align: center; font-size: 12px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
                .barcode {{ height: 40px; background: repeating-linear-gradient(90deg, #333 0, #333 2px, transparent 2px, transparent 4px); width: 200px; margin: 0 auto; opacity: 0.8; }}
            </style>
        </head>
        <body>
            <div class="ticket">
                <div class="header">
                    <h1>🏨 Hotel Reservation</h1>
                    <p>Booking Reference: {booking_ref}</p>
                </div>
                <div class="content">
                    <div class="hotel-info">
                        <div class="hotel-name">{hotel.get('name', 'Hotel') if hotel else 'Hotel'}</div>
                        <div class="hotel-city">{hotel.get('city', '') if hotel else ''}</div>
                    </div>
                    
                    <div class="details-grid">
                        <div class="detail-item">
                            <label>Guest Name</label>
                            <span>{passenger.get('first_name', '')} {passenger.get('last_name', '')}</span>
                        </div>
                        <div class="detail-item">
                            <label>Room Type</label>
                            <span>{room_type}</span>
                        </div>
                        <div class="detail-item">
                            <label>Check-in</label>
                            <span>{check_in}</span>
                        </div>
                        <div class="detail-item">
                            <label>Check-out</label>
                            <span>{check_out}</span>
                        </div>
                        <div class="detail-item">
                            <label>Guests</label>
                            <span>{guests}</span>
                        </div>
                        <div class="detail-item">
                            <label>Email</label>
                            <span>{passenger.get('email', '')}</span>
                        </div>
                    </div>
                    
                    <div class="barcode"></div>
                </div>
                <div class="footer">
                    <p>Thank you for choosing Travel Assistant. Enjoy your stay!</p>
                    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    return html

def send_mock_email(to_email: str, subject: str, body: str):
    """
    Simulate sending an email by logging it.
    """
    logger.info(f"📧 MOCK EMAIL SENT TO: {to_email}")
    logger.info(f"Subject: {subject}")
    logger.info(f"Body length: {len(body)} chars")
    return True
