import json
import time
import socket
import requests
from scapy.all import sniff, Raw, IP, TCP
from pymongo import MongoClient
from flask import Flask, jsonify
from flask_cors import CORS
from urllib.parse import quote_plus

# MongoDB credentials
username = "adnan"
password = "Adnan@4441"
cluster_name = "soc-agent"
database_name = "network_packets"

username_encoded = quote_plus(username)
password_encoded = quote_plus(password)

MONGO_URI = f"mongodb+srv://{username_encoded}:{password_encoded}@{cluster_name}.5rryr.mongodb.net/{database_name}?retryWrites=true&w=majority&appName=Soc-Agent"

client = MongoClient(MONGO_URI)
db = client[database_name]

# Ensure collections exist
def ensure_collections():
    if 'packets' not in db.list_collection_names():
        db.create_collection('packets')
    if 'http-data' not in db.list_collection_names():
        db.create_collection('http-data')
    if 'top10ip' not in db.list_collection_names():
        db.create_collection('top10ip')

ensure_collections()

app = Flask(__name__)
CORS(app)

def get_system_info():
    hostname = socket.gethostname()
    internal_ip = socket.gethostbyname(hostname)
    return {
        'hostname': hostname,
        'internal_ip': internal_ip
    }

def save_system_info():
    system_info = get_system_info()
    system_info_collection = db['system_info']
    system_info_collection.delete_many({})
    system_info_collection.insert_one(system_info)

save_system_info()

def packet_callback(packet):
    if IP in packet:
        ip_layer = packet[IP]
        packet_info = {
            'timestamp': time.time(),
            'src_ip': ip_layer.src,
            'dst_ip': ip_layer.dst,
            'protocol': packet.proto,
            'length': len(packet),
            'raw_data': bytes(packet).hex()
        }
        
        if packet.haslayer(TCP):
            packet_info['src_port'] = packet[TCP].sport
            packet_info['dst_port'] = packet[TCP].dport
            packet_info['protocol_name'] = 'TCP'

            if packet.haslayer(Raw):
                payload = packet[Raw].load
                if b"POST" in payload or b"GET" in payload:
                    method = 'GET' if b"GET" in payload else 'POST'
                    headers = parse_http_headers(payload)
                    body = extract_http_body(payload)

                    http_data = {
                        'timestamp': time.time(),
                        'src_ip': ip_layer.src,
                        'dst_ip': ip_layer.dst,
                        'src_port': packet[TCP].sport,
                        'dst_port': packet[TCP].dport,
                        'method': method,
                        'headers': headers,
                        'body': body
                    }
                    db['http-data'].insert_one(http_data)  # Store in http-data collection
                    print(f"HTTP {method} captured and stored: {http_data}")

        # Store general packet info
        db['packets'].insert_one(packet_info)
        print(f"Packet captured and stored: {packet_info}")

def parse_http_headers(payload):
    """Parse the HTTP headers from the payload."""
    headers = {}
    try:
        raw_headers = payload.split(b'\r\n\r\n')[0]  # Get headers
        for line in raw_headers.split(b'\r\n')[1:]:
            key, value = line.split(b': ', 1)
            headers[key.decode()] = value.decode()
    except Exception as e:
        print("Error parsing headers:", e)
    return headers

def extract_http_body(payload):
    """Extract the HTTP body from the payload."""
    body = {}
    try:
        if b'\r\n\r\n' in payload:
            body_start_index = payload.index(b'\r\n\r\n') + 4  # 4 to skip the \r\n\r\n
            body = payload[body_start_index:].decode(errors='ignore')
    except Exception as e:
        print("Error extracting body:", e)
    return body

def start_sniffing():
    sniff(prn=packet_callback, store=0)

@app.route('/api/system_info', methods=['GET'])
def get_system_info_api():
    system_info = db['system_info'].find_one()
    if system_info:
        system_info['_id'] = str(system_info['_id'])
    return jsonify(system_info)

@app.route('/api/packets', methods=['GET'])
def get_packets():
    packets = list(db['packets'].find().sort("timestamp", -1).limit(100))
    for packet in packets:
        packet['_id'] = str(packet['_id'])
    return jsonify(packets)

@app.route('/api/http_data', methods=['GET'])
def get_http_data():
    http_packets = list(db['http-data'].find().sort("timestamp", -1).limit(100))
    for packet in http_packets:
        packet['_id'] = str(packet['_id'])
    return jsonify(http_packets)

@app.route('/api/top_ips', methods=['GET'])
def get_top_ips():
    pipeline = [
        {
            '$group': {
                '_id': '$src_ip',
                'count': {'$sum': 1}
            }
        },
        {
            '$sort': {'count': -1}
        },
        {
            '$limit': 10
        }
    ]
    top_ips = list(db['packets'].aggregate(pipeline))
    top_ips_info = []
    
    for ip in top_ips:
        ip_address = ip['_id']
        location_data = requests.get(f'http://ip-api.com/json/{ip_address}').json()
        top_ips_info.append({
            'ip': ip_address,
            'count': ip['count'],
            'city': location_data.get('city', 'N/A'),
            'region': location_data.get('regionName', 'N/A'),
            'country': location_data.get('country', 'N/A'),
            'isp': location_data.get('isp', 'N/A'),
        })

    # Save the top 10 IPs to the 'top10ip' collection
    db['top10ip'].delete_many({})  # Clear the collection before inserting new data
    db['top10ip'].insert_many(top_ips_info)

    return jsonify(top_ips_info)

@app.route('/api/threat_intelligence', methods=['GET'])
def get_threat_intelligence():
    packets = list(db['packets'].find())
    threat_data = []

    for packet in packets:
        src_ip = packet['src_ip']
        dst_ip = packet['dst_ip']

        src_threat_info = analyze_ip(src_ip)
        dst_threat_info = analyze_ip(dst_ip)

        threat_data.append({
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'src_is_malicious': src_threat_info['malicious'],
            'dst_is_malicious': dst_threat_info['malicious'],
            'src_response': src_threat_info,
            'dst_response': dst_threat_info,
        })

    return jsonify(threat_data)

def analyze_ip(ip):
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {
        'x-apikey': 'e4611d3bfb028abacfed5a9d0013c7d21b8fb4015c91fa5dba1e705dccdb312f'  # Replace with your VirusTotal API key
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        malicious_count = data['data'].get('attributes', {}).get('last_analysis_stats', {}).get('malicious', 0)
        return {
            'malicious': malicious_count > 0,
            'count': malicious_count,
            'last_analysis': data['data'].get('attributes', {}).get('last_analysis_results', {})
        }
    else:
        return {
            'malicious': False,
            'count': 0,
            'last_analysis': {}
        }

@app.route('/api/stats', methods=['GET'])
def get_packet_stats():
    pipeline = [
        {
            '$group': {
                '_id': '$protocol_name',
                'count': {'$sum': 1}
            }
        }
    ]
    stats = list(db['packets'].aggregate(pipeline))
    return jsonify(stats)

if __name__ == "__main__":
    from multiprocessing import Process
    p = Process(target=start_sniffing)
    p.start()
    app.run(host='0.0.0.0', port=5000, debug=True)
    p.join()
