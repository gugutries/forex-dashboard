import httpx, sqlite3, time
import pandas as pd

DB_FILE = "forex_rates.db"

def fetch_usd_inr_rate():
    url = "https://open.er-api.com/v6/latest/USD"
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    usd_to_inr = data["rates"]["INR"]
    inr_to_usd = round(1 / usd_to_inr, 6)
    updated_time = data["time_last_update_utc"]
    return usd_to_inr, inr_to_usd, updated_time

def store_rates(usd_inr, inr_usd):
    ts = time.time()
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS forex_rates (
                timestamp REAL,
                usd_to_inr REAL,
                inr_to_usd REAL
            )
        """)
        conn.execute("INSERT INTO forex_rates VALUES (?, ?, ?)", (ts, usd_inr, inr_usd))
        conn.commit()

def get_last_forex_rates(n=30):
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql("SELECT * FROM forex_rates ORDER BY timestamp DESC LIMIT ?",
                         conn, params=(n,))
        df = df.sort_values("timestamp")
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        return df

