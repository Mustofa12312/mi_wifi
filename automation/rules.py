import time

def evaluate_rules(devices):
    """
    Simple Rule Engine for Automation.
    Expects a list of device dictionary objects from the database.
    """
    # Rule 1: Alert on new unknown device
    for device in devices:
        # If device was first seen in the last 60 seconds and vendor is unknown
        # In a real app, we would store an 'acknowledged' flag in the database
        # For MVP, we just print an alert if we see an Unknown vendor that is online
        if device['vendor'] == 'Unknown' and device['online'] == 1:
            print(f"[ALERT] Perangkat tak dikenal terdeteksi online! IP: {device['ip']}, MAC: {device['mac']}")
            
        # Rule 2: Alert if Xiaomi device goes offline
        if device['vendor'] and 'Xiaomi' in device['vendor'] and device['online'] == 0:
            print(f"[WARNING] Xiaomi Smart Device ({device['ip']}) terputus dari jaringan!")

def run_automation_engine(interval=30):
    from database import get_db_connection
    while True:
        try:
            conn = get_db_connection()
            devices = conn.execute('SELECT * FROM devices').fetchall()
            conn.close()
            evaluate_rules(devices)
        except Exception as e:
            print(f"[!] Automation Engine Error: {e}")
            
        time.sleep(interval)
