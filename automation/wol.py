import socket
import re

def send_magic_packet(mac_address):
    """
    Sends a Wake-on-LAN magic packet to the specified MAC address.
    """
    # Clean the MAC address
    mac_clean = re.sub(r'[^0-9a-fA-F]', '', mac_address)
    
    if len(mac_clean) != 12:
        return False, "Invalid MAC address format"
        
    try:
        # Create the magic packet: 6 bytes of 0xFF followed by 16 repetitions of the target MAC
        data = bytes.fromhex('FF' * 6 + mac_clean * 16)
        
        # Send broadcast UDP packet to port 9
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(data, ('255.255.255.255', 9))
        sock.close()
        
        return True, "Magic packet sent successfully"
    except Exception as e:
        return False, str(e)
