import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Files = () => {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    useEffect(() => {
        const fetchFiles = async () => {
            try {
                const response = await axios.get('http://localhost:50000/api/files', {
                    params: { page, limit: 50, search }
                });
                setFiles(response.data.data);
                setTotalPages(response.data.totalPages);
                setLoading(false);
            } catch (error) {
                setError('Failed to fetch files');
                setLoading(false);
            }
        };

        fetchFiles();
    }, [page, search]);

    const handleSearchChange = (e) => {
        setSearch(e.target.value);
        setPage(1); // Reset to the first page when search changes
    };

    const handlePageChange = (newPage) => {
        if (newPage >= 1 && newPage <= totalPages) {
            setPage(newPage);
        }
    };

    return (
        <div>
            <h1>Files</h1>
            <input
                type="text"
                placeholder="Search by description"
                value={search}
                onChange={handleSearchChange}
            />
            {loading ? (
                <p>Loading...</p>
            ) : error ? (
                <p>{error}</p>
            ) : (
                <>
                    <table>
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>File Path</th>
                                <th>Description</th>
                            </tr>
                        </thead>
                        <tbody>
                            {files.map(file => (
                                <tr key={file._id}>
                                    <td>{file.type}</td>
                                    <td>{file.file_path}</td>
                                    <td>{file.description}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    <div>
                        <button onClick={() => handlePageChange(page - 1)} disabled={page === 1}>
                            Previous
                        </button>
                        <span>Page {page} of {totalPages}</span>
                        <button onClick={() => handlePageChange(page + 1)} disabled={page === totalPages}>
                            Next
                        </button>
                    </div>
                </>
            )}
        </div>
    );
};

export default Files;
