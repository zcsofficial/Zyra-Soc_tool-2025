import React from 'react';
import './Alert.css'; // Create a CSS file for alert styling

const Alert = ({ message }) => {
    return (
        <div className="alert">
            <p>{message}</p>
        </div>
    );
};

export default Alert;
