import React, { useEffect, useState } from 'react';

const ThreatIntelligence = () => {
    const [threatData, setThreatData] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchThreatIntelligence = async () => {
        try {
            const response = await fetch('http://localhost:5000/api/packets');
            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            setThreatData(data);
        } catch (error) {
            console.error('Error fetching threat intelligence:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchThreatIntelligence();
        const interval = setInterval(fetchThreatIntelligence, 3000); // Update every 3 seconds

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="threat-intelligence">
            <h2>Threat Intelligence</h2>
            {loading ? (
                <div>Loading...</div>
            ) : (
                <table>
                    <thead>
                        <tr>
                            <th>Source IP</th>
                            <th>Destination IP</th>
                            <th>Source Malicious</th>
                            <th>Destination Malicious</th>    
                        </tr>
                    </thead>
                    <tbody>
                        {threatData.length > 0 ? (
                            threatData.map((entry, index) => (
                                <tr key={index}>
                                    <td>{entry.src_ip}</td>
                                    <td>{entry.dst_ip}</td>
                                    <td style={{ color: entry.src_is_malicious ? 'red' : 'green' }}>
                                        {entry.src_is_malicious ? 'Malicious' : 'Safe'}
                                    </td>
                                    <td style={{ color: entry.dst_is_malicious ? 'red' : 'green' }}>
                                        {entry.dst_is_malicious ? 'Malicious' : 'Safe'}
                                    </td>
                                    
                                </tr>
                            ))
                        ) : (
                            <tr>
                                <td colSpan="6">No threat intelligence data available.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default ThreatIntelligence;
