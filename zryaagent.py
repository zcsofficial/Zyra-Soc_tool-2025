import json
import time
import socket
import requests
from scapy.all import sniff, Raw, IP, TCP
from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

# MySQL credentials
MYSQL_HOST = "localhost"
MYSQL_USER = "root"
MYSQL_PASSWORD = "Adnan@66202"
MYSQL_DATABASE = "network_packets"

# Connect to MySQL
def get_db_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE
    )

# Ensure tables exist
def ensure_tables():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS packets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp DOUBLE,
        src_ip VARCHAR(255),
        dst_ip VARCHAR(255),
        protocol INT,
        length INT,
        raw_data TEXT,
        src_port INT,
        dst_port INT,
        protocol_name VARCHAR(50)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS http_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        timestamp DOUBLE,
        src_ip VARCHAR(255),
        dst_ip VARCHAR(255),
        src_port INT,
        dst_port INT,
        method VARCHAR(10),
        headers TEXT,
        body TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS top10ip (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ip VARCHAR(255),
        count INT,
        city VARCHAR(255),
        region VARCHAR(255),
        country VARCHAR(255),
        isp VARCHAR(255)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_info (
        id INT AUTO_INCREMENT PRIMARY KEY,
        hostname VARCHAR(255),
        internal_ip VARCHAR(255)
    )
    ''')

    connection.commit()
    cursor.close()
    connection.close()

ensure_tables()

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
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM system_info")
    cursor.execute(
        "INSERT INTO system_info (hostname, internal_ip) VALUES (%s, %s)",
        (system_info['hostname'], system_info['internal_ip'])
    )
    connection.commit()
    cursor.close()
    connection.close()

save_system_info()

def packet_callback(packet):
    connection = get_db_connection()
    cursor = connection.cursor()

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

                    cursor.execute(
                        """
                        INSERT INTO http_data (timestamp, src_ip, dst_ip, src_port, dst_port, method, headers, body)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (time.time(), ip_layer.src, ip_layer.dst, packet[TCP].sport, packet[TCP].dport, method, json.dumps(headers), body)
                    )

        cursor.execute(
            """
            INSERT INTO packets (timestamp, src_ip, dst_ip, protocol, length, raw_data, src_port, dst_port, protocol_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                packet_info['timestamp'], packet_info['src_ip'], packet_info['dst_ip'], packet_info['protocol'],
                packet_info['length'], packet_info['raw_data'], packet_info.get('src_port'),
                packet_info.get('dst_port'), packet_info.get('protocol_name')
            )
        )

        connection.commit()
        cursor.close()
        connection.close()

        print(f"Packet captured and stored: {packet_info}")

def parse_http_headers(payload):
    headers = {}
    try:
        raw_headers = payload.split(b'\r\n\r\n')[0]
        for line in raw_headers.split(b'\r\n')[1:]:
            key, value = line.split(b': ', 1)
            headers[key.decode()] = value.decode()
    except Exception as e:
        print("Error parsing headers:", e)
    return headers

def extract_http_body(payload):
    body = {}
    try:
        if b'\r\n\r\n' in payload:
            body_start_index = payload.index(b'\r\n\r\n') + 4
            body = payload[body_start_index:].decode(errors='ignore')
    except Exception as e:
        print("Error extracting body:", e)
    return body

def start_sniffing():
    sniff(prn=packet_callback, store=0)

@app.route('/api/system_info', methods=['GET'])
def get_system_info_api():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM system_info LIMIT 1")
    system_info = cursor.fetchone()
    cursor.close()
    connection.close()
    return jsonify(system_info)

@app.route('/api/packets', methods=['GET'])
def get_packets():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM packets ORDER BY timestamp DESC LIMIT 100")
    packets = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(packets)

@app.route('/api/http_data', methods=['GET'])
def get_http_data():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM http_data ORDER BY timestamp DESC LIMIT 100")
    http_packets = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(http_packets)

@app.route('/api/top_ips', methods=['GET'])
def get_top_ips():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute('''
    SELECT src_ip AS ip, COUNT(*) AS count 
    FROM packets 
    GROUP BY src_ip 
    ORDER BY count DESC 
    LIMIT 10
    ''')
    top_ips = cursor.fetchall()

    top_ips_info = []
    for ip in top_ips:
        location_data = requests.get(f'http://ip-api.com/json/{ip["ip"]}').json()
        top_ips_info.append({
            'ip': ip['ip'],
            'count': ip['count'],
            'city': location_data.get('city', 'N/A'),
            'region': location_data.get('regionName', 'N/A'),
            'country': location_data.get('country', 'N/A'),
            'isp': location_data.get('isp', 'N/A'),
        })

    cursor.close()
    connection.close()
    return jsonify(top_ips_info)

@app.route('/api/stats', methods=['GET'])
def get_packet_stats():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
    SELECT protocol_name, COUNT(*) AS count 
    FROM packets 
    GROUP BY protocol_name
    ''')
    stats = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(stats)

if __name__ == "__main__":
    from multiprocessing import Process
    p = Process(target=start_sniffing)
    p.start()
    app.run(host='0.0.0.0', port=5000, debug=True)
    p.join()
