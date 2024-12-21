import React from 'react';
import Globe from './Globe';

const Visualizer = () => {
    return (
        <div>
            <h1 style={{ textAlign: 'center', color: 'cyan' }}>Real-Time Packet Visualization</h1>
            <Globe />
        </div>
    );
};

export default Visualizer;
