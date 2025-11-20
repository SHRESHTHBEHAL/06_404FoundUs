import { useState, type FormEvent } from 'react';
import { useTheme } from '../contexts/ThemeContext';

interface InputBoxProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function InputBox({ onSend, disabled }: InputBoxProps) {
  const [input, setInput] = useState('');
  const { theme } = useTheme();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        padding: '20px 30px',
        backgroundColor: theme === 'dark' ? 'rgba(30, 41, 59, 0.95)' : 'white',
        display: 'flex',
        gap: '12px',
        borderTop: `1px solid ${theme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)'}`,
        transition: 'all 0.3s ease'
      }}
    >
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask about flights, hotels, or travel plans..."
        disabled={disabled}
        style={{
          flex: 1,
          padding: '14px 20px',
          border: `2px solid ${theme === 'dark' ? '#334155' : '#f1f5f9'}`,
          borderRadius: '24px',
          fontSize: '15px',
          outline: 'none',
          transition: 'all 0.2s',
          backgroundColor: theme === 'dark' ? '#1e293b' : '#f8fafc',
          color: theme === 'dark' ? '#f1f5f9' : '#1e293b'
        }}
        onFocus={(e) => {
          e.target.style.borderColor = '#3b82f6';
          e.target.style.backgroundColor = theme === 'dark' ? '#0f172a' : 'white';
          e.target.style.boxShadow = '0 0 0 4px rgba(59, 130, 246, 0.1)';
        }}
        onBlur={(e) => {
          e.target.style.borderColor = theme === 'dark' ? '#334155' : '#f1f5f9';
          e.target.style.backgroundColor = theme === 'dark' ? '#1e293b' : '#f8fafc';
          e.target.style.boxShadow = 'none';
        }}
      />
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
    </form>
  );
}
