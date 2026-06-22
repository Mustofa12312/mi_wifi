import socket

def probe_miio_port(ip):
    """
    Sends a UDP discovery packet to port 54321 to identify a MiIO device.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.5)
        # MiIO discovery packet magic bytes (Helo string)
        magic_bytes = bytes.fromhex('21310020ffffffffffffffffffffffffffffffffffffffffffffffffffffffff')
        sock.sendto(magic_bytes, (ip, 54321))
        data, addr = sock.recvfrom(1024)
        
        if data:
            return True
    except Exception:
        pass
    finally:
        sock.close()
    return False

def is_xiaomi_device(mac, ip=None):
    mac = mac.upper()
    is_mac_match = mac.startswith('4C:C6:4C') or mac.startswith('64:09:80') or mac.startswith('50:D2:F5')
    
    if is_mac_match:
        return True
        
    if ip and probe_miio_port(ip):
        return True
        
    return False
