import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

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

interface FlightMapProps {
    origin: [number, number];
    destination: [number, number];
    originCode: string;
    destinationCode: string;
}

function ChangeView({ bounds }: { bounds: L.LatLngBoundsExpression }) {
    const map = useMap();
    useEffect(() => {
        map.fitBounds(bounds, { padding: [50, 50] });
    }, [bounds, map]);
    return null;
}

export const FlightMap: React.FC<FlightMapProps> = ({ origin, destination, originCode, destinationCode }) => {
    // Ensure valid coordinates
    if (!origin || !destination || origin.length !== 2 || destination.length !== 2) {
        return null;
    }

    const bounds = L.latLngBounds([origin, destination]);

    return (
        <div style={{ height: '250px', width: '100%', borderRadius: '12px', overflow: 'hidden', margin: '10px 0', border: '1px solid #e2e8f0' }}>
            <MapContainer
                center={[20, 0]}
                zoom={2}
                style={{ height: '100%', width: '100%' }}
                scrollWheelZoom={false}
                dragging={false} // Disable dragging for better UX in chat
                zoomControl={false} // Hide zoom controls
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
                />
                <Marker position={origin}>
                    <Popup>{originCode}</Popup>
                </Marker>
                <Marker position={destination}>
                    <Popup>{destinationCode}</Popup>
                </Marker>
                <Polyline
                    positions={[origin, destination]}
                    pathOptions={{ color: '#3b82f6', weight: 3, dashArray: '10, 10', opacity: 0.8 }}
                />
                <ChangeView bounds={bounds} />
            </MapContainer>
        </div>
    );
};
