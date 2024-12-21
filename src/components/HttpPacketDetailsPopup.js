// src/components/HttpPacketDetailsPopup.js

import React from 'react';
import './HttpPacketDetailsPopup.css';

const HttpPacketDetailsPopup = ({ packet, onClose }) => {
    return (
        <div className="popup-overlay">
            <div className="popup-box">
                <button className="close-btn" onClick={onClose}>✕</button>
                <h2>HTTP Packet Details</h2>
                <h3>Timestamp: {new Date(packet.timestamp * 1000).toLocaleString()}</h3>
                <h3>Source IP: {packet.src_ip}</h3>
                <h3>Destination IP: {packet.dst_ip}</h3>
                <h3>Request/Response: {packet.request_type}</h3>
                <h3>Raw Body:</h3>
                <pre>{packet.body ? JSON.stringify(packet.body, null, 2) : 'N/A'}</pre>
                <h3>Headers:</h3>
                <pre>{packet.headers ? JSON.stringify(packet.headers, null, 2) : 'N/A'}</pre>
            </div>
        </div>
    );
};

export default HttpPacketDetailsPopup;
