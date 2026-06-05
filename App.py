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

        # ✅ Anzeige
        df["Zeit_real"] = df["day"] + " " + df["Zeit"].astype(str).str.zfill(2) + ":00"

        df["Richtung"] = df["wd"].astype(str) + " (" + df["wd_deg"].astype(str) + "°)"
        df["Wind"] = df["wskn"]
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
    pivot_wind = df.pivot_table(
        index="Zeit_real",
        columns="Waypoint",
        values="Wind",
        aggfunc="first"
    )

    pivot_wind = df.pivot_table(
        index="Zeit_real",
        columns="Waypoint",
        values="Wind",
        aggfunc="first"
    )
    
    # ✅ Sortierung der Spalten nach P-Nummer
    def sort_key(col):
        return int(col.split()[0].replace("P", ""))

    sorted_cols = sorted(pivot.columns.levels[1], key=sort_key)

    pivot = pivot.reindex(columns=sorted_cols, level=1)

    #pivot = pivot.reindex(sorted(pivot.columns, key=sort_key), axis=1)
    pivot_diff = pivot_diff.reindex(pivot.columns, axis=1)
    pivot_diff = pivot_diff.reindex(index=pivot.index, columns=pivot.columns)

    # ✅ Highlight Funktion
    def highlight(row):
        styles = []
        for col in pivot.columns:
            try:
                diff = pivot_diff.loc[row.name, col]
            except:
                diff = None
    
            # Windgeschwindigkeit aus Text extrahieren
            try:
                val = row[col]
                speed = float(val.split("|")[1].strip())
            except:
                speed = None
    
            # Priorität: Richtungsänderung > Geschwindigkeit
            if pd.notna(diff) and diff > 40:
                styles.append("background-color: #ff0000")  # stark rot
            elif pd.notna(diff) and diff > 20:
                styles.append("background-color: #ff9999")  # hellrot
            elif speed is not None and speed >= 4:
                styles.append("background-color: orange")   # stark wind
            elif speed is not None and speed >= 2:
                styles.append("background-color: yellow")   # mittel wind
            else:
                styles.append("")
        return styles

    
    styled = pivot.style.apply(highlight, axis=1)

    st.dataframe(styled, use_container_width=True)

# Refresh Button
if st.button("🔄 Aktualisieren"):
    st.rerun()
