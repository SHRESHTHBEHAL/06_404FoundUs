import { useState, useRef, useEffect, type FormEvent } from 'react';
import { useTheme } from '../contexts/ThemeContext';

interface SmartInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

// Popular cities and airports for autocomplete
const POPULAR_DESTINATIONS = [
  { code: 'NYC', name: 'New York', country: 'USA' },
  { code: 'LAX', name: 'Los Angeles', country: 'USA' },
  { code: 'LHR', name: 'London', country: 'UK' },
  { code: 'CDG', name: 'Paris', country: 'France' },
  { code: 'NRT', name: 'Tokyo', country: 'Japan' },
  { code: 'DXB', name: 'Dubai', country: 'UAE' },
  { code: 'SIN', name: 'Singapore', country: 'Singapore' },
  { code: 'HKG', name: 'Hong Kong', country: 'China' },
  { code: 'SYD', name: 'Sydney', country: 'Australia' },
  { code: 'BKK', name: 'Bangkok', country: 'Thailand' },
  { code: 'IST', name: 'Istanbul', country: 'Turkey' },
  { code: 'FCO', name: 'Rome', country: 'Italy' },
  { code: 'BCN', name: 'Barcelona', country: 'Spain' },
  { code: 'AMS', name: 'Amsterdam', country: 'Netherlands' },
  { code: 'FRA', name: 'Frankfurt', country: 'Germany' },
  { code: 'MIA', name: 'Miami', country: 'USA' },
  { code: 'SFO', name: 'San Francisco', country: 'USA' },
  { code: 'ORD', name: 'Chicago', country: 'USA' },
];

// Quick action suggestions
const QUICK_ACTIONS = [
  { icon: '💰', text: 'Cheap flights to Paris', emoji: '✈️' },
  { icon: '🏨', text: 'Hotels in Tokyo', emoji: '🗼' },
  { icon: '🏖️', text: 'Beach resorts in Miami', emoji: '🌴' },
  { icon: '🗽', text: 'Weekend in New York', emoji: '🌆' },
  { icon: '✈️', text: 'Round trip to London', emoji: '🇬🇧' },
];

