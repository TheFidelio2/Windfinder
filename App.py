import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# ---------------- Wegpunkte ----------------

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
            st.write(data.get("data", [])[:3])
        except:
            continue

        # API liefert Dictionary → values() verwenden
        for entry in data.get("data", []):
            try:
                rows.append({
                    "Waypoint": wp["name"],
                    "Zeit": int(entry.get("zeit", 0)),
                    "TMP": entry.get("TMP"),
                    "wd": deg_to_compass8(entry.get("wd", 0)),
                    "wskn": entry.get("wskn"),
                    "Tfeel": entry.get("Tfeel")
                })
            except:
                continue
    df = pd.DataFrame(rows)

    if len(df) > 0:
        now_hour = datetime.now().hour
        limit = now_hour + 6

        # ✅ Zeitfilter
        now_hour = datetime.now().hour
        df["Zeit_diff"] = (df["Zeit"] - now_hour + 24) % 24
        df = df[df["Zeit_diff"] <= 6]
        # ✅ Anzeige kombinieren
        df["Anzeige"] = (
            "T:" + df["TMP"].astype(str) +
            " | W:" + df["wd"].astype(str) +
            " | v:" + df["wskn"].astype(str) +
            " | F:" + df["Tfeel"].astype(str)
        )

    return df

# ---------------- UI ----------------

st.set_page_config(layout="wide")
st.title("🌬️ Wind Live Monitoring")

df = load_data()

if len(df) == 0:
    st.write("Keine Daten")
else:
    pivot = df.pivot_table(
        index="Zeit",
        columns="Waypoint",
        values="Anzeige",
        aggfunc="first"
    )

    pivot = pivot.sort_index()

    st.dataframe(pivot, use_container_width=True)

# Refresh Button
if st.button("🔄 Aktualisieren"):
    st.rerun()
