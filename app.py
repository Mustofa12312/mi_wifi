from flask import Flask, render_template, jsonify
from database import init_db, get_db_connection

app = Flask(__name__)

# Initialize database
init_db()

@app.route('/')
def dashboard():
    conn = get_db_connection()
    devices = conn.execute('SELECT * FROM devices').fetchall()
    conn.close()
    
    online_count = sum(1 for d in devices if d['online'] == 1)
    offline_count = len(devices) - online_count
    xiaomi_count = sum(1 for d in devices if d['vendor'] and 'Xiaomi' in d['vendor'])
    
    # Dummy average latency
    avg_latency = 4.2
    
    stats = {
        'online_devices': online_count,
        'offline_devices': offline_count,
        'xiaomi_devices': xiaomi_count,
        'avg_latency': avg_latency
    }
    
    return render_template('dashboard.html', stats=stats, devices=devices)

@app.route('/devices')
def devices_page():
    conn = get_db_connection()
    devices = conn.execute('SELECT * FROM devices ORDER BY last_seen DESC').fetchall()
    conn.close()
    return render_template('devices.html', devices=devices)

@app.route('/api/scan')
def api_scan():
    # Placeholder for actual scan
    conn = get_db_connection()
    devices = conn.execute('SELECT ip, vendor, online as status FROM devices').fetchall()
    conn.close()
    result = [dict(d) for d in devices]
    for d in result:
        d['status'] = 'online' if d['status'] == 1 else 'offline'
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
