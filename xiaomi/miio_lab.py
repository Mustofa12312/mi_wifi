from miio.discovery import discover
import logging

# Suppress verbose miio logs
logging.getLogger("miio").setLevel(logging.CRITICAL)

def discover_miio_devices():
    """
    Scans the local network for MiIO devices and returns their details.
    """
    devices = []
    try:
        # Discover devices on the local network
        found_devices = discover()
        for ip, dev in found_devices.items():
            devices.append({
                "ip": ip,
                "token": dev.token.hex() if dev.token else "N/A",
                "product": dev.product,
                "mac": dev.mac
            })
    except Exception as e:
        print(f"[!] MiIO Discovery Error: {e}")
        
    return devices
