import subprocess
import re
from database import update_device_details

def scan_ports_and_os(ip):
    """
    Runs nmap -O -F (Fast scan + OS detection) on the target IP.
    Requires root/sudo privileges to perform OS detection accurately.
    """
    print(f"[*] Starting advanced security scan on {ip}...")
    try:
        # Note: -O requires sudo. If it fails, we still get ports from -F
        result = subprocess.run(['nmap', '-O', '-F', ip], capture_output=True, text=True)
        output = result.stdout
        
        # Parse Open Ports
        open_ports = []
        port_pattern = re.compile(r'^(\d+)/tcp\s+open\s+([a-zA-Z0-9-]+)', re.MULTILINE)
        for match in port_pattern.finditer(output):
            open_ports.append(f"{match.group(1)} ({match.group(2)})")
            
        ports_str = ", ".join(open_ports) if open_ports else "None"
        
        # Parse OS
        os_type = "Unknown"
        os_match = re.search(r'(OS details|Running|Aggressive OS guesses): (.+)', output)
        if os_match:
            os_type = os_match.group(2).strip()
        else:
            # Check if running without sudo warning
            if "requires root privileges" in result.stderr or "requires root privileges" in output:
                os_type = "Unknown (Requires sudo)"
                
        print(f"[+] Scan result for {ip} -> OS: {os_type}, Ports: {ports_str}")
        
        # Update database
        update_device_details(ip, os_type, ports_str)
        return {"ip": ip, "os_type": os_type, "open_ports": ports_str}
        
    except Exception as e:
        print(f"[!] Error scanning {ip}: {e}")
        return {"error": str(e)}

if __name__ == '__main__':
    # Test
    # print(scan_ports_and_os('127.0.0.1'))
    pass
