import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { HotelResult } from '../../types';

// Fix for default marker icon
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

interface HotelMapProps {
    hotels: HotelResult[];
}

function ChangeView({ bounds }: { bounds: L.LatLngBoundsExpression }) {
    const map = useMap();
    useEffect(() => {
        if (bounds) {
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    }, [bounds, map]);
    return null;
}

export const HotelMap: React.FC<HotelMapProps> = ({ hotels }) => {
    const validHotels = hotels.filter(h => h.coordinates && h.coordinates.length === 2);

    if (validHotels.length === 0) return null;

    const bounds = L.latLngBounds(validHotels.map(h => h.coordinates as [number, number]));

    return (
        <div style={{ height: '300px', width: '100%', borderRadius: '12px', overflow: 'hidden', margin: '10px 0', border: '1px solid #e2e8f0' }}>
            <MapContainer
                center={validHotels[0].coordinates as [number, number]}
                zoom={13}
                style={{ height: '100%', width: '100%' }}
                scrollWheelZoom={false}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                />
                {validHotels.map((hotel, idx) => (
                    <Marker key={`${hotel.name}-${idx}`} position={hotel.coordinates as [number, number]}>
                        <Popup>
                            <div style={{ width: '200px' }}>
                                <h3 style={{ margin: '0 0 5px 0', fontSize: '14px' }}>{hotel.name}</h3>
                                {(hotel.image_url || (hotel.images && hotel.images.length > 0)) && (
                                    <img
                                        src={hotel.image_url || hotel.images?.[0]}
                                        alt={hotel.name}
                                        style={{ width: '100%', height: '100px', objectFit: 'cover', borderRadius: '4px', marginBottom: '5px' }}
                                    />
                                )}
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ fontSize: '12px', color: '#64748b' }}>{hotel.star_rating}★</span>
                                    <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#0f172a' }}>${hotel.price_per_night}</span>
                                </div>
                            </div>
                        </Popup>
                    </Marker>
                ))}
                <ChangeView bounds={bounds} />
            </MapContainer>
        </div>
    );
};
