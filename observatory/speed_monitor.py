import time
import speedtest
from database import add_speedtest_record

def run_speedtest():
    print("[*] Running Internet Speedtest... (This may take a minute)")
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_bps = st.download()
        upload_bps = st.upload()
        ping_ms = st.results.ping
        
        # Convert to Mbps
        download_mbps = download_bps / 10**6
        upload_mbps = upload_bps / 10**6
        
        print(f"[+] Speedtest Result: Ping: {ping_ms:.1f} ms | DL: {download_mbps:.1f} Mbps | UL: {upload_mbps:.1f} Mbps")
        add_speedtest_record(download_mbps, upload_mbps, ping_ms)
        
    except Exception as e:
        print(f"[!] Speedtest Error: {e}")

def run_speed_monitor_loop(interval_hours=1):
    while True:
        run_speedtest()
        # Sleep for interval
        time.sleep(interval_hours * 3600)

if __name__ == '__main__':
    run_speedtest()
