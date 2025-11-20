import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { FlightResult, HotelResult } from '../../types';

interface PriceChartProps {
    data: (FlightResult | HotelResult)[];
    type: 'flight' | 'hotel';
}

export const PriceChart: React.FC<PriceChartProps> = ({ data, type }) => {
    if (!data || data.length === 0) return null;

    const chartData = data.map((item) => ({
        name: type === 'flight'
            ? (item as FlightResult).airline
            : (item as HotelResult).name.split(' ').slice(0, 2).join(' '), // Shorten name
        price: type === 'flight'
            ? (item as FlightResult).price
            : (item as HotelResult).price_per_night,
        fullData: item
    }));

    return (
        <div style={{ height: '250px', width: '100%', marginTop: '20px', padding: '10px', backgroundColor: '#f8fafc', borderRadius: '12px' }}>
            <h4 style={{ margin: '0 0 15px 0', fontSize: '14px', color: '#64748b', fontWeight: '600' }}>Price Comparison</h4>
            <ResponsiveContainer width="100%" height="85%">
                <BarChart data={chartData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis
                        dataKey="name"
                        tick={{ fontSize: 10, fill: '#64748b' }}
                        interval={0}
                        tickLine={false}
                        axisLine={false}
                    />
                    <YAxis
                        tick={{ fontSize: 10, fill: '#64748b' }}
                        tickLine={false}
                        axisLine={false}
                        tickFormatter={(value) => `$${value}`}
                    />
                    <Tooltip
                        cursor={{ fill: '#f1f5f9' }}
                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                        formatter={(value: number) => [`$${value}`, 'Price']}
                    />
                    <Bar dataKey="price" radius={[4, 4, 0, 0]} barSize={40}>
                        {chartData.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#3b82f6' : '#60a5fa'} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};
