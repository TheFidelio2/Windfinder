import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# ---------------- Einstellungen ----------------

waypoints = [
    {"name": "P2", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.537213&lon=9.617470&elev=396"},
    {"name": "P3", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.553687&lon=9.529387&elev=396"},
    {"name": "P4", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.568882&lon=9.398480&elev=396"},
    {"name": "P5", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.601061&lon=9.355469&elev=396"},
    {"name": "P6", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.630091&lon=9.292966&elev=396"},
    {"name": "P7", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.664314&lon=9.225897&elev=396"},
    {"name": "P14", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.686153&lon=9.257889&elev=396"},
    {"name": "P15", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.662275&lon=9.303939&elev=396"}
]

# ---------------- Funktionen ----------------

def deg_to_compass8(deg):
    dirs = ["N","NO","O","SO","S","SW","W","NW"]
    return dirs[int((deg + 22.5) / 45) % 8]

def load_data():
    rows = []

    for wp in waypoints:
        try:
            r = requests.get(wp["url"], timeout=10)
            data = r.json()
        except:
            continue

        # ggf. "data" durch "hourly" ersetzen
        for entry in data.get("data", []):
            rows.append({
                "Waypoint": wp["name"],
                "Zeit": entry.get("time"),
                "Richtung": deg_to_compass8(entry.get("wind_direction", 0)),
                "Wind": entry.get("wind_speed")
            })

    df = pd.DataFrame(rows)

    if len(df) > 0:
        df["Zeit"] = pd.to_datetime(df["Zeit"])

        # ✅ Filter: jetzt + 6 Stunden
        now = datetime.now()
        limit = now + timedelta(hours=6)
        df = df[(df["Zeit"] >= now) & (df["Zeit"] <= limit)]

    return df

def color_wind(val):
    colors = {
        "N": "#4A90E2",
        "NO": "#50E3C2",
        "O": "#F5A623",
        "SO": "#F8E71C",
        "S": "#D0021B",
        "SW": "#8B572A",
        "W": "#7ED321",
        "NW": "#9013FE"
    }
    return "background-color: " + colors.get(val, "white")

# ---------------- UI ----------------

st.set_page_config(layout="wide")
st.title("🌬️ Wind Live Monitoring")

df = load_data()

if len(df) == 0:
    st.write("Keine Daten")
else:
    pivot = df.pivot_table(
        index="Waypoint",
        columns="Zeit",
        values="Richtung",
        aggfunc="first"
    )

    # ✅ schönere Zeitanzeige
    pivot.columns = pivot.columns.strftime("%H:%M")

    st.dataframe(
        pivot.style.applymap(color_wind),
        use_container_width=True
    )

# Refresh Button
if st.button("🔄 Aktualisieren"):
    st.rerun()
