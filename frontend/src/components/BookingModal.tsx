import React, { useState, useEffect } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import type { FlightResult, HotelResult } from '../types';

interface BookingModalProps {
    isOpen: boolean;
    onClose: () => void;
    flight?: FlightResult;
    hotel?: HotelResult;
    sessionId: string;
    onBookingComplete: (bookingRef: string, itineraryHtml: string) => void;
}

type BookingStep = 'passenger' | 'seat' | 'payment' | 'confirmation' | 'guest' | 'room';

export function BookingModal({ isOpen, onClose, flight, hotel, sessionId, onBookingComplete }: BookingModalProps) {
    const { theme } = useTheme();
    const isHotelBooking = !!hotel && !flight;
    const [step, setStep] = useState<BookingStep>(isHotelBooking ? 'guest' : 'passenger');
    const [passengerInfo, setPassengerInfo] = useState({
        first_name: '',
        last_name: '',
        email: '',
        phone: ''
    });
    const [guestInfo, setGuestInfo] = useState({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        check_in: '',
        check_out: '',
        guests: '1'
    });
    const [selectedSeat, setSelectedSeat] = useState<string | null>(null);
    const [selectedRoom, setSelectedRoom] = useState<string>('Standard Room');
    const [paymentInfo, setPaymentInfo] = useState({
        card_number: '',
        expiry: '',
        cvv: '',
        name: ''
    });
    const [bookingRef, setBookingRef] = useState('');
    const [itineraryHtml, setItineraryHtml] = useState('');
    const [isProcessing, setIsProcessing] = useState(false);

    // Reset the booking step when modal opens or booking type changes
    useEffect(() => {
        if (isOpen) {
            setStep(isHotelBooking ? 'guest' : 'passenger');
            // Reset form data
            setPassengerInfo({ first_name: '', last_name: '', email: '', phone: '' });
            setGuestInfo({ first_name: '', last_name: '', email: '', phone: '', check_in: '', check_out: '', guests: '1' });
            setSelectedSeat(null);
            setSelectedRoom('Standard Room');
            setPaymentInfo({ card_number: '', expiry: '', cvv: '', name: '' });
            setBookingRef('');
            setItineraryHtml('');
        }
    }, [isOpen, isHotelBooking]);

    if (!isOpen) return null;

    const handleDownloadItinerary = () => {
        if (!itineraryHtml) return;
        
        const blob = new Blob([itineraryHtml], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Itinerary-${bookingRef}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const handlePassengerSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setStep('seat');
    };

    const handleGuestSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setStep('room');
    };

    const handleSeatSelect = (seat: string) => {
        setSelectedSeat(seat);
    };

    const handleRoomSelect = (room: string) => {
        setSelectedRoom(room);
    };

    const handlePaymentSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsProcessing(true);

        try {
            const bookingData = isHotelBooking ? {
                hotel_id: hotel?.id,
                passenger_info: {
                    first_name: guestInfo.first_name,
                    last_name: guestInfo.last_name,
                    email: guestInfo.email,
                    phone: guestInfo.phone
                },
                room_type: selectedRoom,
                check_in: guestInfo.check_in,
                check_out: guestInfo.check_out,
                guests: guestInfo.guests,
                payment_info: paymentInfo
            } : {
                flight_id: flight?.id,
                passenger_info: passengerInfo,
                seat: selectedSeat,
                payment_info: paymentInfo
            };

            const response = await fetch(`http://localhost:8000/chat/${sessionId}/book`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bookingData)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
                console.error('Booking failed:', errorData);
                throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            setBookingRef(data.booking_reference);
            setItineraryHtml(data.itinerary_html);
            setStep('confirmation');
            onBookingComplete(data.booking_reference, data.itinerary_html);
        } catch (error) {
            console.error('Booking failed:', error);
            alert(`Booking failed: ${error instanceof Error ? error.message : 'Please try again.'}`);
        } finally {
            setIsProcessing(false);
        }
    };

    const renderSeatGrid = () => {
        const rows = ['A', 'B', 'C', 'D', 'E', 'F'];
        const seats = [];
        for (let row = 1; row <= 20; row++) {
            for (const col of rows) {
                const seatNum = `${row}${col}`;
                const isOccupied = Math.random() > 0.7; // Mock occupied seats
                seats.push({ num: seatNum, occupied: isOccupied });
            }
        }
        return seats;
    };

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            backdropFilter: 'blur(4px)'
        }}>
            <div style={{
                backgroundColor: theme === 'dark' ? '#1e293b' : 'white',
                borderRadius: '16px',
                maxWidth: '600px',
                width: '90%',
                maxHeight: '80vh',
                overflow: 'auto',
                boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
            }}>
                {/* Header */}
                <div style={{
                    padding: '24px',
                    borderBottom: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                    color: 'white',
                    borderTopLeftRadius: '16px',
                    borderTopRightRadius: '16px'
                }}>
                    <h2 style={{ margin: 0, fontSize: '20px' }}>
                        {step === 'passenger' && '✈️ Passenger Details'}
                        {step === 'seat' && '💺 Select Your Seat'}
                        {step === 'guest' && '🏨 Guest Information'}
                        {step === 'room' && '🛏️ Select Room Type'}
                        {step === 'payment' && '💳 Payment Information'}
                        {step === 'confirmation' && '✅ Booking Confirmed!'}
                    </h2>
                    <button onClick={onClose} style={{
                        background: 'none',
                        border: 'none',
                        color: 'white',
                        fontSize: '24px',
                        cursor: 'pointer',
                        padding: '0',
                        width: '32px',
                        height: '32px'
                    }}>×</button>
                </div>

                {/* Content */}
                <div style={{ padding: '24px' }}>
                    {step === 'passenger' && (
                        <form onSubmit={handlePassengerSubmit}>
                            <div style={{ marginBottom: '16px' }}>
                                <label style={{ 
                                    display: 'block', 
                                    marginBottom: '4px', 
                                    fontSize: '14px', 
                                    fontWeight: '600',
                                    color: theme === 'dark' ? '#cbd5e1' : '#0f172a'
                                }}>First Name</label>
                                <input
                                    type="text"
                                    required
                                    value={passengerInfo.first_name}
                                    onChange={(e) => setPassengerInfo({ ...passengerInfo, first_name: e.target.value })}
                                    style={{ 
                                        width: '100%', 
                                        padding: '10px', 
                                        borderRadius: '8px', 
                                        border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                        backgroundColor: theme === 'dark' ? '#0f172a' : 'white',
                                        color: theme === 'dark' ? '#f1f5f9' : '#0f172a'
                                    }}
                                />
                            </div>
                            <div style={{ marginBottom: '16px' }}>
                                <label style={{ 
                                    display: 'block', 
                                    marginBottom: '4px', 
                                    fontSize: '14px', 
                                    fontWeight: '600',
                                    color: theme === 'dark' ? '#cbd5e1' : '#0f172a'
                                }}>Last Name</label>
                                <input
                                    type="text"
                                    required
                                    value={passengerInfo.last_name}
                                    onChange={(e) => setPassengerInfo({ ...passengerInfo, last_name: e.target.value })}
                                    style={{ 
                                        width: '100%', 
                                        padding: '10px', 
                                        borderRadius: '8px', 
                                        border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                        backgroundColor: theme === 'dark' ? '#0f172a' : 'white',
                                        color: theme === 'dark' ? '#f1f5f9' : '#0f172a'
                                    }}
                                />
                            </div>
                            <div style={{ marginBottom: '16px' }}>
                                <label style={{ 
                                    display: 'block', 
                                    marginBottom: '4px', 
                                    fontSize: '14px', 
                                    fontWeight: '600',
                                    color: theme === 'dark' ? '#cbd5e1' : '#0f172a'
                                }}>Email</label>
                                <input
                                    type="email"
                                    required
                                    value={passengerInfo.email}
                                    onChange={(e) => setPassengerInfo({ ...passengerInfo, email: e.target.value })}
                                    style={{ 
                                        width: '100%', 
                                        padding: '10px', 
                                        borderRadius: '8px', 
                                        border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                        backgroundColor: theme === 'dark' ? '#0f172a' : 'white',
                                        color: theme === 'dark' ? '#f1f5f9' : '#0f172a'
                                    }}
                                />
                            </div>
                            <div style={{ marginBottom: '24px' }}>
                                <label style={{ 
                                    display: 'block', 
                                    marginBottom: '4px', 
                                    fontSize: '14px', 
                                    fontWeight: '600',
                                    color: theme === 'dark' ? '#cbd5e1' : '#0f172a'
                                }}>Phone</label>
                                <input
                                    type="tel"
                                    required
                                    value={passengerInfo.phone}
                                    onChange={(e) => setPassengerInfo({ ...passengerInfo, phone: e.target.value })}
                                    style={{ 
                                        width: '100%', 
                                        padding: '10px', 
                                        borderRadius: '8px', 
                                        border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                        backgroundColor: theme === 'dark' ? '#0f172a' : 'white',
                                        color: theme === 'dark' ? '#f1f5f9' : '#0f172a'
                                    }}
                                />
                            </div>
                            <button type="submit" style={{
                                width: '100%',
                                padding: '12px',
                                backgroundColor: '#3b82f6',
                                color: 'white',
                                border: 'none',
                                borderRadius: '8px',
                                fontSize: '16px',
                                fontWeight: '600',
                                cursor: 'pointer'
                            }}>Continue to Seat Selection</button>
                        </form>
                    )}

                    {step === 'guest' && (
                        <form onSubmit={handleGuestSubmit}>
                            <div style={{ marginBottom: '16px' }}>
                                <label style={{ 
                                    display: 'block', 
                                    marginBottom: '4px', 
                                    fontSize: '14px', 
                                    fontWeight: '600',
                                    color: theme === 'dark' ? '#cbd5e1' : '#0f172a'
                                }}>First Name</label>
                                <input
                                    type="text"
                                    required
                                    value={guestInfo.first_name}
                                    onChange={(e) => setGuestInfo({ ...guestInfo, first_name: e.target.value })}
                                    style={{ 
                                        width: '100%', 
                                        padding: '10px', 
                                        borderRadius: '8px', 
                                        border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                        backgroundColor: theme === 'dark' ? '#0f172a' : 'white',
                                        color: theme === 'dark' ? '#f1f5f9' : '#0f172a'
                                    }}
                                />
                            </div>
                            <div style={{ marginBottom: '16px' }}>
                                <label style={{ 
                                    display: 'block', 
                                    marginBottom: '4px', 
                                    fontSize: '14px', 
                                    fontWeight: '600',
                                    color: theme === 'dark' ? '#cbd5e1' : '#0f172a'
                                }}>Last Name</label>
                                <input
                                    type="text"
                                    required
                                    value={guestInfo.last_name}
                                    onChange={(e) => setGuestInfo({ ...guestInfo, last_name: e.target.value })}
                                    style={{ 
                                        width: '100%', 
                                        padding: '10px', 
                                        borderRadius: '8px', 
                                        border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                        backgroundColor: theme === 'dark' ? '#0f172a' : 'white',
                                        color: theme === 'dark' ? '#f1f5f9' : '#0f172a'
                                    }}
                                />
                            </div>
                            <div style={{ marginBottom: '16px' }}>
                                <label style={{ 
                                    display: 'block', 
                                    marginBottom: '4px', 
                                    fontSize: '14px', 
                                    fontWeight: '600',
                                    color: theme === 'dark' ? '#cbd5e1' : '#0f172a'
                                }}>Email</label>
                                <input
                                    type="email"
                                    required
                                    value={guestInfo.email}
                                    onChange={(e) => setGuestInfo({ ...guestInfo, email: e.target.value })}
                                    style={{ 
                                        width: '100%', 
                                        padding: '10px', 
                                        borderRadius: '8px', 
                                        border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                        backgroundColor: theme === 'dark' ? '#0f172a' : 'white',
                                        color: theme === 'dark' ? '#f1f5f9' : '#0f172a'
                                    }}
                                />
                            </div>
                            <div style={{ marginBottom: '16px' }}>
                                <label style={{ 
                                    display: 'block', 
                                    marginBottom: '4px', 
                                    fontSize: '14px', 
                                    fontWeight: '600',
                                    color: theme === 'dark' ? '#cbd5e1' : '#0f172a'
                                }}>Phone</label>
                                <input
                                    type="tel"
                                    required
                                    value={guestInfo.phone}
                                    onChange={(e) => setGuestInfo({ ...guestInfo, phone: e.target.value })}
                                    style={{ 
                                        width: '100%', 
                                        padding: '10px', 
                                        borderRadius: '8px', 
                                        border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                        backgroundColor: theme === 'dark' ? '#0f172a' : 'white',
                                        color: theme === 'dark' ? '#f1f5f9' : '#0f172a'
                                    }}
                                />
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                                <div>
                                    <label style={{ 
                                        display: 'block', 
                                        marginBottom: '4px', 
                                        fontSize: '14px', 
                                        fontWeight: '600',
                                        color: theme === 'dark' ? '#cbd5e1' : '#0f172a'
                                    }}>Check-in Date</label>
                                    <input
                                        type="date"
                                        required
                                        value={guestInfo.check_in}
                                        onChange={(e) => setGuestInfo({ ...guestInfo, check_in: e.target.value })}
                                        style={{ 
                                            width: '100%', 
                                            padding: '10px', 
                                            borderRadius: '8px', 
                                            border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                            backgroundColor: theme === 'dark' ? '#0f172a' : 'white',
                                            color: theme === 'dark' ? '#f1f5f9' : '#0f172a'
                                        }}
                                    />
                                </div>
                                <div>
                                    <label style={{ 
                                        display: 'block', 
                                        marginBottom: '4px', 
                                        fontSize: '14px', 
                                        fontWeight: '600',
                                        color: theme === 'dark' ? '#cbd5e1' : '#0f172a'
                                    }}>Check-out Date</label>
                                    <input
                                        type="date"
                                        required
                                        value={guestInfo.check_out}
                                        onChange={(e) => setGuestInfo({ ...guestInfo, check_out: e.target.value })}
                                        style={{ 
                                            width: '100%', 
                                            padding: '10px', 
                                            borderRadius: '8px', 
                                            border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                            backgroundColor: theme === 'dark' ? '#0f172a' : 'white',
                                            color: theme === 'dark' ? '#f1f5f9' : '#0f172a'
                                        }}
                                    />
                                </div>
                            </div>
                            <div style={{ marginBottom: '24px' }}>
                                <label style={{ 
                                    display: 'block', 
                                    marginBottom: '4px', 
                                    fontSize: '14px', 
                                    fontWeight: '600',
                                    color: theme === 'dark' ? '#cbd5e1' : '#0f172a'
                                }}>Number of Guests</label>
                                <select
                                    value={guestInfo.guests}
                                    onChange={(e) => setGuestInfo({ ...guestInfo, guests: e.target.value })}
                                    style={{ 
                                        width: '100%', 
                                        padding: '10px', 
                                        borderRadius: '8px', 
                                        border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                        backgroundColor: theme === 'dark' ? '#0f172a' : 'white',
                                        color: theme === 'dark' ? '#f1f5f9' : '#0f172a'
                                    }}
                                >
                                    <option value="1">1 Guest</option>
                                    <option value="2">2 Guests</option>
                                    <option value="3">3 Guests</option>
                                    <option value="4">4 Guests</option>
                                    <option value="5">5+ Guests</option>
                                </select>
                            </div>
                            <button type="submit" style={{
                                width: '100%',
                                padding: '12px',
                                backgroundColor: '#3b82f6',
                                color: 'white',
                                border: 'none',
                                borderRadius: '8px',
                                fontSize: '16px',
                                fontWeight: '600',
                                cursor: 'pointer'
                            }}>Continue to Room Selection</button>
                        </form>
                    )}

                    {step === 'room' && (
                        <div>
                            <p style={{ 
                                marginBottom: '16px', 
                                color: theme === 'dark' ? '#94a3b8' : '#64748b' 
                            }}>Select your room type</p>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
                                {['Standard Room', 'Deluxe Room', 'Suite', 'Executive Suite'].map((room) => (
                                    <button
                                        key={room}
                                        onClick={() => handleRoomSelect(room)}
                                        style={{
                                            padding: '16px',
                                            border: selectedRoom === room 
                                                ? '2px solid #3b82f6' 
                                                : `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                            borderRadius: '8px',
                                            backgroundColor: selectedRoom === room 
                                                ? (theme === 'dark' ? '#1e3a8a' : '#eff6ff')
                                                : (theme === 'dark' ? '#0f172a' : 'white'),
                                            cursor: 'pointer',
                                            fontSize: '14px',
                                            fontWeight: selectedRoom === room ? '600' : '400',
                                            color: theme === 'dark' ? '#f1f5f9' : '#0f172a',
                                            textAlign: 'left',
                                            transition: 'all 0.2s'
                                        }}
                                    >
                                        <div style={{ fontSize: '16px', marginBottom: '4px' }}>{room}</div>
                                        <div style={{ fontSize: '12px', color: theme === 'dark' ? '#94a3b8' : '#64748b' }}>
                                            {room === 'Standard Room' && '2 Guests • Queen Bed'}
                                            {room === 'Deluxe Room' && '3 Guests • King Bed • City View'}
                                            {room === 'Suite' && '4 Guests • King Bed • Living Room'}
                                            {room === 'Executive Suite' && '5 Guests • Premium Amenities'}
                                        </div>
                                    </button>
                                ))}
                            </div>
                            <button
                                onClick={() => setStep('payment')}
                                style={{
                                    width: '100%',
                                    padding: '12px',
                                    backgroundColor: '#3b82f6',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '8px',
                                    fontSize: '16px',
                                    fontWeight: '600',
                                    cursor: 'pointer'
                                }}
                            >Continue to Payment</button>
                        </div>
                    )}

                    {step === 'seat' && (
                        <div>
                            <p style={{ 
                                marginBottom: '16px', 
                                color: theme === 'dark' ? '#94a3b8' : '#64748b' 
                            }}>Select your preferred seat</p>
                            <div style={{
                                display: 'grid',
                                gridTemplateColumns: 'repeat(6, 1fr)',
                                gap: '8px',
                                marginBottom: '24px',
                                maxHeight: '300px',
                                overflow: 'auto'
                            }}>
                                {renderSeatGrid().map((seat) => (
                                    <button
                                        key={seat.num}
                                        disabled={seat.occupied}
                                        onClick={() => handleSeatSelect(seat.num)}
                                        style={{
                                            padding: '8px',
                                            border: selectedSeat === seat.num 
                                                ? '2px solid #3b82f6' 
                                                : `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                            borderRadius: '6px',
                                            backgroundColor: seat.occupied 
                                                ? (theme === 'dark' ? '#1e293b' : '#f1f5f9')
                                                : (selectedSeat === seat.num 
                                                    ? '#eff6ff' 
                                                    : (theme === 'dark' ? '#0f172a' : 'white')),
                                            cursor: seat.occupied ? 'not-allowed' : 'pointer',
                                            fontSize: '12px',
                                            fontWeight: selectedSeat === seat.num ? '600' : '400',
                                            color: seat.occupied 
                                                ? '#94a3b8' 
                                                : (theme === 'dark' ? '#f1f5f9' : '#0f172a')
                                        }}
                                    >
                                        {seat.num}
                                    </button>
                                ))}
                            </div>
                            <button
                                onClick={() => setStep('payment')}
                                disabled={!selectedSeat}
                                style={{
                                    width: '100%',
                                    padding: '12px',
                                    backgroundColor: selectedSeat ? '#3b82f6' : '#cbd5e1',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '8px',
                                    fontSize: '16px',
                                    fontWeight: '600',
                                    cursor: selectedSeat ? 'pointer' : 'not-allowed'
                                }}
                            >Continue to Payment</button>
                        </div>
                    )}

                    {step === 'payment' && (
                        <form onSubmit={handlePaymentSubmit}>
                            <div style={{ marginBottom: '16px' }}>
                                <label style={{ 
                                    display: 'block', 
                                    marginBottom: '4px', 
                                    fontSize: '14px', 
                                    fontWeight: '600',
                                    color: theme === 'dark' ? '#cbd5e1' : '#0f172a'
                                }}>Card Number</label>
                                <input
                                    type="text"
                                    required
                                    placeholder="1234 5678 9012 3456"
                                    value={paymentInfo.card_number}
                                    onChange={(e) => setPaymentInfo({ ...paymentInfo, card_number: e.target.value })}
                                    style={{ 
                                        width: '100%', 
                                        padding: '10px', 
                                        borderRadius: '8px', 
                                        border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                        backgroundColor: theme === 'dark' ? '#0f172a' : 'white',
                                        color: theme === 'dark' ? '#f1f5f9' : '#0f172a'
                                    }}
                                />
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                                <div>
                                    <label style={{ 
                                        display: 'block', 
                                        marginBottom: '4px', 
                                        fontSize: '14px', 
                                        fontWeight: '600',
                                        color: theme === 'dark' ? '#cbd5e1' : '#0f172a'
                                    }}>Expiry</label>
                                    <input
                                        type="text"
                                        required
                                        placeholder="MM/YY"
                                        value={paymentInfo.expiry}
                                        onChange={(e) => setPaymentInfo({ ...paymentInfo, expiry: e.target.value })}
                                        style={{ 
                                            width: '100%', 
                                            padding: '10px', 
                                            borderRadius: '8px', 
                                            border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                            backgroundColor: theme === 'dark' ? '#0f172a' : 'white',
                                            color: theme === 'dark' ? '#f1f5f9' : '#0f172a'
                                        }}
                                    />
                                </div>
                                <div>
                                    <label style={{ 
                                        display: 'block', 
                                        marginBottom: '4px', 
                                        fontSize: '14px', 
                                        fontWeight: '600',
                                        color: theme === 'dark' ? '#cbd5e1' : '#0f172a'
                                    }}>CVV</label>
                                    <input
                                        type="text"
                                        required
                                        placeholder="123"
                                        value={paymentInfo.cvv}
                                        onChange={(e) => setPaymentInfo({ ...paymentInfo, cvv: e.target.value })}
                                        style={{ 
                                            width: '100%', 
                                            padding: '10px', 
                                            borderRadius: '8px', 
                                            border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                            backgroundColor: theme === 'dark' ? '#0f172a' : 'white',
                                            color: theme === 'dark' ? '#f1f5f9' : '#0f172a'
                                        }}
                                    />
                                </div>
                            </div>
                            <div style={{ marginBottom: '24px' }}>
                                <label style={{ 
                                    display: 'block', 
                                    marginBottom: '4px', 
                                    fontSize: '14px', 
                                    fontWeight: '600',
                                    color: theme === 'dark' ? '#cbd5e1' : '#0f172a'
                                }}>Cardholder Name</label>
                                <input
                                    type="text"
                                    required
                                    value={paymentInfo.name}
                                    onChange={(e) => setPaymentInfo({ ...paymentInfo, name: e.target.value })}
                                    style={{ 
                                        width: '100%', 
                                        padding: '10px', 
                                        borderRadius: '8px', 
                                        border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                                        backgroundColor: theme === 'dark' ? '#0f172a' : 'white',
                                        color: theme === 'dark' ? '#f1f5f9' : '#0f172a'
                                    }}
                                />
                            </div>
                            <button type="submit" disabled={isProcessing} style={{
                                width: '100%',
                                padding: '12px',
                                backgroundColor: isProcessing ? '#cbd5e1' : '#16a34a',
                                color: 'white',
                                border: 'none',
                                borderRadius: '8px',
                                fontSize: '16px',
                                fontWeight: '600',
                                cursor: isProcessing ? 'not-allowed' : 'pointer'
                            }}>
                                {isProcessing ? 'Processing...' : `Pay $${flight?.price || hotel?.price_per_night || 0}`}
                            </button>
                        </form>
                    )}                    {step === 'confirmation' && (
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '64px', marginBottom: '16px' }}>🎉</div>
                            <h3 style={{ 
                                margin: '0 0 8px', 
                                color: '#16a34a'
                            }}>Booking Confirmed!</h3>
                            <p style={{ 
                                color: theme === 'dark' ? '#94a3b8' : '#64748b', 
                                marginBottom: '16px' 
                            }}>Your booking reference is:</p>
                            <div style={{
                                padding: '16px',
                                backgroundColor: theme === 'dark' ? '#022c22' : '#f0fdf4',
                                borderRadius: '8px',
                                fontSize: '24px',
                                fontWeight: '700',
                                color: '#16a34a',
                                marginBottom: '24px',
                                letterSpacing: '2px'
                            }}>{bookingRef}</div>
                            <p style={{ 
                                fontSize: '14px', 
                                color: theme === 'dark' ? '#94a3b8' : '#64748b', 
                                marginBottom: '24px' 
                            }}>
                                A confirmation email has been sent to {passengerInfo.email}
                            </p>
                            
                            <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
                                <button onClick={handleDownloadItinerary} style={{
                                    flex: 1,
                                    padding: '12px',
                                    backgroundColor: '#16a34a',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '8px',
                                    fontSize: '14px',
                                    fontWeight: '600',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '8px'
                                }}>
                                    <span>📥</span>
                                    <span>Download Itinerary</span>
                                </button>
                                
                                <button onClick={() => {
                                    const printWindow = window.open('', '_blank');
                                    if (printWindow && itineraryHtml) {
                                        printWindow.document.write(itineraryHtml);
                                        printWindow.document.close();
                                        printWindow.print();
                                    }
                                }} style={{
                                    flex: 1,
                                    padding: '12px',
                                    backgroundColor: '#3b82f6',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '8px',
                                    fontSize: '14px',
                                    fontWeight: '600',
                                    cursor: 'pointer',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '8px'
                                }}>
                                    <span>🖨️</span>
                                    <span>Print</span>
                                </button>
                            </div>
                            
                            <button onClick={onClose} style={{
                                width: '100%',
                                padding: '12px',
                                backgroundColor: '#f1f5f9',
                                color: '#475569',
                                border: '1px solid #e2e8f0',
                                borderRadius: '8px',
                                fontSize: '16px',
                                fontWeight: '600',
                                cursor: 'pointer'
                            }}>Close</button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
