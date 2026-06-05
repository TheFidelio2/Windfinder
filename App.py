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
    {"name": "P15", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.662275&lon=9.303939&elev=396"},
    {"name": "P16", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.647017&lon=9.355478&elev=396"}
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

        for entry in data.get("data", []):
            try:
                # ✅ "01n" sauber behandeln
                zeit_raw = entry.get("zeit", "0")
                zeit_clean = str(zeit_raw).replace("n", "")

                rows.append({
                    "Waypoint": wp["name"],
                    "Zeit": int(zeit_clean),
                    "wd_deg": entry.get("wd", 0),
                    "wd": deg_to_compass8(entry.get("wd", 0)),
                    "wskn": entry.get("wskn")
                })
            except:
                continue

    df = pd.DataFrame(rows)

    if len(df) > 0:
        # ✅ aktuelle Stunde
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        now_hour = now.hour

        # ✅ richtige Reihenfolge (auch über Mitternacht)
        df["Zeit_diff"] = (df["Zeit"] - now_hour + 24) % 24
        df = df.sort_values("Zeit_diff")

        # ✅ nur nächste 6 Werte pro Wegpunkt
        df = df.groupby("Waypoint").head(6)

        # ✅ echte Zeit berechnen
        df["Zeit_real"] = df["Zeit"].astype(str).str.zfill(2) + ":00"

        # ✅ Anzeige
        df["Anzeige"] = (
            df["wd"].astype(str) +
            " (" + df["wd_deg"].astype(str) + "°)" +
            " | " + df["wskn"].astype(str)
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
        index="Zeit_real",
        columns="Waypoint",
        values="Anzeige",
        aggfunc="first"
    )
    
    pivot = pivot.sort_index()
    
    pivot.index = pivot.index.strftime("%H:%M")
    
    order = ["P2","P3","P4","P5","P6","P7","P14","P15"]
    pivot = pivot.reindex(columns=order)
    
    st.dataframe(pivot, use_container_width=True)

# Refresh Button
if st.button("🔄 Aktualisieren"):
    st.rerun()
