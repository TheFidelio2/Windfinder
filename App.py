import streamlit as st import pandas as pd import requests
API_URL = "https://api-main02.meteo-services.com/rundum/"
def deg_to_compass8(deg): directions = ["N", "NO", "O", "SO", "S", "SW", "W", "NW"] idx = int((deg + 22.5) / 45) % 8 return directions[idx]
@st.cache_data(ttl=300) def load_data(): try: r = requests.get(API_URL, timeout=10) r.raise_for_status() data = r.json() except Exception as e: st.error(f"Fehler beim Laden der API: {e}") return pd.DataFrame()
records = []

for wp in data.get("waypoints", []):
    for m in wp.get("measurements", []):
        records.append({
            "Waypoint": wp.get("name"),
            "Zeit": m.get("timestamp"),
            "Richtung (°)": m.get("direction"),
            "Wind (m/s)": m.get("speed"),
            "Richtung": deg_to_compass8(m.get("direction", 0))
        })

df = pd.DataFrame(records)

if not df.empty:
    df["Zeit"] = pd.to_datetime(df["Zeit"])
    df = df.sort_values(["Zeit", "Waypoint"])

return df
st.set_page_config(layout="wide") st.title("Wind Live Monitoring")
df = load_data()
if df.empty: st.warning("Keine Daten verfügbar") else: pivot = df.pivot(index="Waypoint", columns="Zeit", values="Richtung") st.dataframe(pivot, use_container_width=True)
if st.checkbox("Rohdaten anzeigen"):
    st.dataframe(df, use_container_width=True)
if st.button("Aktualisieren"): st.cache_data.clear() st.rerun()
