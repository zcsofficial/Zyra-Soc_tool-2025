CREATE DATABASE IF NOT EXISTS network_packets;

USE network_packets;

CREATE TABLE IF NOT EXISTS packets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DOUBLE,
    src_ip VARCHAR(45),
    dst_ip VARCHAR(45),
    protocol INT,
    length INT,
    src_port INT,
    dst_port INT,
    protocol_name VARCHAR(10),
    raw_data TEXT
);

CREATE TABLE IF NOT EXISTS http_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DOUBLE,
    src_ip VARCHAR(45),
    dst_ip VARCHAR(45),
    src_port INT,
    dst_port INT,
    method VARCHAR(10),
    headers TEXT,
    body TEXT
);

CREATE TABLE IF NOT EXISTS system_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hostname VARCHAR(255),
    internal_ip VARCHAR(45)
);

CREATE TABLE IF NOT EXISTS top10ip (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip VARCHAR(45),
    count INT,
    city VARCHAR(255),
    region VARCHAR(255),
    country VARCHAR(255),
    isp VARCHAR(255)
);
