import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './PacketAnalysis.css';

const PacketAnalysis = () => {
    const [packets, setPackets] = useState([]);
    const [selectedPacket, setSelectedPacket] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPackets = async () => {
            try {
                const response = await axios.get('http://localhost:5000/api/packets');
                setPackets(response.data);
                setLoading(false);
            } catch (error) {
                setError('Failed to fetch packets.');
                setLoading(false);
            }
        };

        fetchPackets();
    }, []);

    const fetchPacketDetails = async (packetId) => {
        try {
            const response = await axios.get(`http://localhost:5000/api/packet/${packetId}`);
            setSelectedPacket(response.data);
        } catch (error) {
            setError('Failed to fetch packet details.');
        }
    };

    return (
        <div className="packet-analysis">
            <h2>Deep Packet Analysis</h2>
            {loading ? (
                <p>Loading...</p>
            ) : error ? (
                <div className="error-message">{error}</div>
            ) : (
                <div className="packet-container">
                    <div className="packet-list">
                        <h3>Packets</h3>
                        <ul>
                            {packets.map((packet) => (
                                <li key={packet._id} onClick={() => fetchPacketDetails(packet._id)}>
                                    {packet.src_ip} -> {packet.dst_ip} ({new Date(packet.timestamp * 1000).toLocaleString()})
                                </li>
                            ))}
                        </ul>
                    </div>
                    <div className="packet-details">
                        {selectedPacket ? (
                            <>
                                <h3>Packet Details</h3>
                                <pre>{JSON.stringify(selectedPacket, null, 2)}</pre>
                            </>
                        ) : (
                            <p>Select a packet to see details</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default PacketAnalysis;
