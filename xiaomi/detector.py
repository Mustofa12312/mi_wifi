import socket

def is_xiaomi_device(mac, ip=None):
    mac = mac.upper()
    is_mac_match = mac.startswith('4C:C6:4C') or mac.startswith('64:09:80') or mac.startswith('50:D2:F5')
    
    if not is_mac_match:
        return False
        
    # If MAC matches, we can optionally check for MiIO open ports (54321) to confirm
    # This is for v2.0 features
    if ip:
        # We could add an active probe here
        pass
        
    return True
