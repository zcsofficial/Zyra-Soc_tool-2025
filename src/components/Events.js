import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Events = () => {
    const [events, setEvents] = useState([]);
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchEvents = async () => {
            setLoading(true);
            try {
                const response = await axios.get('http://localhost:50000/api/events', {
                    params: {
                        page,
                        limit: 50,
                        search
                    }
                });
                setEvents(response.data.data);
                setTotalPages(response.data.totalPages);
            } catch (err) {
                setError('Failed to fetch events');
                console.error(err);
            }
            setLoading(false);
        };

        fetchEvents();
    }, [page, search]);

    const handleSearchChange = (e) => {
        setSearch(e.target.value);
        setPage(1); // Reset to first page when searching
    };

    const handlePageChange = (newPage) => {
        setPage(newPage);
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div>
            <h2>Events</h2>
            <input
                type="text"
                value={search}
                onChange={handleSearchChange}
                placeholder="Search..."
            />
            <table>
                <thead>
                    <tr>
                        <th>Type</th>
                        <th>PID</th>
                        <th>Process Name</th>
                        <th>User</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    {events.map((event) => (
                        <tr key={event._id}>
                            <td>{event.type}</td>
                            <td>{event.pid}</td>
                            <td>{event.process_name}</td>
                            <td>{event.user}</td>
                            <td>{event.description}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <div>
                {Array.from({ length: totalPages }, (_, i) => (
                    <button
                        key={i}
                        onClick={() => handlePageChange(i + 1)}
                        disabled={page === i + 1}
                    >
                        {i + 1}
                    </button>
                ))}
            </div>
        </div>
    );
};

export default Events;
