import { useEffect, useState } from 'react';
import axios from 'axios';
import type { PreferencesResponse, PreferenceItem } from '../types';

interface PreferencesPanelProps {
  sessionId: string;
  isOpen: boolean;
  onClose: () => void;
}

export function PreferencesPanel({ sessionId, isOpen, onClose }: PreferencesPanelProps) {
  const [preferences, setPreferences] = useState<PreferencesResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchPreferences();
    }
  }, [isOpen, sessionId]);

  const fetchPreferences = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://127.0.0.1:8000/chat/${sessionId}/preferences`);
      setPreferences(response.data);
    } catch (error) {
      console.error('Failed to fetch preferences:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClearPreferences = async () => {
    try {
      await axios.delete(`http://127.0.0.1:8000/chat/${sessionId}/preferences`);
      fetchPreferences(); // Refresh
    } catch (error) {
      console.error('Failed to clear preferences:', error);
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'flight_time': return '🌅';
      case 'cabin_class': return '💼';
      case 'airline': return '✈️';
      case 'max_stops': return '🔄';
      case 'min_hotel_rating': return '⭐';
      case 'hotel_budget': return '💰';
      case 'amenity': return '🏊';
      default: return '📌';
    }
  };

  const formatCategory = (category: string) => {
    return category.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.3)',
          backdropFilter: 'blur(2px)',
          zIndex: 999,
          animation: 'fadeIn 0.2s ease-out'
        }}
        onClick={onClose}
      />

      {/* Panel */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          right: 0,
          bottom: 0,
          width: '400px',
          maxWidth: '90vw',
          backgroundColor: 'white',
          boxShadow: '-4px 0 20px rgba(0, 0, 0, 0.15)',
          zIndex: 1000,
          display: 'flex',
          flexDirection: 'column',
          animation: 'slideInRight 0.3s ease-out'
        }}
      >
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid #e2e8f0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#f8fafc'
        }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#1e293b' }}>
              Your Preferences
            </h2>
            <p style={{ margin: '4px 0 0', fontSize: '13px', color: '#64748b' }}>
              Learned from your conversations
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              border: 'none',
              backgroundColor: '#e2e8f0',
              color: '#475569',
              fontSize: '18px',
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#cbd5e1'}
            onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#e2e8f0'}
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px 0', color: '#94a3b8' }}>
              Loading preferences...
            </div>
          ) : !preferences || preferences.preference_items.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              padding: '40px 20px',
              color: '#94a3b8'
            }}>
              <div style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.5 }}>🎯</div>
              <p style={{ fontSize: '14px', margin: 0 }}>
                No preferences learned yet.<br />
                Try saying "I prefer morning flights" or "I like 4-star hotels"
              </p>
            </div>
          ) : (
            <>
              {/* Summary */}
              {preferences.summary && preferences.summary !== "No preferences learned yet" && (
                <div style={{
                  padding: '16px',
                  backgroundColor: '#eff6ff',
                  borderRadius: '12px',
                  marginBottom: '24px',
                  border: '1px solid #dbeafe'
                }}>
                  <div style={{ 
                    fontSize: '13px', 
                    color: '#1e40af',
                    lineHeight: '1.6'
                  }}>
                    {preferences.summary}
                  </div>
                </div>
              )}

              {/* Preference Items */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {preferences.preference_items.map((item: PreferenceItem, index: number) => (
                  <div
                    key={index}
                    style={{
                      padding: '14px 16px',
                      backgroundColor: '#f8fafc',
                      borderRadius: '10px',
                      border: '1px solid #e2e8f0',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#f1f5f9';
                      e.currentTarget.style.borderColor = '#cbd5e1';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = '#f8fafc';
                      e.currentTarget.style.borderColor = '#e2e8f0';
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                      <span style={{ fontSize: '20px' }}>{getCategoryIcon(item.category)}</span>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: '13px', fontWeight: '600', color: '#334155' }}>
                          {formatCategory(item.category)}
                        </div>
                        <div style={{ fontSize: '15px', color: '#0f172a', fontWeight: '500' }}>
                          {item.value}
                        </div>
                      </div>
                      <div style={{
                        fontSize: '11px',
                        color: '#64748b',
                        backgroundColor: 'white',
                        padding: '4px 8px',
                        borderRadius: '6px',
                        fontWeight: '600'
                      }}>
                        {Math.round(item.confidence * 100)}%
                      </div>
                    </div>
                    {item.source_message && (
                      <div style={{
                        fontSize: '12px',
                        color: '#64748b',
                        marginTop: '6px',
                        fontStyle: 'italic',
                        paddingLeft: '30px'
                      }}>
                        "{item.source_message}"
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        {preferences && preferences.preference_items.length > 0 && (
          <div style={{
            padding: '16px 24px',
            borderTop: '1px solid #e2e8f0',
            backgroundColor: '#f8fafc'
          }}>
            <button
              onClick={handleClearPreferences}
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: '#fef2f2',
                border: '1px solid #fecaca',
                borderRadius: '8px',
                color: '#dc2626',
                fontSize: '14px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#fee2e2';
                e.currentTarget.style.borderColor = '#fca5a5';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = '#fef2f2';
                e.currentTarget.style.borderColor = '#fecaca';
              }}
            >
              Clear All Preferences
            </button>
          </div>
        )}
      </div>

      {/* Animations */}
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideInRight {
          from { transform: translateX(100%); }
          to { transform: translateX(0); }
        }
      `}</style>
    </>
  );
}
