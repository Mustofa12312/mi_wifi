import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'network.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            mac TEXT,
            vendor TEXT,
            hostname TEXT,
            first_seen DATETIME,
            last_seen DATETIME,
            online INTEGER,
            os_type TEXT,
            open_ports TEXT,
            custom_name TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS ping_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id INTEGER,
            latency REAL,
            created_at DATETIME,
            FOREIGN KEY (device_id) REFERENCES devices (id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS speedtest_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            download REAL,
            upload REAL,
            ping REAL,
            created_at DATETIME
        )
    ''')
    
    # Simple Migration to add columns if they don't exist
    try:
        c.execute('ALTER TABLE devices ADD COLUMN os_type TEXT')
        c.execute('ALTER TABLE devices ADD COLUMN open_ports TEXT')
        c.execute('ALTER TABLE devices ADD COLUMN custom_name TEXT')
    except sqlite3.OperationalError:
        pass # Columns already exist
        
    # Set all devices offline on startup
    c.execute('UPDATE devices SET online = 0')
    
    conn.commit()
    conn.close()

def update_device(ip, mac, vendor, hostname, is_online):
    conn = get_db_connection()
    c = conn.cursor()
    now = datetime.now()
    
    c.execute('SELECT id FROM devices WHERE mac = ? OR ip = ?', (mac, ip))
    device = c.fetchone()
    
    if device:
        # Update existing
        c.execute('''
            UPDATE devices 
            SET ip = ?, mac = ?, vendor = ?, hostname = ?, last_seen = ?, online = ?
            WHERE id = ?
        ''', (ip, mac, vendor, hostname, now, 1 if is_online else 0, device['id']))
    else:
        # Insert new
        if is_online:
            c.execute('''
                INSERT INTO devices (ip, mac, vendor, hostname, first_seen, last_seen, online)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (ip, mac, vendor, hostname, now, now, 1))
            
    conn.commit()
    conn.close()

def add_ping_record(device_id, latency):
    if latency is None:
        return
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO ping_history (device_id, latency, created_at) VALUES (?, ?, ?)',
              (device_id, latency, datetime.now()))
    conn.commit()
    conn.close()

def set_all_offline():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE devices SET online = 0')
    conn.commit()
    conn.close()

def update_device_details(ip, os_type, open_ports):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE devices SET os_type = ?, open_ports = ? WHERE ip = ?', (os_type, open_ports, ip))
    conn.commit()
    conn.close()


def update_device_alias(ip, custom_name):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE devices SET custom_name = ? WHERE ip = ?', (custom_name, ip))
    conn.commit()
    conn.close()

def add_speedtest_record(download, upload, ping):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO speedtest_history (download, upload, ping, created_at) VALUES (?, ?, ?, ?)',
              (download, upload, ping, datetime.now()))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
