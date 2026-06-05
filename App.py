import streamlit as st
import pandas as pd
import requests

# ---------------- Wegpunkte ----------------

waypoints = [
    {"name": "P2 Lindau", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.537213&lon=9.617470&elev=396"},
    {"name": "P3 Rheinmündung", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.553687&lon=9.529387&elev=396"},
    {"name": "P4 Romanshorn", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.568882&lon=9.398480&elev=396"},
    {"name": "P5 Kesswill", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.601061&lon=9.355469&elev=396"},
    {"name": "P6 Altnau", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.630091&lon=9.292966&elev=396"},
    {"name": "P7 Konstanz", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.664314&lon=9.225897&elev=396"},
    {"name": "P14 Meersburg", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.686153&lon=9.257889&elev=396"},
    {"name": "P15", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.662275&lon=9.303939&elev=396"},
    {"name": "P16 Immenstad", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.647017&lon=9.355478&elev=396"},
    {"name": "P17 Friedrichshafen", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.634182&lon=9.436297&elev=396"},
    {"name": "P18 Langenargen", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.584788&lon=9.524766&elev=396"},
    {"name": "P19 Wasserburg", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.559905&lon=9.590836&elev=396"},
    {"name": "P20 Lindau", "url": "https://api-main02.meteo-services.com/rundum/wind-ICOND2-02.php?lat=47.5418&lon=9.671614&elev=396"},
]

# ---------------- Funktionen ----------------

def deg_to_compass8(deg):
    dirs = ["N","NO","O","SO","S","SW","W","NW"]
    return dirs[int((deg + 22.5) / 45) % 8]

# ✅ Winkel-Differenz korrekt (360° berücksichtigt)
def calc_diff(series):
    diffs = []
    prev = None
    for val in series:
        if prev is None:
            diffs.append(None)
        else:
            d = abs(val - prev)
            diffs.append(min(d, 360 - d))
        prev = val
    return diffs

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
                zeit_raw = entry.get("zeit", "0")
                zeit_clean = str(zeit_raw).replace("n", "")

                rows.append({
                    "Waypoint": wp["name"],
                    "day": entry.get("day"),
                    "Zeit": int(zeit_clean),
                    "wd_deg": entry.get("wd", 0),
                    "wd": deg_to_compass8(entry.get("wd", 0)),
                    "wskn": entry.get("wskn")
                })
            except:
                continue

    df = pd.DataFrame(rows)

    if len(df) > 0:

        # ✅ Zeitraum
        df = df[
            ((df["day"] == "Fri") & (df["Zeit"] >= 16)) |
            ((df["day"] == "Sat") & (df["Zeit"] <= 16))
        ]

        # ✅ Sortierung
        day_order = {"Fri": 0, "Sat": 1}
        df["day_num"] = df["day"].map(day_order)
        df = df.sort_values(["Waypoint", "day_num", "Zeit"])

        # ✅ Differenz berechnen
        df["wd_diff"] = df.groupby("Waypoint")["wd_deg"].transform(calc_diff)
        df["wskn_diff"] = df.groupby("Waypoint")["wskn"].diff()

        # ✅ Anzeige
        df["Zeit_real"] = df["day"] + " " + df["Zeit"].astype(str).str.zfill(2) + ":00"

        df["Richtung"] = df["wd"].astype(str) + " (" + df["wd_deg"].astype(str) + "°)"
        df["Wind"] = df["wskn"]
        

    return df

# ---------------- UI ----------------

st.set_page_config(layout="wide")
st.title("🌬️ Wind Live Monitoring")

df = load_data()

if len(df) == 0:
    st.write("Keine Daten")
else:
    
    pivot_dir = df.pivot_table(
        index="Zeit_real",
        columns="Waypoint",
        values="Richtung",
        aggfunc="first"
    )
    
    pivot_wind = df.pivot_table(
        index="Zeit_real",
        columns="Waypoint",
        values="Wind",
        aggfunc="first"
    )

    pivot_diff = df.pivot_table(
        index="Zeit_real",
        columns="Waypoint",
        values="wd_diff",
        aggfunc="first"
    )

    pivot_wind_diff = df.pivot_table(
        index="Zeit_real",
        columns="Waypoint",
        values="wskn_diff",
        aggfunc="first"
    )

    # ✅ Sortierung nach P-Nummer
    def sort_key(col):
        return int(col.split()[0].replace("P", ""))

    sorted_cols = sorted(pivot_dir.columns, key=sort_key)

    pivot_dir = pivot_dir.reindex(columns=sorted_cols)
    pivot_wind = pivot_wind.reindex(columns=sorted_cols)
    pivot_diff = pivot_diff.reindex_like(pivot_wind)
    pivot_wind_diff = pivot_wind_diff.reindex_like(pivot_wind)
    pivot_wind_diff = pivot_wind_diff.reindex(index=pivot_wind.index, columns=pivot_wind.columns)

    # ✅ Highlight Funktion (nur für Wind)
    def highlight(row):
        styles = []
        for col in pivot_wind.columns:
            
            # Werte holen
            diff_dir = pivot_diff.loc[row.name, col] if row.name in pivot_diff.index and col in pivot_diff.columns else None
            diff_wind = pivot_wind_diff.loc[row.name, col] if row.name in pivot_wind_diff.index and col in pivot_wind_diff.columns else None
            speed = row[col]
    
            # PRIORITÄT: Richtung > Windänderung > absolute Geschwindigkeit
    
            # 🔴 Richtungsänderung
            if pd.notna(diff_dir) and diff_dir > 20:
                styles.append("background-color: #ff0000")
            
            elif pd.notna(diff_dir) and diff_dir > 10:
                styles.append("background-color: #ff9999")
    
            # 🟢 Zunahme Wind
            elif pd.notna(diff_wind) and diff_wind >= 4:
                styles.append("background-color: #00cc44")  # stark grün
            
            elif pd.notna(diff_wind) and diff_wind >= 2:
                styles.append("background-color: #99ff99")  # hellgrün
    
            # 🔵 Abnahme Wind
            elif pd.notna(diff_wind) and diff_wind <= -4:
                styles.append("background-color: #3399ff")  # blau
            
            elif pd.notna(diff_wind) and diff_wind <= -2:
                styles.append("background-color: #cce5ff")  # hellblau
    
            
            else:
                styles.append("")
    
        return styles
    
    styled_wind = pivot_wind.style.apply(highlight, axis=1)

    st.subheader("🧭 Richtung")
    st.dataframe(pivot_dir, use_container_width=True)

    st.subheader("🌬️ Wind")
    st.dataframe(styled_wind, use_container_width=True)
    
# Refresh Button
if st.button("🔄 Aktualisieren"):
    st.rerun()
