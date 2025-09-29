# app.py
import os
import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
from data_fetcher import get_data
from utils import find_nearest_markets, get_user_location_by_ip, best_price_for_crop, normalize_price_column, haversine

# Only set page config if running as the main Streamlit page, not when embedded
if not os.environ.get("EMBEDDED_STREAMLIT"):
    st.set_page_config(page_title="Kerala Farmer Market Prices", layout="wide", initial_sidebar_state="expanded")

st.title("🌾 Kerala Farmers’ Market Price Tracker")
st.markdown("Track current market prices across Kerala markets, find the nearest market, and compare best prices for your crop.")

# --- load data (CSV or mock) ---
@st.cache_data(ttl=120)  # refresh every 2 minutes
def load_prices():
    df = get_data()
    # standardize column names
    expected = ["market", "market_lat", "market_lon", "crop", "unit", "price", "timestamp"]
    for c in expected:
        if c not in df.columns:
            df[c] = pd.NA
    df = df[expected]
    df = normalize_price_column(df, "price")
    # Drop rows with no price or crop or market
    df = df.dropna(subset=["price", "crop", "market"]).reset_index(drop=True)
    return df

df_prices = load_prices()

# --- Sidebar: filters and location ---
st.sidebar.header("Filters & Location")

# Search / filter controls
crop_list = sorted(df_prices["crop"].dropna().unique())
selected_crop = st.sidebar.selectbox("Choose crop", options=["All"] + crop_list, index=0)

markets_list = sorted(df_prices["market"].dropna().unique())
selected_market = st.sidebar.multiselect("Filter by market (optional)", options=markets_list, default=[])

min_price = float(df_prices["price"].min()) if not df_prices["price"].empty else 0.0
max_price = float(df_prices["price"].max()) if not df_prices["price"].empty else 1000.0
price_range = st.sidebar.slider("Price range", min_value=float(round(min_price,2)), max_value=float(round(max_price*1.5,2)),
                                value=(float(round(min_price,2)), float(round(max_price,2))))

st.sidebar.markdown("---")
st.sidebar.write("Get nearest markets:")
auto_detect = st.sidebar.button("Detect my approximate location (IP-based)")
manual_lat = st.sidebar.text_input("Or enter latitude (optional)", value="")
manual_lon = st.sidebar.text_input("Or enter longitude (optional)", value="")

user_location = None
if auto_detect:
    loc = get_user_location_by_ip()
    if loc:
        st.sidebar.success(f"Detected location: {loc[0]:.4f}, {loc[1]:.4f}")
        user_location = loc
    else:
        st.sidebar.error("Could not detect location automatically. Please enter coordinates or select a market.")

# If user entered manual coords:
if manual_lat.strip() and manual_lon.strip():
    try:
        user_lat = float(manual_lat.strip())
        user_lon = float(manual_lon.strip())
        user_location = (user_lat, user_lon)
        st.sidebar.success(f"Using manual location: {user_lat:.4f}, {user_lon:.4f}")
    except:
        st.sidebar.warning("Invalid manual coordinates — ignoring.")

# UI: choose a reference market as fallback
st.sidebar.markdown("Or pick your town's market:")
user_market_pick = st.sidebar.selectbox("Pick nearest market manually (optional)", options=["None"] + markets_list, index=0)
if user_market_pick != "None" and user_location is None:
    # take coordinates from data for that market (first row)
    row = df_prices[df_prices["market"] == user_market_pick].iloc[0]
    if pd.notna(row["market_lat"]) and pd.notna(row["market_lon"]):
        user_location = (float(row["market_lat"]), float(row["market_lon"]))
        st.sidebar.info(f"Using coordinates of {user_market_pick}")

# --- Filtering the main DataFrame ---
df_filtered = df_prices.copy()

if selected_crop != "All":
    df_filtered = df_filtered[df_filtered["crop"].str.lower() == selected_crop.lower()]

if selected_market:
    df_filtered = df_filtered[df_filtered["market"].isin(selected_market)]

df_filtered = df_filtered[(df_filtered["price"] >= price_range[0]) & (df_filtered["price"] <= price_range[1])]

# Show summary
col1, col2, col3 = st.columns([2,1,1])
with col1:
    st.subheader("Market Prices")
    st.write(f"Showing {len(df_filtered)} price entries.")
with col2:
    # latest timestamp info
    if "timestamp" in df_prices.columns:
        try:
            last_ts = df_prices["timestamp"].dropna().max()
            st.markdown(f"**Data timestamp:** {last_ts}")
        except:
            st.markdown("**Data timestamp:** -")
with col3:
    st.button("Refresh data")

# --- Table with all prices (sortable) ---
def format_price_df(df):
    df = df.copy()
    df["price"] = df["price"].map(lambda x: round(float(x),2))
    return df[["crop", "unit", "price", "market", "market_lat", "market_lon", "timestamp", "price"]]

st.dataframe(df_filtered.sort_values(["crop","market","price"], ascending=[True, True, False]).reset_index(drop=True), use_container_width=True)

# --- Best Price comparison for selected crop ---
st.markdown("---")
st.subheader("Best price comparison")

if selected_crop == "All":
    st.info("Select a crop in the sidebar to see best price comparisons.")
