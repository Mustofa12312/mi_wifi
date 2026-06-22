import csv
import io
from database import get_db_connection

def generate_devices_csv():
    """
    Generates a CSV string containing all devices and their status.
    """
    conn = get_db_connection()
    devices = conn.execute('SELECT * FROM devices ORDER BY last_seen DESC').fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['ID', 'IP Address', 'MAC Address', 'Vendor', 'Hostname', 'First Seen', 'Last Seen', 'Status', 'OS Type', 'Open Ports'])
    
    for d in devices:
        status = 'Online' if d['online'] == 1 else 'Offline'
        writer.writerow([
            d['id'], 
            d['ip'], 
            d['mac'], 
            d['vendor'], 
            d['hostname'], 
            d['first_seen'], 
            d['last_seen'], 
            status,
            d['os_type'] or 'Unknown',
            d['open_ports'] or 'None'
        ])
        
    return output.getvalue()
