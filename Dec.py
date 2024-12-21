import os
import platform
import psutil
import pymongo
from pymongo.errors import PyMongoError
from urllib.parse import quote_plus
import time
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import threading

# Flask App Initialization
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB Connection and Initialization
class MongoDBHandler:
    def __init__(self):
        username = os.getenv('MONGO_USER', 'adnan')
        password = os.getenv('MONGO_PASSWORD', 'Adnan@4441')
        cluster_name = os.getenv('MONGO_CLUSTER', 'soc-agent')
        database_name = os.getenv('MONGO_DB_NAME', 'network_packets')

        # URL encode credentials
        username_encoded = quote_plus(username)
        password_encoded = quote_plus(password)

        # MongoDB URI
        mongo_uri = f"mongodb+srv://{username_encoded}:{password_encoded}@{cluster_name}.5rryr.mongodb.net/{database_name}?retryWrites=true&w=majority&appName=Soc-Agent"

        # Connect to MongoDB
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[database_name]

        # Ensure collections exist or create them
        collection_names = ['events', 'network', 'files', 'authentication']
        self.collections = {}
        for name in collection_names:
            if name not in self.db.list_collection_names():
                self.collections[name] = self.db.create_collection(name)
            else:
                self.collections[name] = self.db[name]

    def log_event(self, event_data, collection_name):
        try:
            collection = self.collections[collection_name]
            collection.insert_one(event_data)
            print(f"Logged event to {collection_name}: {event_data}")
        except PyMongoError as e:
            print(f"Failed to log event to {collection_name}: {e}")

# Monitoring Classes
class LoginMonitor:
    def __init__(self, db_handler):
        self.db_handler = db_handler
        self.running = False

    def monitor_logins(self):
        self.running = True
        try:
            if platform.system() == "Windows":
                self._monitor_logins_windows()
            else:
                self._monitor_logins_linux()
        except Exception as e:
            print(f"Error in monitoring logins: {e}")
        finally:
            self.running = False

    def _monitor_logins_windows(self):
        import win32evtlog
        server = 'localhost'
        logtype = 'Security'
        hand = win32evtlog.OpenEventLog(server, logtype)
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        events = win32evtlog.ReadEventLog(hand, flags, 0)

        for event in events:
            if event.EventID == 4624:  # Successful login
                self.db_handler.log_event({
                    'type': 'Login Success',
                    'user': event.StringInserts[5],
                    'description': f'Successful login for user {event.StringInserts[5]}'
                }, 'authentication')
            elif event.EventID == 4625:  # Failed login
                self.db_handler.log_event({
                    'type': 'Login Failure',
                    'user': event.StringInserts[5],
                    'description': f'Failed login attempt for user {event.StringInserts[5]}'
                }, 'authentication')

    def _monitor_logins_linux(self):
        log_paths = ['/var/log/auth.log', '/var/log/secure']
        for log_path in log_paths:
            if os.path.exists(log_path):
                try:
                    with open(log_path) as f:
                        lines = f.readlines()

                    for line in lines:
                        if 'sshd' in line and 'Failed password' in line:
                            self.db_handler.log_event({
                                'type': 'Login Failure',
                                'description': line.strip()
                            }, 'authentication')
                        elif 'sshd' in line and 'Accepted password' in line:
                            self.db_handler.log_event({
                                'type': 'Login Success',
                                'description': line.strip()
                            }, 'authentication')
                except Exception as e:
                    print(f"Error reading {log_path}: {e}")
                break
            else:
                print(f"Log file not found: {log_path}")

class ProcessMonitor:
    def __init__(self, db_handler):
        self.db_handler = db_handler
        self.running = False

    def monitor_processes(self):
        self.running = True
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                self.db_handler.log_event({
                    'type': 'Process Execution',
                    'pid': proc.info['pid'],
                    'process_name': proc.info['name'],
                    'user': proc.info['username'],
                    'description': f'Process {proc.info["name"]} executed by {proc.info["username"]}'
                }, 'events')
        except Exception as e:
            print(f"Error in monitoring processes: {e}")
        finally:
            self.running = False

class NetworkMonitor:
    def __init__(self, db_handler):
        self.db_handler = db_handler
        self.running = False

    def monitor_network(self):
        self.running = True
        try:
            connections = psutil.net_connections(kind='inet')
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    self.db_handler.log_event({
                        'type': 'Network Connection',
                        'local_address': f'{conn.laddr.ip}:{conn.laddr.port}',
                        'remote_address': f'{conn.raddr.ip}:{conn.raddr.port}' if conn.raddr else 'N/A',
                        'description': f'Established connection from {conn.laddr.ip}:{conn.laddr.port} to {conn.raddr.ip}:{conn.raddr.port}'
                    }, 'network')
        except Exception as e:
            print(f"Error in monitoring network connections: {e}")
        finally:
            self.running = False

