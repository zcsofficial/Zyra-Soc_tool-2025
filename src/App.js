import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import './App.css';
import LoadingSpinner from './components/LoadingSpinner';
import Map from './components/Map';
import Alerts from './components/Alerts';
import Network from './components/Network';
import ExportData from './components/ExportData';
import ThreatIntelligence from './components/ThreatIntelligence';
import Events from './components/Events';
import LoginActivity from './components/LoginActivity';
import Files from './components/Files';
import Access from './components/Access';  // Import the Access component

const App = () => {
    const [loading, setLoading] = useState(true);
    const [systemInfo, setSystemInfo] = useState({ hostname: '', internal_ip: '' });
    const [topIps, setTopIps] = useState([]);
    const [error, setError] = useState(null);

    // State for additional data
    const [processCount, setProcessCount] = useState(null);
    const [loginCount, setLoginCount] = useState(null);

    useEffect(() => {
        const fetchSystemInfo = async () => {
            try {
                const response = await fetch('http://localhost:50000/api/system_info');
                if (!response.ok) throw new Error('Network response was not ok');
                const data = await response.json();
                setSystemInfo(data);
            } catch (error) {
                setError('Failed to fetch system information.');
            } finally {
                setLoading(false);
            }
        };

        fetchSystemInfo();
    }, []);

    useEffect(() => {
        const fetchTopIps = async () => {
            try {
                const response = await fetch('http://localhost:50000/api/top_ips');
                if (!response.ok) throw new Error('Network response was not ok');
                const data = await response.json();
                setTopIps(data);
            } catch (error) {
                console.error('Error fetching top IPs:', error);
            }
        };

        fetchTopIps();
        const interval = setInterval(fetchTopIps, 3000);

        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        const fetchAdditionalData = async () => {
            try {
                const [processResponse, loginResponse] = await Promise.all([
                    fetch('http://localhost:50000/api/process_count'),
                    fetch('http://localhost:50000/api/login_count'),
                ]);

                if (!processResponse.ok || !loginResponse.ok) throw new Error('Network response was not ok');

                const [processData, loginData] = await Promise.all([
                    processResponse.json(),
                    loginResponse.json(),
                ]);

                setProcessCount(processData.count);
                setLoginCount(loginData.count);
            } catch (error) {
                console.error('Error fetching additional data:', error);
            }
        };

        fetchAdditionalData();
        const interval = setInterval(fetchAdditionalData, 30000); // Refresh every 30 seconds

        return () => clearInterval(interval);
    }, []);

    const ipLocations = topIps.map(ipInfo => ({
        ip: ipInfo.ip,
        count: ipInfo.count,
        lat: ipInfo.latitude || 0, // Fallback to 0 if latitude is not available
        lon: ipInfo.longitude || 0, // Fallback to 0 if longitude is not available
    }));

    return (
        <Router>
            <div className="dashboard">
                <header className="dashboard-header">
                    <h1>SOC Dashboard</h1>
                </header>
                <div className="dashboard-navbar">
                    <nav>
                        <ul>
                            <li><Link to="/">Overview</Link></li>
                            <li><Link to="/alerts">Alerts</Link></li>
                            <li><Link to="/network">Network</Link></li>
                            <li><Link to="/export">Export Data</Link></li>
                            <li><Link to="/threat-intelligence">Threat Intelligence</Link></li>
                            <li><Link to="/events">Events</Link></li>
                            <li><Link to="/login-activity">Login Activity</Link></li>
                            <li><Link to="/files">Files</Link></li>
                            <li><Link to="/access">Access</Link></li>  {/* New Nav Item */}
                        </ul>
                    </nav>
                </div>
                <main className="dashboard-main">
                    <Routes>
                        <Route path="/" element={
                            <>
                                {loading ? (
                                    <LoadingSpinner />
                                ) : error ? (
                                    <div className="error-message">{error}</div>
                                ) : (
                                    <div className="system-info">
                                        <h2>System Information</h2>
                                        <p><strong>Hostname:</strong> {systemInfo.hostname}</p>
                                        <p><strong>Internal IP:</strong> {systemInfo.internal_ip}</p>
                                        <div className="additional-info">
                                            <p><strong>Number of Processes:</strong> {processCount !== null ? processCount : <LoadingSpinner />}</p>
                                            <p><strong>Login Attempts:</strong> {loginCount !== null ? loginCount : <LoadingSpinner />}</p>
                                        </div>
                                    </div>
                                )}
                                <div className="map-card">
                                    <h2>Top 10 IP Locations</h2>
                                    <Map locations={ipLocations} />
                                </div>
                                <div className="top-ips">
                                    <h2>Top 10 IP Addresses</h2>
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>IP Address</th>
                                                <th>Count</th>
                                                <th>City</th>
                                                <th>Region</th>
                                                <th>Country</th>
                                                <th>ISP</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {topIps.map((ipInfo, index) => (
                                                <tr key={index}>
                                                    <td>{ipInfo.ip}</td>
                                                    <td>{ipInfo.count}</td>
                                                    <td>{ipInfo.city}</td>
                                                    <td>{ipInfo.region}</td>
                                                    <td>{ipInfo.country}</td>
                                                    <td>{ipInfo.isp}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                                <div className="summary">
                                    <h2>Summary</h2>
                                    <p><strong>Total Processes:</strong> {processCount !== null ? processCount : <LoadingSpinner />}</p>
                                    <p><strong>Total Login Attempts:</strong> {loginCount !== null ? loginCount : <LoadingSpinner />}</p>
                                </div>
                            </>
                        } />
                        <Route path="/alerts" element={<Alerts />} />
                        <Route path="/network" element={<Network />} />
                        <Route path="/export" element={<ExportData />} />
                        <Route path="/threat-intelligence" element={<ThreatIntelligence />} />
                        <Route path="/events" element={<Events />} />
                        <Route path="/login-activity" element={<LoginActivity />} />
                        <Route path="/files" element={<Files />} />
                        <Route path="/access" element={<Access />} />  {/* New Route */}
                    </Routes>
                </main>
            </div>
        </Router>
    );
};

export default App;
