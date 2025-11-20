import { useEffect, useRef } from 'react';
import type { Message, FlightResult, HotelResult } from '../types';
import { FlightMap } from './Visualizations/FlightMap';
import { HotelMap } from './Visualizations/HotelMap';
import { PriceChart } from './Visualizations/PriceChart';
import { FlightTimeline } from './Visualizations/FlightTimeline';
import { useTheme } from '../contexts/ThemeContext';
import { SearchingSkeleton } from './LoadingSkeleton';

interface MessageListProps {
  messages: Message[];
  flightResults: FlightResult[];
  hotelResults: HotelResult[];
  status: string;
  onSelectFlight?: (flight: FlightResult) => void;
  onSelectHotel?: (hotel: HotelResult) => void;
  onBookFlight?: (flight: FlightResult) => void;
  onBookHotel?: (hotel: HotelResult) => void;
}

export function MessageList({ messages, flightResults, hotelResults, status, onSelectFlight, onSelectHotel, onBookFlight, onBookHotel }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const { theme } = useTheme();

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, flightResults, hotelResults, status]);

  // Helper for status badge
  const getStatusBadge = (status: string) => {
    const badgeStyle = {
      padding: '6px 12px',
      borderRadius: '20px',
      fontSize: '12px',
      fontWeight: '600',
      display: 'flex',
      alignItems: 'center',
      gap: '6px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
      animation: 'fadeIn 0.3s ease-out'
    };

    if (status === 'processing') return <span style={{ ...badgeStyle, backgroundColor: '#e0f2fe', color: '#0284c7' }}>🔄 Processing request...</span>;
    if (status === 'cancelling_previous') return <span style={{ ...badgeStyle, backgroundColor: '#fee2e2', color: '#991b1b' }}>⚠️ Interrupted - Updating...</span>;
    if (status === 'cancelled') return <span style={{ ...badgeStyle, backgroundColor: '#fef2f2', color: '#ef4444' }}>❌ Search Cancelled</span>;
    if (status === 'completed') return <span style={{ ...badgeStyle, backgroundColor: '#dcfce7', color: '#166534' }}>✅ Search Completed</span>;
    return null;
  };

  return (
    <div style={{
      flex: 1,
      overflowY: 'auto',
      padding: '24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      scrollBehavior: 'smooth'
    }}>
      {messages.length === 0 && (
        <div style={{
          textAlign: 'center',
          marginTop: '100px',
          color: theme === 'dark' ? '#64748b' : '#94a3b8',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '16px'
        }}
          className="fade-in"
        >
          <div style={{ fontSize: '48px', opacity: 0.5 }}>✈️</div>
          <div>
            <h3 style={{ margin: 0, color: theme === 'dark' ? '#cbd5e1' : '#475569' }}>Where to next?</h3>
            <p style={{ margin: '8px 0 0', fontSize: '14px' }}>Try "Flights to Paris next week" or "Hotels in Tokyo"</p>
          </div>
        </div>
      )}

      {messages.map((msg) => (
        <div
          key={msg.id}
          style={{
            alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
            maxWidth: '80%',
            display: 'flex',
            gap: '12px',
            flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row',
            animation: 'slideIn 0.3s ease-out'
          }}
        >
          {/* Avatar */}
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            backgroundColor: msg.sender === 'user' ? '#3b82f6' : '#10b981',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '18px',
            flexShrink: 0,
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            color: 'white'
          }}>
            {msg.sender === 'user' ? '👤' : '🤖'}
          </div>

          {/* Message Bubble */}
          <div style={{
            padding: '16px 20px',
            borderRadius: '20px',
            borderTopRightRadius: msg.sender === 'user' ? '4px' : '20px',
            borderTopLeftRadius: msg.sender === 'assistant' ? '4px' : '20px',
            backgroundColor: msg.sender === 'user'
              ? '#3b82f6'
              : theme === 'dark' ? '#1e293b' : 'white',
            background: msg.sender === 'user'
              ? 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)'
              : theme === 'dark' ? '#1e293b' : 'white',
            color: msg.sender === 'user'
              ? 'white'
              : theme === 'dark' ? '#e2e8f0' : '#1e293b',
            boxShadow: theme === 'dark'
              ? '0 2px 8px rgba(0,0,0,0.3)'
              : '0 2px 8px rgba(0,0,0,0.05)',
            lineHeight: '1.6',
            fontSize: '15px',
            transition: 'all 0.3s ease'
          }}>
            {msg.text}
          </div>
        </div>
      ))}

      {/* Status Indicator */}
      {status && status !== 'connected' && (
        <div style={{
          alignSelf: status === 'processing' ? 'flex-start' : 'center',
          margin: '10px 0',
          zIndex: 10,
          width: status === 'processing' ? '100%' : 'auto',
          paddingLeft: status === 'processing' ? '48px' : '0'
        }}>
          {status === 'processing' ? (
            <SearchingSkeleton />
          ) : (
            getStatusBadge(status)
          )}
        </div>
      )}

      {/* Flight Results */}
      {flightResults.length > 0 && (
        <div style={{
          alignSelf: 'flex-start',
          width: '100%',
          paddingLeft: '48px', // Align with assistant text
          animation: 'fadeIn 0.5s ease-out'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '16px',
            color: '#64748b',
            fontSize: '13px',
            fontWeight: '600',
            letterSpacing: '0.5px'
          }}>
            <span>✈️</span> FLIGHT OPTIONS
            {flightResults[0].is_partial && (
              <span style={{
                backgroundColor: '#fef3c7',
                color: '#d97706',
                padding: '2px 8px',
                borderRadius: '10px',
                fontSize: '10px'
              }}>PARTIAL RESULTS</span>
            )}
          </div>

          {/* Flight Map */}
          {flightResults[0].origin_coordinates && flightResults[0].destination_coordinates && (
            <FlightMap
              origin={flightResults[0].origin_coordinates}
              destination={flightResults[0].destination_coordinates}
              originCode={flightResults[0].origin}
              destinationCode={flightResults[0].destination}
            />
          )}

          {/* Price Chart */}
          <PriceChart data={flightResults.slice(0, 5)} type="flight" />

          {/* Flight Timeline */}
          <FlightTimeline flights={flightResults} />

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '16px',
            marginTop: '20px',
            opacity: status === 'cancelled' ? 0.7 : 1,
            filter: status === 'cancelled' ? 'grayscale(100%)' : 'none',
            transition: 'all 0.3s ease'
          }}>
            {flightResults.slice(0, 4).map((flight, idx) => (
              <div
                key={idx}
                style={{
                  padding: '20px',
                  borderRadius: '16px',
                  backgroundColor: theme === 'dark' ? '#1e293b' : 'white',
                  boxShadow: theme === 'dark'
                    ? '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)'
                    : '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
                  border: `1px solid ${theme === 'dark' ? '#334155' : '#f1f5f9'}`,
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'hidden'
                }}
                className="slide-in"
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = theme === 'dark'
                    ? '0 10px 15px -3px rgba(0, 0, 0, 0.5)'
                    : '0 10px 15px -3px rgba(0, 0, 0, 0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = theme === 'dark'
                    ? '0 4px 6px -1px rgba(0, 0, 0, 0.3)'
                    : '0 4px 6px -1px rgba(0, 0, 0, 0.05)';
                }}
              >
                {flight.is_partial && (
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    right: 0,
                    backgroundColor: '#fffbeb',
                    color: '#b45309',
                    fontSize: '10px',
                    padding: '4px 8px',
                    borderBottomLeftRadius: '8px',
                    fontWeight: '600'
                  }}>PARTIAL</div>
                )}

                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{
                      width: '32px',
                      height: '32px',
                      backgroundColor: theme === 'dark' ? '#334155' : '#eff6ff',
                      borderRadius: '8px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '16px'
                    }}>✈️</div>
                    <div>
                      <div style={{
                        fontWeight: '700',
                        color: theme === 'dark' ? '#f1f5f9' : '#0f172a',
                        fontSize: '15px'
                      }}>{flight.airline}</div>
                      <div style={{
                        color: theme === 'dark' ? '#94a3b8' : '#64748b',
                        fontSize: '12px'
                      }}>{flight.flight_number}</div>
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '18px', fontWeight: '700', color: '#2563eb' }}>${flight.price}</div>
                    <div style={{
                      fontSize: '12px',
                      color: theme === 'dark' ? '#94a3b8' : '#64748b'
                    }}>round trip</div>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{
                      fontSize: '20px',
                      fontWeight: '700',
                      color: theme === 'dark' ? '#f1f5f9' : '#1e293b'
                    }}>{flight.departure_time.split('T')[1].slice(0, 5)}</div>
                    <div style={{
                      fontSize: '12px',
                      color: theme === 'dark' ? '#94a3b8' : '#64748b',
                      fontWeight: '500'
                    }}>{flight.origin}</div>
                  </div>

                  <div style={{ flex: 2, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                    <div style={{
                      fontSize: '11px',
                      color: theme === 'dark' ? '#64748b' : '#94a3b8'
                    }}>
                      {flight.total_journey_duration 
                        ? `${Math.floor(flight.total_journey_duration / 60)}h ${flight.total_journey_duration % 60}m`
                        : `${Math.floor(flight.duration_minutes / 60)}h ${flight.duration_minutes % 60}m`
                      }
                    </div>
                    <div style={{
                      width: '100%',
                      height: '2px',
                      backgroundColor: theme === 'dark' ? '#475569' : '#e2e8f0',
                      position: 'relative',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}>
                      {flight.stops === 0 ? (
                        <div style={{
                          position: 'absolute',
                          top: '-3px',
                          left: '50%',
                          transform: 'translateX(-50%)',
                          width: '6px',
                          height: '6px',
                          borderRadius: '50%',
                          backgroundColor: theme === 'dark' ? '#64748b' : '#cbd5e1'
                        }}></div>
                      ) : (
                        <>
                          {Array.from({ length: flight.stops }).map((_, idx) => (
                            <div key={idx} style={{
                              position: 'absolute',
                              top: '-3px',
                              left: `${((idx + 1) / (flight.stops + 1)) * 100}%`,
                              transform: 'translateX(-50%)',
                              width: '8px',
                              height: '8px',
                              borderRadius: '50%',
                              backgroundColor: '#f59e0b',
                              border: '2px solid ' + (theme === 'dark' ? '#1e293b' : 'white')
                            }}></div>
                          ))}
                        </>
                      )}
                    </div>
                    <div style={{
                      fontSize: '11px',
                      color: theme === 'dark' ? '#94a3b8' : '#64748b'
                    }}>{flight.stops === 0 ? 'Direct' : `${flight.stops} Stop(s)`}</div>
                    {flight.layovers && flight.layovers.length > 0 && (
                      <div style={{
                        fontSize: '10px',
                        color: theme === 'dark' ? '#64748b' : '#94a3b8',
                        marginTop: '2px'
                      }}>
                        via {flight.layovers.map((l: any) => l.city).join(', ')}
                      </div>
                    )}
                  </div>

                  <div style={{ flex: 1, textAlign: 'right' }}>
                    <div style={{
                      fontSize: '20px',
                      fontWeight: '700',
                      color: theme === 'dark' ? '#f1f5f9' : '#1e293b'
                    }}>{flight.arrival_time.split('T')[1].slice(0, 5)}</div>
                    <div style={{
                      fontSize: '12px',
                      color: theme === 'dark' ? '#94a3b8' : '#64748b',
                      fontWeight: '500'
                    }}>{flight.destination}</div>
                  </div>
                </div>

                {/* Multi-leg flight details */}
                {flight.segments && flight.segments.length > 0 && (
                  <div style={{
                    marginTop: '12px',
                    padding: '12px',
                    backgroundColor: theme === 'dark' ? '#0f172a' : '#f8fafc',
                    borderRadius: '8px',
                    fontSize: '11px'
                  }}>
                    <div style={{
                      fontWeight: '600',
                      marginBottom: '8px',
                      color: theme === 'dark' ? '#cbd5e1' : '#475569'
                    }}>✈️ Flight Segments:</div>
                    {flight.segments.map((segment: any, idx: number) => (
                      <div key={idx} style={{ marginBottom: '6px' }}>
                        <div style={{ color: theme === 'dark' ? '#94a3b8' : '#64748b' }}>
                          {idx + 1}. {segment.origin} → {segment.destination} • {segment.airline} {segment.flight_number}
                          <span style={{ marginLeft: '8px', color: theme === 'dark' ? '#64748b' : '#94a3b8' }}>
                            ({Math.floor(segment.duration_minutes / 60)}h {segment.duration_minutes % 60}m)
                          </span>
                        </div>
                        {idx < (flight.segments?.length || 0) - 1 && flight.layovers?.[idx] && (
                          <div style={{
                            marginLeft: '12px',
                            marginTop: '4px',
                            color: '#f59e0b',
                            fontSize: '10px'
                          }}>
                            ⏱️ Layover in {flight.layovers[idx].city}: {flight.layovers[idx].duration_minutes} min
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                  <button style={{
                    padding: '10px',
                    backgroundColor: theme === 'dark' ? '#334155' : '#f8fafc',
                    border: `1px solid ${theme === 'dark' ? '#475569' : '#e2e8f0'}`,
                    borderRadius: '8px',
                    color: theme === 'dark' ? '#cbd5e1' : '#475569',
                    fontSize: '13px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                    onClick={() => onSelectFlight?.(flight)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = theme === 'dark' ? '#475569' : '#f1f5f9';
                      e.currentTarget.style.color = theme === 'dark' ? '#f1f5f9' : '#0f172a';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = theme === 'dark' ? '#334155' : '#f8fafc';
                      e.currentTarget.style.color = theme === 'dark' ? '#cbd5e1' : '#475569';
                    }}
                  >
                    Select
                  </button>
                  <button style={{
                    padding: '10px',
                    backgroundColor: '#16a34a',
                    border: 'none',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '13px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                    onClick={() => onBookFlight?.(flight)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#15803d';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = '#16a34a';
                    }}
                  >
                    Book Now
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hotel Results */}
      {hotelResults.length > 0 && (
        <div style={{
          alignSelf: 'flex-start',
          width: '100%',
          paddingLeft: '48px',
          marginTop: '8px',
          animation: 'fadeIn 0.5s ease-out 0.2s backwards'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '16px',
            color: '#64748b',
            fontSize: '13px',
            fontWeight: '600',
            letterSpacing: '0.5px'
          }}>
            <span>🏨</span> HOTEL OPTIONS
            {hotelResults[0].is_partial && (
              <span style={{
                backgroundColor: '#fef3c7',
                color: '#d97706',
                padding: '2px 8px',
                borderRadius: '10px',
                fontSize: '10px'
              }}>PARTIAL RESULTS</span>
            )}
          </div>

          {/* Hotel Map */}
          <HotelMap hotels={hotelResults} />

          {/* Price Chart */}
          <PriceChart data={hotelResults.slice(0, 5)} type="hotel" />

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: '16px',
            marginTop: '20px',
            opacity: status === 'cancelled' ? 0.7 : 1,
            filter: status === 'cancelled' ? 'grayscale(100%)' : 'none',
            transition: 'all 0.3s ease'
          }}>
            {hotelResults.slice(0, 4).map((hotel, idx) => (
              <div
                key={idx}
                style={{
                  borderRadius: '16px',
                  backgroundColor: theme === 'dark' ? '#1e293b' : 'white',
                  boxShadow: theme === 'dark'
                    ? '0 4px 6px -1px rgba(0, 0, 0, 0.3)'
                    : '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
                  border: `1px solid ${theme === 'dark' ? '#334155' : '#f1f5f9'}`,
                  overflow: 'hidden',
                  cursor: 'pointer',
                  transition: 'transform 0.2s',
                  position: 'relative'
                }}
                className="slide-in"
                onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
              >
                {hotel.is_partial && (
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    right: 0,
                    backgroundColor: '#fffbeb',
                    color: '#b45309',
                    fontSize: '10px',
                    padding: '4px 8px',
                    borderBottomLeftRadius: '8px',
                    fontWeight: '600',
                    zIndex: 2
                  }}>PARTIAL</div>
                )}

                {/* Image */}
                <div style={{
                  height: '150px',
                  backgroundColor: '#cbd5e1',
                  position: 'relative',
                  overflow: 'hidden'
                }}>
                  <img
                    src={hotel.image_url || hotel.images?.[0] || `https://source.unsplash.com/random/400x300/?hotel,${hotel.city}`}
                    alt={hotel.name}
                    style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                    onError={(e) => {
                      // Fallback if image fails
                      e.currentTarget.src = 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80';
                    }}
                  />
                  <div style={{
                    position: 'absolute',
                    bottom: '8px',
                    left: '8px',
                    backgroundColor: 'rgba(0,0,0,0.6)',
                    color: 'white',
                    padding: '4px 8px',
                    borderRadius: '6px',
                    fontSize: '12px',
                    fontWeight: '600'
                  }}>
                    ⭐ {hotel.star_rating}
                  </div>
                </div>

                <div style={{ padding: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <div style={{
                      fontWeight: '700',
                      color: theme === 'dark' ? '#f1f5f9' : '#0f172a',
                      fontSize: '15px',
                      lineHeight: '1.4'
                    }}>{hotel.name}</div>
                    <div style={{ fontWeight: '700', color: '#16a34a', fontSize: '16px' }}>${hotel.price_per_night}</div>
                  </div>

                  <div style={{
                    fontSize: '13px',
                    color: theme === 'dark' ? '#94a3b8' : '#64748b',
                    marginBottom: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}>
                    <span>📍 {hotel.city}</span>
                    <span>•</span>
                    <span style={{
                      color: theme === 'dark' ? '#cbd5e1' : '#0f172a',
                      fontWeight: '600'
                    }}>{hotel.review_score}/10</span>
                    <span style={{ fontSize: '11px' }}>({hotel.review_count} reviews)</span>
                  </div>

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {hotel.amenities.slice(0, 3).map((amenity, i) => (
                      <span key={i} style={{
                        fontSize: '11px',
                        backgroundColor: theme === 'dark' ? '#334155' : '#f1f5f9',
                        padding: '4px 8px',
                        borderRadius: '6px',
                        color: theme === 'dark' ? '#cbd5e1' : '#475569',
                        fontWeight: '500'
                      }}>
                        {amenity}
                      </span>
                    ))}
                  </div>

                  <button style={{
                    width: '100%',
                    marginTop: '12px',
                    padding: '10px',
                    backgroundColor: '#16a34a',
                    border: 'none',
                    borderRadius: '8px',
                    color: 'white',
                    fontSize: '13px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                    onClick={() => onBookHotel?.(hotel)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#15803d';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = '#16a34a';
                    }}
                  >
                    Book Now
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
