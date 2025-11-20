import { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { MessageList } from './components/MessageList';
import { SmartInput } from './components/SmartInput';
import { PreferencesPanel } from './components/PreferencesPanel';
import AgentStatus from './components/AgentStatus';
import { BookingModal } from './components/BookingModal';
import { useWebSocket } from './hooks/useWebSocket';
import { useTheme } from './contexts/ThemeContext';
import type { Message, FlightResult, HotelResult, WebSocketEvent, PreferencesResponse } from './types';

// Generate or retrieve session ID
const getSessionId = () => {
  let sessionId = sessionStorage.getItem('travel_session_id');
  if (!sessionId) {
    sessionId = Math.random().toString(36).substring(2, 15);
    sessionStorage.setItem('travel_session_id', sessionId);
  }
  return sessionId;
};

function App() {
  const { theme, toggleTheme } = useTheme();
  const [sessionId] = useState(getSessionId);
  const [messages, setMessages] = useState<Message[]>([]);
  const [flightResults, setFlightResults] = useState<FlightResult[]>([]);
  const [hotelResults, setHotelResults] = useState<HotelResult[]>([]);
  const [status, setStatus] = useState<string>('');
  const [preferencesPanelOpen, setPreferencesPanelOpen] = useState(false);
  const [preferencesData, setPreferencesData] = useState<PreferencesResponse | null>(null);
  const [agentStatus, setAgentStatus] = useState<{ agent: string; status: string; step: string } | null>(null);

  // Booking modal state
  const [bookingModalOpen, setBookingModalOpen] = useState(false);
  const [selectedFlightForBooking, setSelectedFlightForBooking] = useState<FlightResult | undefined>();
  const [selectedHotelForBooking, setSelectedHotelForBooking] = useState<HotelResult | undefined>();

  // Fetch preferences on mount
  useEffect(() => {
    const fetchPreferences = async () => {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/chat/${sessionId}/preferences`);
        setPreferencesData(response.data);
      } catch (error) {
        console.error('Failed to fetch preferences:', error);
      }
    };
    fetchPreferences();
  }, [sessionId]);

  // Handle Server-Sent Events (SSE)
  useEffect(() => {
    const eventSource = new EventSource(`http://127.0.0.1:8000/chat/${sessionId}/stream`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('SSE Event:', data);

        if (data.type === 'agent_status') {
          setAgentStatus(data.data);
          // Auto-hide after 5 seconds of inactivity if needed, but for now keep it
        }
      } catch (error) {
        console.error('Error parsing SSE event:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE Error:', error);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [sessionId]);

  // Clear agent status when response is received (via WebSocket)
  useEffect(() => {
    if (status === 'completed' || status === 'cancelled') {
      const timer = setTimeout(() => setAgentStatus(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [status]);

  // Handle WebSocket messages
  const handleWebSocketMessage = useCallback((event: WebSocketEvent) => {
    console.log('Processing WebSocket event:', event.type);

    switch (event.type) {
      case 'status':
        setStatus(event.status);
        break;

      case 'message':
        if (event.sender === 'assistant') {
          setMessages((prev) => [
            ...prev,
            {
              id: event.request_id || Math.random().toString(36),
              sender: 'assistant',
              text: event.text,
              timestamp: Date.now(),
            },
          ]);
        }
        break;

      case 'flight_results':
        setFlightResults(event.results);
        break;

      case 'hotel_results':
        setHotelResults(event.results);
        break;

      case 'error':
        console.error('Error from backend:', event.error);
        setMessages((prev) => [
          ...prev,
          {
            id: Math.random().toString(36),
            sender: 'assistant',
            text: `Error: ${event.error}`,
            timestamp: Date.now(),
          },
        ]);
        break;

      case 'preference_update':
        // Refresh preferences when updated
        axios.get(`http://127.0.0.1:8000/chat/${sessionId}/preferences`)
          .then(response => setPreferencesData(response.data))
          .catch(error => console.error('Failed to refresh preferences:', error));
        break;

      case 'preferences_cleared':
        // Refresh preferences when cleared
        axios.get(`http://127.0.0.1:8000/chat/${sessionId}/preferences`)
          .then(response => setPreferencesData(response.data))
          .catch(error => console.error('Failed to refresh preferences:', error));
        break;

      default:
        console.log('Unhandled event type:', event);
    }
  }, [sessionId]);

  // Connect to WebSocket
  const { connected } = useWebSocket(sessionId, handleWebSocketMessage);

  // Send message to backend
  const handleSendMessage = async (text: string) => {
    // Add user message to UI immediately
    const userMessage: Message = {
      id: Math.random().toString(36),
      sender: 'user',
      text,
      timestamp: Date.now(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Send to backend
    try {
      await axios.post(`http://127.0.0.1:8000/chat/${sessionId}/message`, {
        message: text,
      });
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: Math.random().toString(36),
          sender: 'assistant',
          text: 'Failed to send message. Please try again.',
          timestamp: Date.now(),
        },
      ]);
    }
  };

  // Handle selection
  const handleSelectFlight = (flight: FlightResult) => {
    handleSendMessage(`I'll take the ${flight.airline} flight ${flight.flight_number} to ${flight.destination} for $${flight.price}.`);
    setFlightResults([]);
  };

  const handleSelectHotel = (hotel: HotelResult) => {
    handleSendMessage(`I'd like to book ${hotel.name} in ${hotel.city} for $${hotel.price_per_night}/night.`);
    setHotelResults([]);
  };

  const handleBookFlight = (flight: FlightResult) => {
    setSelectedFlightForBooking(flight);
    setBookingModalOpen(true);
    // Clear results after selecting
    setFlightResults([]);
    setHotelResults([]);
  };

  const handleBookHotel = (hotel: HotelResult) => {
    setSelectedHotelForBooking(hotel);
    setBookingModalOpen(true);
    // Clear results after selecting
    setFlightResults([]);
    setHotelResults([]);
  };

  return (
    <div
      style={{
        height: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        padding: '20px',
        background: theme === 'dark'
          ? 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)'
          : 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
        transition: 'background 0.3s ease'
      }}
      className="fade-in"
    >
      {/* Glassmorphism Container */}
      <div
        style={{
          width: '100%',
          maxWidth: '1000px',
          height: '90vh',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: theme === 'dark'
            ? 'rgba(30, 41, 59, 0.85)'
            : 'rgba(255, 255, 255, 0.85)',
          backdropFilter: 'blur(12px)',
          borderRadius: '24px',
          boxShadow: theme === 'dark'
            ? '0 8px 32px 0 rgba(0, 0, 0, 0.6)'
            : '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
          border: theme === 'dark'
            ? '1px solid rgba(255, 255, 255, 0.1)'
            : '1px solid rgba(255, 255, 255, 0.18)',
          overflow: 'hidden',
          position: 'relative',
          transition: 'all 0.3s ease'
        }}
        className="scale-in"
      >
        {/* Agent Status Overlay */}
        {agentStatus && (
          <AgentStatus
            agent={agentStatus.agent}
            status={agentStatus.status}
            step={agentStatus.step}
            isVisible={true}
          />
        )}

        {/* Header */}
        <div
          style={{
            padding: '20px 30px',
            backgroundColor: theme === 'dark'
              ? 'rgba(30, 41, 59, 0.95)'
              : 'rgba(255, 255, 255, 0.9)',
            borderBottom: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)'}`,
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            transition: 'all 0.3s ease'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '20px',
              color: 'white',
              boxShadow: '0 4px 6px -1px rgba(59, 130, 246, 0.5)'
            }}>
              ✈️
            </div>
            <div>
              <h1 style={{
                margin: 0,
                fontSize: '18px',
                fontWeight: '700',
                color: theme === 'dark' ? '#f1f5f9' : '#1e293b',
                transition: 'color 0.3s ease'
              }}>
                Travel Assistant
              </h1>
              <span style={{
                fontSize: '12px',
                color: theme === 'dark' ? '#94a3b8' : '#64748b',
                transition: 'color 0.3s ease'
              }}>
                AI-Powered Trip Planner
              </span>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {/* Dark Mode Toggle */}
            <button
              onClick={toggleTheme}
              style={{
                width: '40px',
                height: '40px',
                borderRadius: '10px',
                backgroundColor: theme === 'dark' ? '#334155' : '#f8fafc',
                border: `1px solid ${theme === 'dark' ? '#475569' : '#e2e8f0'}`,
                color: theme === 'dark' ? '#fbbf24' : '#f59e0b',
                fontSize: '20px',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'scale(1.1)';
                e.currentTarget.style.backgroundColor = theme === 'dark' ? '#475569' : '#f1f5f9';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.backgroundColor = theme === 'dark' ? '#334155' : '#f8fafc';
              }}
              title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
            >
              {theme === 'dark' ? '☀️' : '🌙'}
            </button>

            {/* Preferences Button */}
            <button
              onClick={() => setPreferencesPanelOpen(true)}
              style={{
                position: 'relative',
                padding: '8px 16px',
                backgroundColor: theme === 'dark' ? '#334155' : '#f8fafc',
                border: `1px solid ${theme === 'dark' ? '#475569' : '#e2e8f0'}`,
                borderRadius: '10px',
                color: theme === 'dark' ? '#cbd5e1' : '#475569',
                fontSize: '13px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = theme === 'dark' ? '#475569' : '#f1f5f9';
                e.currentTarget.style.borderColor = theme === 'dark' ? '#64748b' : '#cbd5e1';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = theme === 'dark' ? '#334155' : '#f8fafc';
                e.currentTarget.style.borderColor = theme === 'dark' ? '#475569' : '#e2e8f0';
              }}
            >
              🎯 Preferences
              {preferencesData && preferencesData.preference_items.length > 0 && (
                <span style={{
                  backgroundColor: '#3b82f6',
                  color: 'white',
                  fontSize: '10px',
                  fontWeight: '700',
                  padding: '2px 6px',
                  borderRadius: '10px',
                  minWidth: '18px',
                  textAlign: 'center'
                }}>
                  {preferencesData.preference_items.length}
                </span>
              )}
            </button>

            {/* Connection Status */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 12px',
              borderRadius: '20px',
              backgroundColor: connected
                ? (theme === 'dark' ? 'rgba(34, 197, 94, 0.2)' : 'rgba(220, 252, 231, 0.5)')
                : (theme === 'dark' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(254, 226, 226, 0.5)'),
              border: `1px solid ${connected
                ? (theme === 'dark' ? '#22c55e' : '#86efac')
                : (theme === 'dark' ? '#ef4444' : '#fca5a5')}`,
              transition: 'all 0.3s ease'
            }}>
              <div style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: connected ? '#16a34a' : '#dc2626',
                boxShadow: connected ? '0 0 8px #16a34a' : 'none',
                animation: connected ? 'pulse 2s infinite' : 'none'
              }} />
              <span style={{
                fontSize: '12px',
                fontWeight: '600',
                color: connected
                  ? (theme === 'dark' ? '#86efac' : '#166534')
                  : (theme === 'dark' ? '#fca5a5' : '#991b1b'),
                transition: 'color 0.3s ease'
              }}>
                {connected ? 'Online' : 'Offline'}
              </span>
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <MessageList
          messages={messages}
          flightResults={flightResults}
          hotelResults={hotelResults}
          status={status}
          onSelectFlight={handleSelectFlight}
          onSelectHotel={handleSelectHotel}
          onBookFlight={handleBookFlight}
          onBookHotel={handleBookHotel}
        />

        {/* Input Area */}
        <SmartInput onSend={handleSendMessage} disabled={!connected} />
      </div>

      {/* Preferences Panel */}
      <PreferencesPanel
        sessionId={sessionId}
        isOpen={preferencesPanelOpen}
        onClose={() => setPreferencesPanelOpen(false)}
      />

      {/* Booking Modal */}
      <BookingModal
        isOpen={bookingModalOpen}
        onClose={() => {
          setBookingModalOpen(false);
          setSelectedFlightForBooking(undefined);
          setSelectedHotelForBooking(undefined);
        }}
        flight={selectedFlightForBooking}
        hotel={selectedHotelForBooking}
        sessionId={sessionId}
        onBookingComplete={(bookingRef, itineraryHtml) => {
          // Add confirmation message
          setMessages(prev => [...prev, {
            id: Math.random().toString(36),
            sender: 'assistant',
            text: `🎉 Booking confirmed! Your reference is ${bookingRef}. Check your email for the itinerary.`,
            timestamp: Date.now()
          }]);

          // Open itinerary in new tab
          const blob = new Blob([itineraryHtml], { type: 'text/html' });
          const url = URL.createObjectURL(blob);
          window.open(url, '_blank');
        }}
      />
    </div>
  );
}

export default App;
