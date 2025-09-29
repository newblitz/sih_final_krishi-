# data_fetcher.py
import os
import pandas as pd
import numpy as np
import requests
from datetime import datetime

SAMPLE_CSV_PATH = os.path.join("sample_data", "kerala_mandi.csv")

def generate_mock_data():
    """Return a mock DataFrame for Kerala mandi markets with lat/lon and prices."""
    markets = [
        ("Kozhikode Market", 11.2588, 75.7804),
        ("Kochi Market", 9.9312, 76.2673),
        ("Thiruvananthapuram Market", 8.5241, 76.9366),
        ("Thrissur Market", 10.5276, 76.2144),
        ("Alappuzha Market", 9.4981, 76.3388),
        ("Kannur Market", 11.8745, 75.3704),
        ("Palakkad Market", 10.7867, 76.6548),
        ("Kollam Market", 8.8932, 76.6141)
    ]
    crops = [
        ("Onion", "kg"),
        ("Tomato", "kg"),
        ("Potato", "kg"),
        ("Coconut", "count"),
        ("Banana", "dozen"),
        ("Chilly", "kg"),
        ("Turmeric", "kg"),
        ("Green Gram", "kg"),
    ]

    rows = []
    t = datetime.utcnow().isoformat()
    rng = np.random.default_rng(seed=42)
    for m_name, lat, lon in markets:
        for crop, unit in crops:
            # price variation by market & crop
            base = {
                "Onion": 20, "Tomato": 25, "Potato": 18, "Coconut": 28,
                "Banana": 60, "Chilly": 120, "Turmeric": 200, "Green Gram": 110
            }.get(crop, 50)
            # add rng noise
            price = round(base * rng.uniform(0.8, 1.3), 2)
            rows.append({
                "market": m_name,
                "market_lat": lat + rng.normal(0, 0.01),
                "market_lon": lon + rng.normal(0, 0.01),
                "crop": crop,
                "unit": unit,
                "price": price,
                "timestamp": t
            })

    df = pd.DataFrame(rows)
    return df

def load_csv(csv_path=SAMPLE_CSV_PATH):
    """Load CSV if present and compatible. Return DataFrame or None."""
    if not os.path.exists(csv_path):
        return None
    try:
        df = pd.read_csv(csv_path)
        # Expecting columns: market, market_lat, market_lon, crop, unit, price, timestamp
        required = {"market", "crop", "unit", "price"}
        if not required.issubset(set(df.columns)):
            return None
        # if lat/lon missing, attempt to fill NA with None
        if "market_lat" not in df.columns or "market_lon" not in df.columns:
            df["market_lat"] = pd.NA
            df["market_lon"] = pd.NA
        return df
    except Exception as e:
        print("Failed to load CSV:", e)
        return None

def fetch_live_from_api(api_url, params=None, headers=None, timeout=10):
    """Optional: fetch data from external API that returns JSON list of rows matching the schema."""
    try:
        resp = requests.get(api_url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print("API fetch failed:", e)
        return None

def get_data(csv_path=SAMPLE_CSV_PATH, live_api=None):
    """
    Returns a DataFrame with the needed columns:
    market, market_lat, market_lon, crop, unit, price, timestamp
    """
    # 1) try live API if provided
    if live_api:
        df_api = fetch_live_from_api(live_api)
        if df_api is not None and not df_api.empty:
            return df_api

    # 2) try CSV
    df_csv = load_csv(csv_path)
    if df_csv is not None:
        return df_csv

    # 3) fallback: generate mock dataset
    return generate_mock_data()