class FileSystemMonitor:
    def __init__(self, db_handler, path_to_watch="/"):
        self.db_handler = db_handler
        self.path_to_watch = path_to_watch
        self.running = False

    def monitor_filesystem(self):
        self.running = True
        modified_files = set()
        while self.running:
            try:
                for root, dirs, files in os.walk(self.path_to_watch):
                    for file_name in files:
                        file_path = os.path.join(root, file_name)
                        if file_path not in modified_files:
                            modified_files.add(file_path)
                            self.db_handler.log_event({
                                'type': 'File Created',
                                'file_path': file_path,
                                'description': f'File created: {file_path}'
                            }, 'files')
                    for dir_name in dirs:
                        dir_path = os.path.join(root, dir_name)
                        if dir_path not in modified_files:
                            modified_files.add(dir_path)
                            self.db_handler.log_event({
                                'type': 'Directory Created',
                                'file_path': dir_path,
                                'description': f'Directory created: {dir_path}'
                            }, 'files')
            except Exception as e:
                print(f"Error in monitoring filesystem: {e}")
            
            # Sleep for a while before re-checking
            time.sleep(10)

    def stop(self):
        self.running = False

# Global Variables to Track Monitoring Threads
monitor_threads = {}
monitors = {}

# Initialize MongoDB Handler
db_handler = MongoDBHandler()

# Initialize Monitors
monitors['login'] = LoginMonitor(db_handler)
monitors['process'] = ProcessMonitor(db_handler)
monitors['network'] = NetworkMonitor(db_handler)
monitors['filesystem'] = FileSystemMonitor(db_handler)

# Flask Routes for File Operations
ROOT_DIR = '/'  # Adjust this path as needed

@app.route('/list', methods=['GET'])
def list_files():
    path = request.args.get('path', ROOT_DIR)
    full_path = os.path.join(ROOT_DIR, path.strip('/'))
    
    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        return jsonify({'error': 'Directory not found'}), 404

    files = os.listdir(full_path)
    return jsonify({'files': files})

@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400
    
    safe_filename = os.path.basename(filename)
    directory = os.path.dirname(filename)
    
    full_path = os.path.join(ROOT_DIR, directory.strip('/'), safe_filename)
    
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_from_directory(directory, safe_filename, as_attachment=True)

@app.route('/delete', methods=['DELETE'])
def delete_file():
    filename = request.args.get('filename')
    if not filename:
        return jsonify({'error': 'Filename is required'}), 400
    
    safe_filename = os.path.basename(filename)
    directory = os.path.dirname(filename)
    full_path = os.path.join(ROOT_DIR, directory.strip('/'), safe_filename)
    
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return jsonify({'error': 'File not found'}), 404
    
    os.remove(full_path)
    return jsonify({'message': 'File deleted successfully'})

@app.route('/help', methods=['GET'])
def help_menu():
    help_text = (
        "Available commands:\n"
        "ls            - List files in the current directory\n"
        "cd <dir>      - Change directory\n"
        "cd ..         - Move up one directory\n"
        "pwd           - Print working directory\n"
        "download <file> - Download a file\n"
        "delete <file> - Delete a file\n"
        "help          - Show this help menu\n"
        "start <monitor> - Start a monitoring task (login, process, network, filesystem)\n"
        "stop <monitor>  - Stop a monitoring task\n"
        "status        - Check the status of all monitoring tasks"
    )
    return jsonify({'help': help_text})

# Flask Routes for Monitoring Control
@app.route('/start', methods=['POST'])
def start_monitor():
    monitor_type = request.json.get('monitor_type')
    
    if monitor_type not in monitors:
        return jsonify({'error': f'Unknown monitor type: {monitor_type}'}), 400
    
    if monitor_type in monitor_threads and monitor_threads[monitor_type].is_alive():
        return jsonify({'message': f'{monitor_type} monitoring is already running'}), 200
    
    monitor_thread = threading.Thread(target=monitors[monitor_type].monitor_logins if monitor_type == 'login' else monitors[monitor_type].monitor_processes if monitor_type == 'process' else monitors[monitor_type].monitor_network if monitor_type == 'network' else monitors[monitor_type].monitor_filesystem)
    monitor_thread.start()
    monitor_threads[monitor_type] = monitor_thread
    
    return jsonify({'message': f'{monitor_type} monitoring started'}), 200

@app.route('/stop', methods=['POST'])
def stop_monitor():
    monitor_type = request.json.get('monitor_type')
    
    if monitor_type not in monitors:
        return jsonify({'error': f'Unknown monitor type: {monitor_type}'}), 400
    
    if monitor_type not in monitor_threads or not monitor_threads[monitor_type].is_alive():
        return jsonify({'message': f'{monitor_type} monitoring is not running'}), 200
    
    monitors[monitor_type].stop()
    monitor_threads[monitor_type].join()
    
    return jsonify({'message': f'{monitor_type} monitoring stopped'}), 200

@app.route('/status', methods=['GET'])
def status():
    status = {}
    for monitor_type, monitor in monitors.items():
        status[monitor_type] = monitor.running
    
    return jsonify(status)

if __name__ == '__main__':
    app.run(port=5050)
