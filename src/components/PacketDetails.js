import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import './PacketDetails.css';

const PacketDetails = () => {
    const { packetId } = useParams();
    const [packet, setPacket] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchPacketDetails = async () => {
            try {
                const response = await axios.get(`http://localhost:5000/api/packet/${packetId}`);
                setPacket(response.data);
            } catch (error) {
                setError("Failed to fetch packet details.");
                console.error("Error fetching packet details", error);
            }
        };

        fetchPacketDetails();
    }, [packetId]);

    if (error) {
        return <div className="error-message">{error}</div>;
    }

    if (!packet) {
        return <div>Loading...</div>;
    }

    return (
        <div className="packet-details">
            <h2>Packet Details</h2>
            <p><strong>ID:</strong> {packet._id}</p>
            <p><strong>Timestamp:</strong> {new Date(packet.timestamp * 1000).toLocaleString()}</p>
            <p><strong>Source IP:</strong> {packet.src_ip}</p>
            <p><strong>Destination IP:</strong> {packet.dst_ip}</p>
            <p><strong>Protocol:</strong> {packet.protocol_name}</p>
            <p><strong>Length:</strong> {packet.length}</p>
            <p><strong>Raw Data:</strong> {packet.raw_data}</p>
            {packet.src_port && <p><strong>Source Port:</strong> {packet.src_port}</p>}
            {packet.dst_port && <p><strong>Destination Port:</strong> {packet.dst_port}</p>}
        </div>
    );
};

export default PacketDetails;
