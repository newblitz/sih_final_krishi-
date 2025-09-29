# utils.py
import math
import pandas as pd
import requests

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate great circle distance between two points in kilometers.
    """
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def find_nearest_markets(df_markets, user_lat, user_lon, top_n=5):
    """
    df_markets must have columns market, market_lat, market_lon.
    Returns DataFrame with extra 'distance_km' column sorted ascending.
    """
    df = df_markets.copy()
    # If lat/lon missing, return empty
    if df["market_lat"].isna().all() or df["market_lon"].isna().all():
        return pd.DataFrame()
    df["distance_km"] = df.apply(
        lambda row: haversine(user_lat, user_lon, float(row["market_lat"]), float(row["market_lon"])), axis=1
    )
    # aggregate unique markets and their lat/lon (take first)
    df_markets_unique = df[["market", "market_lat", "market_lon", "distance_km"]].drop_duplicates(subset=["market"])
    return df_markets_unique.sort_values("distance_km").head(top_n)

def get_user_location_by_ip():
    """
    Attempt to get approximate user location via public IP geolocation.
    Uses ipinfo.io as a simple free endpoint; this may be rate-limited.
    Returns (lat, lon) or None.
    """
    try:
        resp = requests.get("https://ipinfo.io/json", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if "loc" in data:
            lat_str, lon_str = data["loc"].split(",")
            return float(lat_str), float(lon_str)
    except Exception as e:
        print("IP geolocation failed:", e)
    return None

def best_price_for_crop(df_prices, crop):
    """
    Returns best (highest) price row(s) for crop across markets.
    """
    crop_df = df_prices[df_prices["crop"].str.lower() == crop.lower()]
    if crop_df.empty:
        return None
    max_price = crop_df["price"].max()
    best_rows = crop_df[crop_df["price"] == max_price]
    return best_rows.sort_values("market")

def normalize_price_column(df, price_col="price"):
    df = df.copy()
    df[price_col] = pd.to_numeric(df[price_col], errors="coerce")
    return df
