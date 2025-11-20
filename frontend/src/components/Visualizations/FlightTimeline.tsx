import React from 'react';
import type { FlightResult } from '../../types';

interface FlightTimelineProps {
    flights: FlightResult[];
}

export const FlightTimeline: React.FC<FlightTimelineProps> = ({ flights }) => {
    if (!flights || flights.length === 0) return null;

    const sortedFlights = [...flights].sort((a, b) =>
        new Date(a.departure_time).getTime() - new Date(b.departure_time).getTime()
    );

    // Assume flights are on the same day for simplicity of this view, or base it on the first flight's day
    const baseDate = new Date(sortedFlights[0].departure_time);
    const startTime = new Date(baseDate).setHours(4, 0, 0, 0); // Start at 4 AM
    const endTime = new Date(baseDate).setHours(28, 0, 0, 0); // End at 4 AM next day (24h window)
    const totalMs = endTime - startTime;

    return (
        <div style={{ marginTop: '20px', padding: '20px', backgroundColor: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
            <h4 style={{ margin: '0 0 20px 0', fontSize: '14px', color: '#64748b', fontWeight: '600' }}>Flight Schedule Timeline</h4>

            <div style={{ position: 'relative', height: '20px', marginBottom: '10px', borderBottom: '1px solid #cbd5e1' }}>
                {[6, 12, 18, 24].map(hour => (
                    <div key={hour} style={{
                        position: 'absolute',
                        left: `${((hour - 4) / 24) * 100}%`,
                        transform: 'translateX(-50%)',
                        fontSize: '10px',
                        color: '#94a3b8'
                    }}>
                        {hour > 23 ? '00:00' : `${hour}:00`}
                    </div>
                ))}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {sortedFlights.slice(0, 5).map((flight, idx) => {
                    const dep = new Date(flight.departure_time);
                    const arr = new Date(flight.arrival_time);

                    // Calculate position and width
                    let startPct = ((dep.getTime() - startTime) / totalMs) * 100;
                    let widthPct = ((arr.getTime() - dep.getTime()) / totalMs) * 100;

                    // Clamp values
                    if (startPct < 0) startPct = 0;
                    if (startPct + widthPct > 100) widthPct = 100 - startPct;

                    return (
                        <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '12px' }}>
                            <div style={{ width: '30px', fontWeight: '600', color: '#64748b' }}>{flight.airline.substring(0, 2).toUpperCase()}</div>
                            <div style={{ flex: 1, position: 'relative', height: '30px', backgroundColor: '#e2e8f0', borderRadius: '6px', overflow: 'hidden' }}>
                                {/* Flight Bar */}
                                <div style={{
                                    position: 'absolute',
                                    left: `${startPct}%`,
                                    width: `${widthPct}%`,
                                    height: '100%',
                                    backgroundColor: idx % 2 === 0 ? '#3b82f6' : '#60a5fa',
                                    borderRadius: '4px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: 'white',
                                    fontSize: '10px',
                                    whiteSpace: 'nowrap',
                                    overflow: 'hidden',
                                    boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
                                }}>
                                    {dep.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - {arr.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};
