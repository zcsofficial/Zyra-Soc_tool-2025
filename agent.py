import os
import platform
import psutil
import pymongo
from pymongo.errors import CollectionInvalid
from urllib.parse import quote_plus
import time

# MongoDB connection details from environment variables
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
client = pymongo.MongoClient(mongo_uri)
db = client[database_name]

# Ensure collections exist or create them
collection_names = ['events', 'network', 'files', 'authentication']
collections = {}
for name in collection_names:
    if name not in db.list_collection_names():
        collections[name] = db.create_collection(name)
    else:
        collections[name] = db[name]

# Log event function
def log_event(event_data, collection_name):
    try:
        collection = collections[collection_name]
        collection.insert_one(event_data)
        print(f"Logged event to {collection_name}: {event_data}")
    except Exception as e:
        print(f"Failed to log event: {e}")

# Collect Login Attempts
def monitor_logins():
    if platform.system() == "Windows":
        monitor_logins_windows()
    else:
        monitor_logins_linux()

def monitor_logins_windows():
    import win32evtlog
    server = 'localhost'
    logtype = 'Security'
    hand = win32evtlog.OpenEventLog(server, logtype)
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    events = win32evtlog.ReadEventLog(hand, flags, 0)

    for event in events:
        if event.EventID == 4624:  # Successful login
            log_event({
                'type': 'Login Success',
                'user': event.StringInserts[5],
                'description': f'Successful login for user {event.StringInserts[5]}'
            }, 'authentication')
        elif event.EventID == 4625:  # Failed login
            log_event({
                'type': 'Login Failure',
                'user': event.StringInserts[5],
                'description': f'Failed login attempt for user {event.StringInserts[5]}'
            }, 'authentication')

def monitor_logins_linux():
    log_paths = ['/var/log/auth.log', '/var/log/secure']
    
    for log_path in log_paths:
        if os.path.exists(log_path):
            with open(log_path) as f:
                lines = f.readlines()

            for line in lines:
                if 'sshd' in line and 'Failed password' in line:
                    log_event({
                        'type': 'Login Failure',
                        'description': line.strip()
                    }, 'authentication')
                elif 'sshd' in line and 'Accepted password' in line:
                    log_event({
                        'type': 'Login Success',
                        'description': line.strip()
                    }, 'authentication')
            break  # Exit loop once the log file is found and processed
        else:
            print(f"Log file not found: {log_path}")

# Process Monitoring
def monitor_processes():
    for proc in psutil.process_iter(['pid', 'name', 'username']):
        log_event({
            'type': 'Process Execution',
            'pid': proc.info['pid'],
            'process_name': proc.info['name'],
            'user': proc.info['username'],
            'description': f'Process {proc.info["name"]} executed by {proc.info["username"]}'
        }, 'events')

# Network Activity Monitoring
def monitor_network():
    connections = psutil.net_connections(kind='inet')
    for conn in connections:
        if conn.status == 'ESTABLISHED':
            log_event({
                'type': 'Network Connection',
                'local_address': f'{conn.laddr.ip}:{conn.laddr.port}',
                'remote_address': f'{conn.raddr.ip}:{conn.raddr.port}' if conn.raddr else 'N/A',
                'description': f'Established connection from {conn.laddr.ip}:{conn.laddr.port} to {conn.raddr.ip}:{conn.raddr.port}'
            }, 'network')

# File System Monitoring with os.walk()
def monitor_filesystem(path_to_watch):
    modified_files = set()
    
    while True:
        for root, dirs, files in os.walk(path_to_watch):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if file_path not in modified_files:
                    modified_files.add(file_path)
                    log_event({
                        'type': 'File Created',
                        'file_path': file_path,
                        'description': f'File created: {file_path}'
                    }, 'files')
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if dir_path not in modified_files:
                    modified_files.add(dir_path)
                    log_event({
                        'type': 'Directory Created',
                        'file_path': dir_path,
                        'description': f'Directory created: {dir_path}'
                    }, 'files')
        
        # Sleep for a while before re-checking
        time.sleep(10)

def main():
    # Start monitoring system components
    monitor_logins()
    monitor_processes()
    monitor_network()

    # Monitor the entire filesystem
    monitor_filesystem("/")

if __name__ == "__main__":
    main()