export function SmartInput({ onSend, disabled }: SmartInputProps) {
  const [input, setInput] = useState('');
  const [suggestions, setSuggestions] = useState<typeof POPULAR_DESTINATIONS>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const { theme } = useTheme();

  // Voice Input Logic (Server-Side Transcription)
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

        // Stop all tracks immediately
        stream.getTracks().forEach(track => track.stop());

        // Reset listening state immediately so UI updates
        setIsListening(false);
        setIsProcessing(true);

        try {
          const formData = new FormData();
          formData.append('file', audioBlob, 'recording.webm');

          const response = await fetch('http://127.0.0.1:8000/transcribe', {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) throw new Error('Transcription failed');

          const data = await response.json();
          if (data.text) {
            setInput(data.text);
            // Auto-submit if it's a clear command? Maybe not, let user review.
          }
        } catch (error) {
          console.error('Error transcribing audio:', error);
          alert('Failed to transcribe audio. Please try again.');
        } finally {
          setIsProcessing(false);
        }
      };

      mediaRecorder.start();
      setIsListening(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isListening) {
      mediaRecorderRef.current.stop();
      // isListening set to false in onstop
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const handleInputChange = (value: string) => {
    setInput(value);

    // Auto-complete logic
    if (value.length >= 2) {
      const filtered = POPULAR_DESTINATIONS.filter(dest =>
        dest.name.toLowerCase().includes(value.toLowerCase()) ||
        dest.code.toLowerCase().includes(value.toLowerCase()) ||
        dest.country.toLowerCase().includes(value.toLowerCase())
      ).slice(0, 5);

      setSuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
      setSelectedIndex(-1);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (destination: typeof POPULAR_DESTINATIONS[0]) => {
    // Smart insertion - if input has "to" or "in", append the city name
    const lowerInput = input.toLowerCase();
    let newInput = '';

    if (lowerInput.includes(' to ') || lowerInput.includes(' in ')) {
      // Replace the partial word with the full destination
      const words = input.split(' ');
      words[words.length - 1] = destination.name;
      newInput = words.join(' ');
    } else if (lowerInput.startsWith('hotel') || lowerInput.startsWith('flight')) {
      newInput = `${input.trim()} to ${destination.name}`;
    } else {
      newInput = `Flights to ${destination.name}`;
    }

    setInput(newInput);
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  const handleQuickAction = (text: string) => {
    setInput(text);
    setShowSuggestions(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestions) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, suggestions.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, -1));
    } else if (e.key === 'Enter' && selectedIndex >= 0) {
      e.preventDefault();
      handleSuggestionClick(suggestions[selectedIndex]);
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  // Click outside to close suggestions
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (inputRef.current && !inputRef.current.contains(e.target as Node)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div style={{
      padding: '20px 30px',
      backgroundColor: theme === 'dark' ? 'rgba(30, 41, 59, 0.95)' : 'white',
      borderTop: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)'}`,
      transition: 'all 0.3s ease'
    }}>
      {/* Quick Actions */}
      {input.length === 0 && (
        <div style={{
          display: 'flex',
          gap: '8px',
          marginBottom: '12px',
          overflowX: 'auto',
          paddingBottom: '4px'
        }}>
          {QUICK_ACTIONS.map((action, idx) => (
            <button
              key={idx}
              onClick={() => handleQuickAction(action.text)}
              style={{
                padding: '6px 12px',
                borderRadius: '16px',
                border: `1px solid ${theme === 'dark' ? '#475569' : '#e2e8f0'}`,
                backgroundColor: theme === 'dark' ? '#334155' : '#f8fafc',
                color: theme === 'dark' ? '#cbd5e1' : '#475569',
                fontSize: '13px',
                fontWeight: '500',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
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
              <span>{action.icon}</span>
              <span>{action.text}</span>
            </button>
          ))}
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} style={{ position: 'relative' }}>
        <div style={{ display: 'flex', gap: '12px', position: 'relative' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => handleInputChange(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isListening ? "Listening..." : (isProcessing ? "Processing audio..." : "Ask about flights, hotels, or travel plans...")}
              disabled={disabled || isProcessing}
              style={{
                width: '100%',
                padding: '14px 20px',
                paddingRight: '50px', // Make room for mic button
                border: `2px solid ${isListening ? '#ef4444' : (theme === 'dark' ? '#334155' : '#f1f5f9')}`,
                borderRadius: '24px',
                fontSize: '15px',
                outline: 'none',
                transition: 'all 0.2s',
                backgroundColor: theme === 'dark' ? '#1e293b' : '#f8fafc',
                color: theme === 'dark' ? '#f1f5f9' : '#1e293b'
              }}
              onFocus={(e) => {
                if (!isListening) {
                  e.target.style.borderColor = '#3b82f6';
                  e.target.style.backgroundColor = theme === 'dark' ? '#0f172a' : 'white';
                  e.target.style.boxShadow = '0 0 0 4px rgba(59, 130, 246, 0.1)';
                }
              }}
              onBlur={(e) => {
                if (!isListening) {
                  e.target.style.borderColor = theme === 'dark' ? '#334155' : '#f1f5f9';
                  e.target.style.backgroundColor = theme === 'dark' ? '#1e293b' : '#f8fafc';
                  e.target.style.boxShadow = 'none';
                }
              }}
            />

            {/* Microphone Button inside Input */}
            <button
              type="button"
              onClick={toggleListening}
              style={{
                position: 'absolute',
                right: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: isListening ? '#ef4444' : (theme === 'dark' ? '#94a3b8' : '#64748b'),
                padding: '8px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.2s'
              }}
              title="Voice Input"
            >
              {isListening ? (
                <div style={{
                  width: '12px',
                  height: '12px',
                  backgroundColor: '#ef4444',
                  borderRadius: '2px',
                  animation: 'pulse 1s infinite'
                }} />
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                  <line x1="12" y1="19" x2="12" y2="23"></line>
                  <line x1="8" y1="23" x2="16" y2="23"></line>
                </svg>
              )}
            </button>

            {/* Auto-complete Suggestions */}
            {showSuggestions && suggestions.length > 0 && (
              <div style={{
                position: 'absolute',
                bottom: '100%',
                left: 0,
                right: 0,
                marginBottom: '8px',
                backgroundColor: theme === 'dark' ? '#1e293b' : 'white',
                borderRadius: '12px',
                boxShadow: theme === 'dark'
                  ? '0 -8px 32px rgba(0,0,0,0.5)'
                  : '0 -8px 32px rgba(0,0,0,0.1)',
                border: `1px solid ${theme === 'dark' ? '#334155' : '#e2e8f0'}`,
                overflow: 'hidden',
                zIndex: 100,
                animation: 'slideInUp 0.2s ease-out'
              }}>
                {suggestions.map((dest, idx) => (
                  <div
                    key={dest.code}
                    onClick={() => handleSuggestionClick(dest)}
                    style={{
                      padding: '12px 16px',
                      cursor: 'pointer',
                      backgroundColor: selectedIndex === idx
                        ? (theme === 'dark' ? '#334155' : '#f1f5f9')
                        : 'transparent',
                      transition: 'background-color 0.15s',
                      borderBottom: idx < suggestions.length - 1
                        ? `1px solid ${theme === 'dark' ? '#334155' : '#f1f5f9'}`
                        : 'none'
                    }}
                    onMouseEnter={(e) => {
                      if (selectedIndex !== idx) {
                        e.currentTarget.style.backgroundColor = theme === 'dark' ? '#334155' : '#f1f5f9';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (selectedIndex !== idx) {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{
                          fontWeight: '600',
                          color: theme === 'dark' ? '#f1f5f9' : '#0f172a',
                          fontSize: '14px'
                        }}>
                          ✈️ {dest.name}
                        </div>
                        <div style={{
                          fontSize: '12px',
                          color: theme === 'dark' ? '#94a3b8' : '#64748b',
                          marginTop: '2px'
                        }}>
                          {dest.country}
                        </div>
                      </div>
                      <div style={{
                        fontSize: '12px',
                        fontWeight: '600',
                        color: theme === 'dark' ? '#64748b' : '#94a3b8',
                        fontFamily: 'monospace'
                      }}>
                        {dest.code}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={disabled || !input.trim()}
            style={{
              width: '50px',
              height: '50px',
              borderRadius: '50%',
              backgroundColor: disabled || !input.trim() ? (theme === 'dark' ? '#334155' : '#e2e8f0') : '#3b82f6',
              color: 'white',
              border: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: disabled || !input.trim() ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s',
              boxShadow: disabled || !input.trim() ? 'none' : '0 4px 6px -1px rgba(59, 130, 246, 0.5)',
              transform: disabled || !input.trim() ? 'scale(0.95)' : 'scale(1)'
            }}
            onMouseEnter={(e) => {
              if (!disabled && input.trim()) {
                e.currentTarget.style.transform = 'scale(1.05)';
                e.currentTarget.style.backgroundColor = '#2563eb';
              }
            }}
            onMouseLeave={(e) => {
              if (!disabled && input.trim()) {
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.backgroundColor = '#3b82f6';
              }
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </form>

      <style>{`
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
}
