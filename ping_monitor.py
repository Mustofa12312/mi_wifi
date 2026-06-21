import subprocess
import re
import time
from database import get_db_connection, add_ping_record, update_device

def ping_device(ip):
    try:
        # Ping with 1 packet, 1 second timeout
        result = subprocess.run(['ping', '-c', '1', '-W', '1', ip], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Parse latency
            match = re.search(r'time=([\d.]+)\s*ms', result.stdout)
            if match:
                return float(match.group(1))
        return None
    except Exception as e:
        print(f"[!] Error pinging {ip}: {e}")
        return None

def monitor_pings():
    print("[*] Starting ping monitor cycle...")
    conn = get_db_connection()
    c = conn.cursor()
    # Get all online devices
    c.execute('SELECT id, ip, mac, vendor, hostname FROM devices WHERE online = 1')
    devices = c.fetchall()
    
    for device in devices:
        latency = ping_device(device['ip'])
        if latency is not None:
            # Device is still online, record ping
            add_ping_record(device['id'], latency)
        else:
            # Device didn't respond to ping, maybe offline
            print(f"[-] Device {device['ip']} missed ping.")
            # If we want to aggressively mark offline here, we could:
            # update_device(device['ip'], device['mac'], device['vendor'], device['hostname'], is_online=False)
            
    conn.close()
    print("[+] Ping cycle complete.")

def run_ping_loop(interval=30):
    while True:
        monitor_pings()
        time.sleep(interval)

if __name__ == '__main__':
    monitor_pings()