else:
    best_rows = best_price_for_crop(df_prices, selected_crop)
    if best_rows is None or best_rows.empty:
        st.warning("No data available for this crop.")
    else:
        # show best price markets and also full list for selected crop sorted descending
        st.markdown(f"**Highest current price for {selected_crop}: ₹{best_rows['price'].iloc[0]:.2f} / {best_rows['unit'].iloc[0]}**")
        st.table(best_rows[["market","price","unit","timestamp"]].drop_duplicates().reset_index(drop=True))
        st.markdown("**All market prices for this crop:**")
        crop_df = df_prices[df_prices["crop"].str.lower() == selected_crop.lower()].sort_values("price", ascending=False)
        st.dataframe(crop_df[["market","price","unit","market_lat","market_lon","timestamp"]].reset_index(drop=True), use_container_width=True)

# --- Visualization: Bar chart of prices across markets for the selected crop ---
st.markdown("---")
st.subheader("Visual comparison")

viz_col1, viz_col2 = st.columns([1,1])
with viz_col1:
    if selected_crop == "All":
        # top crops average price
        avg_by_crop = df_filtered.groupby("crop").price.mean().reset_index().sort_values("price", ascending=False)
        fig = px.bar(avg_by_crop, x="crop", y="price", title="Average price by crop (filtered)", labels={"price":"Avg Price (₹)"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        crop_df = df_prices[df_prices["crop"].str.lower() == selected_crop.lower()]
        if crop_df.empty:
            st.write("No data for selected crop.")
        else:
            fig = px.bar(crop_df.sort_values("price"), x="market", y="price", hover_data=["unit","timestamp"], title=f"{selected_crop}: Price by market", labels={"price":"Price (₹)"})
            st.plotly_chart(fig, use_container_width=True)

with viz_col2:
    # Show a price distribution
    if selected_crop == "All":
        st.write("Select a crop to see distribution.")
    else:
        crop_df = df_prices[df_prices["crop"].str.lower() == selected_crop.lower()]
        if not crop_df.empty:
            fig2 = px.box(crop_df, y="price", points="all", title=f"Price distribution for {selected_crop}")
            st.plotly_chart(fig2, use_container_width=True)

# --- Map showing markets and their price for selected crop or filtered set ---
st.markdown("---")
st.subheader("Market map")

map_df = df_filtered.copy()
# If no lat/lon available, aggregate market coords from df_prices
if "market_lat" in map_df.columns and map_df["market_lat"].notna().any():
    # For mapping, get median lat/lon per market and average price for marker size
    map_agg = map_df.groupby(["market","unit","market_lat","market_lon"], as_index=False).agg({
        "price": "mean"
    }).dropna(subset=["market_lat","market_lon"])
    if map_agg.empty:
        st.info("No geo coordinates in dataset to show map.")
    else:
        # use pydeck
        midpoint = (map_agg["market_lat"].mean(), map_agg["market_lon"].mean())
        st.write("Markets shown (size = average price). Click markers for details.")
        tooltip = {"html": "<b>{market}</b><br>Avg price: ₹{price:.2f} / {unit}", "style": {"color": "white"}}
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_agg,
            get_position=["market_lon", "market_lat"],
            get_fill_color=[255, 140, 0, 140],
            get_radius="price * 50",  # scale radius by price (tweak)
            pickable=True,
            radius_scale=1,
            radius_min_pixels=5,
            radius_max_pixels=80
        )
        view_state = pdk.ViewState(latitude=midpoint[0], longitude=midpoint[1], zoom=7, pitch=0)
        r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
        st.pydeck_chart(r)
else:
    st.info("Dataset does not include market coordinates, so map is unavailable.")

# --- Nearest Market feature ---
st.markdown("---")
st.subheader("Nearest markets to you")

if user_location is None:
    st.info("No user location provided. Use 'Detect my approximate location' or enter coordinates in the sidebar, or pick a market manually.")
else:
    user_lat, user_lon = user_location
    # prepare a markets DataFrame
    markets_df = df_prices[["market","market_lat","market_lon"]].drop_duplicates(subset=["market"])
    # drop missing coords
    markets_df = markets_df.dropna(subset=["market_lat","market_lon"])
    if markets_df.empty:
        st.warning("No market coordinates in data; cannot compute nearest markets.")
    else:
        nearest = find_nearest_markets(df_prices, user_lat, user_lon, top_n=5)
        if nearest.empty:
            st.warning("Could not compute nearby markets.")
        else:
            # Show distances
            nearest["distance_km"] = nearest["distance_km"].map(lambda x: round(float(x),2))
            st.table(nearest[["market","distance_km","market_lat","market_lon"]].reset_index(drop=True))
            # For convenience, show prices for nearest markets for the selected crop (or all)
            nearby_markets = nearest["market"].tolist()
            near_prices = df_prices[df_prices["market"].isin(nearby_markets)]
            if selected_crop != "All":
                near_prices = near_prices[near_prices["crop"].str.lower() == selected_crop.lower()]
            if near_prices.empty:
                st.info("No price entries for the selected crop in the nearby markets. Try choosing 'All' crops or a different location.")
            else:
                st.markdown("Prices in nearby markets:")
                st.dataframe(near_prices[["market","crop","price","unit","timestamp"]].sort_values(["crop","price"], ascending=[True,False]).reset_index(drop=True), use_container_width=True)

# --- Footer / tips ---
st.markdown("---")
st.caption("Notes: Data may be from a CSV snapshot or a live API (if configured). Automatic location detection is approximate (via IP). For accurate location-based results, enter GPS coordinates or select your market manually.")
st.markdown("**How to use:** Use the sidebar to select a crop, apply market filters or price ranges, detect your location, and compare prices across markets. The system will highlight the highest price for a selected crop and show a table + map for easy comparison.")
