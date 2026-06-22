import subprocess
import re
import time

def start_dns_sniffer(interface="any"):
    """
    Passively listens to DNS requests (port 53) using tcpdump.
    Requires tcpdump to be installed and run with sudo.
    """
    print("[*] Starting DNS Observatory Sniffer...")
    
    # We will maintain a simple memory cache of top domains
    top_domains = {}
    
    try:
        # Run tcpdump in line-buffered mode
        process = subprocess.Popen(
            ['tcpdump', '-l', '-n', '-i', interface, 'udp port 53'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        
        # Regex to parse: "192.168.1.5.53421 > 8.8.8.8.53: 1234+ A? google.com. (28)"
        dns_pattern = re.compile(r'A\?\s+([a-zA-Z0-9.-]+)\.?\s+\(')
        
        print("[+] DNS Sniffer is running. Monitoring traffic...")
        
        for line in iter(process.stdout.readline, ''):
            match = dns_pattern.search(line)
            if match:
                domain = match.group(1).rstrip('.')
                # Count occurrences
                if domain in top_domains:
                    top_domains[domain] += 1
                else:
                    top_domains[domain] = 1
                    
                # Optionally print or store it
                # For MVP, we just print the top domains every 10 hits
                total_hits = sum(top_domains.values())
                if total_hits % 20 == 0:
                    sorted_domains = sorted(top_domains.items(), key=lambda item: item[1], reverse=True)[:5]
                    print(f"\n--- [DNS OBSERVATORY] Top 5 Domains Requested ---")
                    for d, count in sorted_domains:
                        print(f"  {count}x : {d}")
                    print("-------------------------------------------------")
                    
    except FileNotFoundError:
        print("[!] tcpdump not found. DNS Observatory cannot start.")
    except PermissionError:
        print("[!] Sudo/root required to run DNS Observatory (tcpdump).")
    except Exception as e:
        print(f"[!] DNS Sniffer Error: {e}")

if __name__ == '__main__':
    start_dns_sniffer()
