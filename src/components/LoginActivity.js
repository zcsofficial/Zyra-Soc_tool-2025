import React, { useState, useEffect } from 'react';
import LoadingSpinner from './LoadingSpinner'; // Adjust the path as necessary

const LoginActivity = () => {
    const [loginActivities, setLoginActivities] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchLoginActivities = async () => {
            try {
                const response = await fetch('http://localhost:50000/api/login_activity');
                if (!response.ok) throw new Error('Network response was not ok');
                const data = await response.json();
                setLoginActivities(data);
            } catch (error) {
                setError('Failed to fetch login activity data.');
                console.error('Error fetching login activity:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchLoginActivities();
        const interval = setInterval(fetchLoginActivities, 30000); // Refresh every 30 seconds

        return () => clearInterval(interval);
    }, []);

    if (loading) return <LoadingSpinner />;
    if (error) return <div className="error-message">{error}</div>;

    return (
        <div className="login-activity">
            <h2>Login Activity</h2>
            <table>
                <thead>
                    <tr>
                        <th>IP Address</th>
                        <th>Event</th>
                        <th>Count</th>
                        <th>Timestamps</th>
                        <th>Detected At</th>
                    </tr>
                </thead>
                <tbody>
                    {loginActivities.map((activity, index) => (
                        <tr key={index}>
                            <td>{activity.ip}</td>
                            <td>{activity.event}</td>
                            <td>{activity.count}</td>
                            <td>{activity.timestamps.join(', ')}</td>
                            <td>{new Date(activity.detected_at).toLocaleString()}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default LoginActivity;
