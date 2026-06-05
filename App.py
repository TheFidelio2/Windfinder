import streamlit as st
import pandas as pd
import requests

API_URL = "https://api-main02.meteo-services.com/rundum/"

def deg_to_compass8(deg):
    dirs = ["N","NO","O","SO","S","SW","W","NW"]
    return dirs[int((deg + 22.5) / 45) % 8]

def load_data():
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

    rows = []

    for wp in waypoints:
        try:
            r = requests.get(wp["url"], timeout=10)
            data = r.json()
        except:
            continue

        # 🔍 ggf. "data" durch "hourly" ersetzen falls nötig
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

    return df

st.title("Wind Monitoring")

df = load_data()

if len(df) == 0:
    st.write("Keine Daten")
else:
    pivot = df.pivot_table(index="Waypoint", columns="Zeit", values="Richtung", aggfunc="first")
    st.dataframe(pivot)

if st.button("Refresh"):
    st.rerun()
