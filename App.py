import streamlit as st
import pandas as pd
import requests

API_URL = "https://api-main02.meteo-services.com/rundum/"

def deg_to_compass8(deg):
    dirs = ["N","NO","O","SO","S","SW","W","NW"]
    return dirs[int((deg + 22.5) / 45) % 8]

def load_data():
    try:
        r = requests.get(API_URL, timeout=10)
        data = r.json()
    except:
        return pd.DataFrame()

    rows = []

    for wp in waypoints:
        try:
            r = requests.get(wp["url"], timeout=10)
            data = r.json()
        except:
            continue

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
    def color_wind(val):
    colors = {
        "N": "#4A90E2",   # blau
        "NO": "#50E3C2",  # türkis
        "O": "#F5A623",   # orange
        "SO": "#F8E71C",  # gelb
        "S": "#D0021B",   # rot
        "SW": "#8B572A",  # braun
        "W": "#7ED321",   # grün
        "NW": "#9013FE"   # lila
    }
    return f"background-color: {colors.get(val, 'white')}"
    st.dataframe(
    pivot.style.applymap(color_wind),
    use_container_width=True
)

if st.button("Refresh"):
    st.rerun()
