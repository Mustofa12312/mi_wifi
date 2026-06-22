from database import get_db_connection

def clean_old_records(days=30):
    """
    Deletes ping and speedtest records older than the specified number of days.
    This helps keep the SQLite database small and fast.
    """
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # SQLite date modifier: date('now', '-30 days')
        ping_del = c.execute("DELETE FROM ping_history WHERE created_at < date('now', ?)", (f"-{days} days",)).rowcount
        speed_del = c.execute("DELETE FROM speedtest_history WHERE created_at < date('now', ?)", (f"-{days} days",)).rowcount
        
        conn.commit()
        conn.close()
        
        print(f"[+] Database cleanup executed: Removed {ping_del} old ping records and {speed_del} old speedtest records.")
    except Exception as e:
        print(f"[!] Database cleanup failed: {e}")

if __name__ == '__main__':
    clean_old_records()
