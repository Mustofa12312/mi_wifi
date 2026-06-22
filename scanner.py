import subprocess
import re
import time
from database import update_device, set_all_offline

from xiaomi.detector import probe_miio_port

def get_vendor(mac, ip):
    mac = mac.upper()
    
    # Active UDP Probe for Xiaomi IoT
    if probe_miio_port(ip):
        return 'Xiaomi Smart Device (MiIO)'
        
    # Simple offline vendor detection based on MAC prefix
    if mac.startswith('4C:C6:4C') or mac.startswith('64:09:80') or mac.startswith('50:D2:F5'):
        return 'Xiaomi'
    if mac.startswith('00:1A:2B') or mac.startswith('DC:A6:32'):
        return 'Raspberry/Ubuntu'
    if mac.startswith('A1:B2:C3'):
        return 'Fiberhome'
    return 'Unknown'

def scan_network(subnet="192.168.1.0/24"):
    print(f"[*] Starting network scan on {subnet}...")
    # 1. Ping sweep to populate ARP cache
    try:
        subprocess.run(['nmap', '-sn', subnet], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("[!] nmap not found, relying on existing ARP cache.")

    # 2. Read ARP cache
    try:
        arp_result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        lines = arp_result.stdout.split('\n')
        
        # Regex to parse: hostname (192.168.1.X) at MAC [ether] on IFACE
        # Or ? (192.168.1.X) at MAC [ether] on IFACE
        arp_pattern = re.compile(r'(?P<hostname>[^\s]+)\s+\((?P<ip>\d+\.\d+\.\d+\.\d+)\)\s+at\s+(?P<mac>[0-9a-fA-F:]+)')
        
        devices_found = []
        for line in lines:
            match = arp_pattern.search(line)
            if match:
                hostname = match.group('hostname') if match.group('hostname') != '?' else 'Unknown'
                ip = match.group('ip')
                mac = match.group('mac').upper()
                vendor = get_vendor(mac, ip)
                
                # Exclude broadcast
                if mac == 'FF:FF:FF:FF:FF:FF' or ip.endswith('.255'):
                    continue
                    
                devices_found.append((ip, mac, vendor, hostname))
        
        # Update database
        set_all_offline() # Reset status
        for ip, mac, vendor, hostname in devices_found:
            update_device(ip, mac, vendor, hostname, is_online=True)
            
        print(f"[+] Scan complete. Found {len(devices_found)} devices.")
        
    except Exception as e:
        print(f"[!] Error during scan: {e}")

def run_scanner_loop(interval=60):
    while True:
        scan_network()
        time.sleep(interval)

if __name__ == '__main__':
    scan_network()
