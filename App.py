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

    for wp in data.get("waypoints", []):
        for m in wp.get("measurements", []):
            rows.append({
                "Waypoint": wp.get("name"),
                "Zeit": m.get("timestamp"),
                "Richtung": deg_to_compass8(m.get("direction", 0)),
                "Wind": m.get("speed")
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
    pivot = df.pivot(index="Waypoint", columns="Zeit", values="Richtung")
    st.dataframe(pivot)

if st.button("Refresh"):
    st.rerun()
