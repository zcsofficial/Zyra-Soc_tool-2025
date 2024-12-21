import React, { useState, useEffect } from 'react';

const Access = () => {
    const [currentPath, setCurrentPath] = useState('/');
    const [commandHistory, setCommandHistory] = useState([]);
    const [commandInput, setCommandInput] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [files, setFiles] = useState([]);

    const commands = ['ls', 'cd', 'pwd', 'download', 'delete', 'help'];

    useEffect(() => {
        if (currentPath) {
            fetchFiles(currentPath);
        }
    }, [currentPath]);

    const fetchFiles = async (path) => {
        try {
            const response = await fetch(`http://localhost:5050/list?path=${encodeURIComponent(path)}`);
            const data = await response.json();
            setFiles(data.files || []);
        } catch (error) {
            console.error('Error fetching files:', error);
            displayOutput(`Error fetching files: ${error.message}`);
        }
    };

    const executeCommand = async (command) => {
        const [cmd, ...args] = command.trim().split(' ');
        let output = '';

        try {
            switch (cmd) {
                case 'ls':
                    output = files.length > 0 ? files.join('\n') : 'No files found.';
                    break;
                case 'cd':
                    const newPath = args.join(' ');
                    if (newPath === '..') {
                        const pathParts = currentPath.split('/').filter(part => part);
                        pathParts.pop();
                        setCurrentPath(pathParts.join('/') || '/');
                    } else {
                        setCurrentPath(newPath.startsWith('/') ? newPath : `${currentPath}/${newPath}`);
                    }
                    output = `Changed directory to ${currentPath}`;
                    break;
                case 'pwd':
                    output = currentPath;
                    break;
                case 'help':
                    const helpResponse = await fetch('http://localhost:5050/help');
                    const helpData = await helpResponse.json();
                    output = helpData.help;
                    break;
                case 'download':
                    const fileToDownload = args.join(' ');
                    const downloadResponse = await fetch(`http://localhost:5050/download?filename=${encodeURIComponent(currentPath + '/' + fileToDownload)}`);
                    if (downloadResponse.ok) {
                        const blob = await downloadResponse.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = fileToDownload;
                        a.click();
                        window.URL.revokeObjectURL(url);
                        output = `Downloaded ${fileToDownload}`;
                    } else {
                        const errorData = await downloadResponse.json();
                        output = `Error: ${errorData.error}`;
                    }
                    break;
                case 'delete':
                    const fileToDelete = args.join(' ');
                    const deleteResponse = await fetch(`http://localhost:5050/delete?filename=${encodeURIComponent(currentPath + '/' + fileToDelete)}`, { method: 'DELETE' });
                    const deleteData = await deleteResponse.json();
                    output = deleteData.message || deleteData.error;
                    break;
                default:
                    output = 'Unknown command. Type `help` for a list of available commands.';
            }
        } catch (error) {
            output = `Error: ${error.message}`;
        }

        displayOutput(output);
    };

    const displayOutput = (text) => {
        setCommandHistory(prevHistory => [...prevHistory, { command: commandInput, output: text }]);
    };

    const handleInput = (event) => {
        setCommandInput(event.target.value);
        handleSuggestions(event.target.value);
    };

    const handleSuggestions = (inputValue) => {
        const [cmd, ...args] = inputValue.trim().split(' ');

        if (commands.includes(cmd)) {
            setSuggestions(commands.filter(c => c.startsWith(cmd)));
        } else if (args.length > 0) {
            const fileSuggestions = files.filter(f => f.startsWith(args.join(' ')));
            setSuggestions(fileSuggestions);
        } else {
            setSuggestions([]);
        }
    };

    const handleKeyDown = (event) => {
        if (event.key === 'Enter') {
            const command = commandInput;
            setCommandInput('');
            executeCommand(command);
            setSuggestions([]);
        } else if (event.key === 'Tab') {
            event.preventDefault();
            if (suggestions.length > 0) {
                setCommandInput(suggestions[0]);
                setSuggestions([]);
            }
        }
    };

    return (
        <div id="terminal-container">
            <div id="terminal-header">
                <div className="title">Terminal Dashboard</div>
                <div className="buttons">
                    <div className="btn btn-close"></div>
                    <div className="btn btn-minimize"></div>
                    <div className="btn btn-maximize"></div>
                </div>
            </div>
            <div id="terminal">
                <div id="output">
                    {commandHistory.map((entry, index) => (
                        <div key={index}>
                            <p className="command-output">
                                <span className="prompt">> {currentPath} </span>{entry.command}
                            </p>
                            <p className="command-output">{entry.output}</p>
                        </div>
                    ))}
                </div>
            </div>
            <div id="input-container">
                <input
                    id="input"
                    type="text"
                    value={commandInput}
                    onChange={handleInput}
                    onKeyDown={handleKeyDown}
                    autoFocus
                    placeholder="Enter command..."
                />
                <div id="suggestions" className="autocomplete-suggestions">
                    {suggestions.map((suggestion, index) => (
                        <div
                            key={index}
                            className="autocomplete-suggestion"
                            onClick={() => setCommandInput(suggestion)}
                        >
                            {suggestion}
                        </div>
                    ))}
                </div>
            </div>
            <style>
                {`
                    /* Global Styles */
                    * {
                        box-sizing: border-box;
                    }

                    body {
                        background-color: #0d0d0d;
                        font-family: 'Orbitron', sans-serif;
                        color: #ffffff;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        flex-direction: column;
                        min-height: 100vh;
                    }

                    #terminal-container {
                        width: 90%;
                        max-width: 1200px;
                        height: 70vh;
                        background-color: #1e272e;
                        border-radius: 10px;
                        box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.5);
                        overflow: hidden;
                        display: flex;
                        flex-direction: column;
                        margin: auto;
                    }

                    #terminal-header {
                        padding: 10px;
                        background-color: #2d3436;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        border-bottom: 1px solid #344952;
                    }

                    #terminal-header .title {
                        font-weight: bold;
                        font-size: 18px;
                    }

                    #terminal-header .buttons {
                        display: flex;
                        gap: 8px;
                    }

                    #terminal-header .buttons .btn {
                        width: 14px;
                        height: 14px;
                        border-radius: 50%;
                        cursor: pointer;
                    }

                    #terminal-header .btn-close {
                        background-color: #ff5e57;
                    }

                    #terminal-header .btn-minimize {
                        background-color: #febc2e;
                    }

                    #terminal-header .btn-maximize {
                        background-color: #28c940;
                    }

                    #terminal {
                        flex-grow: 1;
                        padding: 20px;
                        overflow-y: auto;
                        background-color: #000;
                        color: #00ff00;
                        font-size: 16px;
                        line-height: 1.4;
                    }

                    #input-container {
                        background-color: #2d3436;
                        padding: 10px;
                        border-top: 1px solid #344952;
                        position: relative;
                    }

                    #input {
                        width: calc(100% - 20px);
                        background-color: #1e272e;
                        border: none;
                        color: #00ff00;
                        font-size: 18px;
                        padding: 10px;
                        box-sizing: border-box;
                        border-radius: 4px;
                    }

                    .command-output {
                        margin: 0;
                        padding: 5px 0;
                        white-space: pre-wrap;
                    }

                    .prompt {
                        color: #ffcc00;
                    }

                    .autocomplete-suggestions {
                        background-color: #1e272e;
                        color: #00ff00;
                        border: 1px solid #00ff00;
                        max-height: 200px;
                        overflow-y: auto;
                        position: absolute;
                        z-index: 1000;
                        width: calc(100% - 20px);
                        left: 10px;
                        top: 40px;
                        box-sizing: border-box;
                        border-radius: 4px;
                    }

                    .autocomplete-suggestion {
                        padding: 8px;
                        cursor: pointer;
                    }

                    .autocomplete-suggestion:hover {
                        background-color: #005500;
                    }

                    @media (max-width: 768px) {
                        #terminal-container {
                            width: 100%;
                            height: 100vh;
                        }

                        #input {
                            font-size: 16px;
                        }
                    }
                `}
            </style>
        </div>
    );
};

export default Access;
