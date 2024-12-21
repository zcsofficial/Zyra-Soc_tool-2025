// src/api.js
export const fetchSystemInfo = async () => {
    try {
        const response = await fetch('http://localhost:5000/api/system_info');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching system info:', error);
        return null;
    }
};

export const fetchTopIps = async () => {
    try {
        const response = await fetch('http://localhost:5000/api/top_ips');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching top IPs:', error);
        return [];
    }
};

// src/api.js
export const fetchPacketDetails = async (packetId) => {
    try {
        const response = await fetch(`http://localhost:5000/api/packet/${packetId}`);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching packet details:', error);
        return null;
    }
};

export const fetchNetworkPackets = async () => {
    try {
        const response = await fetch('http://localhost:5000/api/packets');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching network packets:', error);
        return null;
    }
};

