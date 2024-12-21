// src/components/PacketDetailsPopup.js

import React from 'react';
import './PacketDetailsPopup.css';

const PacketDetailsPopup = ({ packet, onClose }) => {
    return (
        <div className="popup-overlay">
            <div className="popup-box">
                <button className="close-btn" onClick={onClose}>✕</button>
                <h2>Packet Details</h2>
                <pre>{JSON.stringify(packet, null, 2)}</pre>
            </div>
        </div>
    );
};

export default PacketDetailsPopup;
