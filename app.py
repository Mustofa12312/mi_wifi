from flask import Flask, render_template, jsonify, Response
from database import init_db, get_db_connection
from reports.exporter import generate_devices_csv
from security.scanner import scan_ports_and_os
from automation.rules import run_automation_engine
from observatory.sniffer import start_dns_sniffer
import threading

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

from scanner import scan_network, run_scanner_loop
from ping_monitor import run_ping_loop
import threading

@app.route('/api/scan')
def api_scan():
    # Trigger a network scan in the background
    threading.Thread(target=scan_network, daemon=True).start()
    return jsonify({"message": "Scan triggered in background. Please wait a moment."})

@app.route('/api/devices')
def api_devices():
    conn = get_db_connection()
    devices = conn.execute('SELECT * FROM devices ORDER BY last_seen DESC').fetchall()
    conn.close()
    return jsonify([dict(d) for d in devices])

@app.route('/api/ping')
def api_ping():
    conn = get_db_connection()
    history = conn.execute('''
        SELECT d.ip, d.hostname, p.latency, p.created_at 
        FROM ping_history p 
        JOIN devices d ON p.device_id = d.id 
        ORDER BY p.created_at DESC LIMIT 50
    ''').fetchall()
    conn.close()
    return jsonify([dict(h) for h in history])

@app.route('/api/export/devices.csv')
def export_devices_csv():
    csv_data = generate_devices_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=devices_report.csv"}
    )

@app.route('/api/scan_ports/<ip>')
def api_scan_ports(ip):
    # Runs the advanced NMAP scan in the background, or blocking for now
    # Since nmap might take time, we can run it asynchronously or blocking. 
    # Let's run it blocking so the frontend can show the result immediately for this IP.
    result = scan_ports_and_os(ip)
    return jsonify(result)

if __name__ == '__main__':
    # Start background tasks
    print("[*] Starting Background Scanner Thread...")
    scanner_thread = threading.Thread(target=run_scanner_loop, args=(60,), daemon=True)
    scanner_thread.start()
    
    print("[*] Starting Background Ping Monitor Thread...")
    ping_thread = threading.Thread(target=run_ping_loop, args=(30,), daemon=True)
    ping_thread.start()
    
    print("[*] Starting Automation Engine Thread...")
    auto_thread = threading.Thread(target=run_automation_engine, args=(30,), daemon=True)
    auto_thread.start()
    
    print("[*] Starting DNS Observatory Thread...")
    dns_thread = threading.Thread(target=start_dns_sniffer, daemon=True)
    dns_thread.start()
    
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
