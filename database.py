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
            online INTEGER
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
    
    # insert dummy data for testing if empty
    c.execute('SELECT COUNT(*) FROM devices')
    if c.fetchone()[0] == 0:
        now = datetime.now()
        devices = [
            ('192.168.1.1', 'A1:B2:C3:D4:E5:F6', 'Fiberhome', 'Router', now, now, 1),
            ('192.168.1.3', '4C:C6:4C:A8:2A:E6', 'Xiaomi', 'Mi Wi-Fi Range Extender Pro', now, now, 1),
            ('192.168.1.64', '00:1A:2B:3C:4D:5E', 'Ubuntu', 'Server-R03', now, now, 1),
            ('192.168.1.45', 'AA:BB:CC:DD:EE:FF', 'Apple', 'Mustofa-iPhone', now, now, 0)
        ]
        c.executemany('''
            INSERT INTO devices (ip, mac, vendor, hostname, first_seen, last_seen, online)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', devices)
        
        c.execute('SELECT id FROM devices')
        for row in c.fetchall():
            c.execute('INSERT INTO ping_history (device_id, latency, created_at) VALUES (?, ?, ?)', (row['id'], 2.5, now))
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
