import subprocess
import re

def discover_miio_devices():
    """
    Scans the local network for MiIO devices using miiocli.
    """
    devices = []
    try:
        result = subprocess.run(['venv/bin/miiocli', 'discover', '--handshake'], capture_output=True, text=True)
        output = result.stdout + result.stderr
        
        # Parse output like:
        # IP 192.168.1.3 (ID: 12345) - token: b'ffffffffffffffffffffffffffffffff'
        pattern = re.compile(r'IP\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+\(ID:\s+(?P<id>[a-zA-Z0-9]+)\)\s+-\s+token:\s+b?\'?(?P<token>[0-9a-fA-F]+)\'?')
        
        # Also catch mdns output:
        # 192.168.1.3 (miio.repeater.v3)
        mdns_pattern = re.compile(r'(?P<ip>\d+\.\d+\.\d+\.\d+)\s+\((?P<model>[a-zA-Z0-9.-_]+)\)')
        
        ip_map = {}
        
        for line in output.split('\n'):
            mdns_match = mdns_pattern.search(line)
            if mdns_match:
                ip = mdns_match.group('ip')
                if ip not in ip_map:
                    ip_map[ip] = {"ip": ip, "mac": "Unknown", "product": mdns_match.group('model'), "token": "Hidden"}
            
            match = pattern.search(line)
            if match:
                ip = match.group('ip')
                if ip not in ip_map:
                    ip_map[ip] = {"ip": ip, "mac": "Unknown", "product": "Generic MiIO", "token": match.group('token')}
                else:
                    ip_map[ip]["token"] = match.group('token')
                    
        devices = list(ip_map.values())
        
    except Exception as e:
        print(f"[!] MiIO Discovery Error: {e}")
        
    return devices
