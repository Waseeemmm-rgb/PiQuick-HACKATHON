import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="PIQuick Dashboard - OQBI Oman", layout="wide")

# ----------------------------
# PARAMETER RANGES & UNITS
# ----------------------------
# NOTE: Emissions changed to 1-30 (%) per your request
recommended_limits = {
    "pressure": (20.0, 50.0),                 # bar
    "temperature": (200.0, 300.0),           # °C
    "flow": (1.0, 100.0),                    # Kg/hour
    "vibration": (10.0, 80.0),               # Hz
    "oil_condition": (20.0, 80.0),           # index
    "chemical_concentration": (30.0, 90.0),  # %
    "energy_consumption": (25.0, 50.0),      # GJ
    "emissions": (1.0, 30.0),                # %  <-- updated
    "production_unit": (50.0, 500.0)         # ton/day
}

# Friendly units for labels
units = {
    "pressure": "bar",
    "temperature": "°C",
    "flow": "Kg/hour",
    "vibration": "Hz",
    "oil_condition": "index",
    "chemical_concentration": "%",
    "energy_consumption": "GJ",
    "emissions": "%",            # updated unit
    "production_unit": "ton/day"
}

# allow wide numeric entry range (user not blocked from exceeding recommended)
ALLOWED_MIN = -1e6
ALLOWED_MAX = 1e6

# ----------------------------
# STYLES
# ----------------------------
st.markdown(
    """
    <style>
    body, .main, .block-container { background-color: #d7ecff; color: #002b5b; }
    h1 span.oq { color: #ff9933; font-weight: 700; }
    .stDataFrame th { background-color: #ff9933 !important; color: white !important; font-weight: bold; }
    .stDataFrame tbody tr:nth-child(even) { background-color: #f2f7ff !important; }
    .stDataFrame tbody tr:hover { background-color: #ffe8cc !important; }
    input[type=number] { border-radius: 8px; padding: 6px; font-weight: 700; font-size: 15px; }
    .summary-card, .suggestion-card { background-color: #ffffff; padding: 12px; border-radius: 8px; box-shadow: 0 0 8px rgba(0,0,0,0.08); margin-top: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# HEADER
# ----------------------------
st.markdown(
    "<h1 style='text-align:center;'><span class='oq'>OQBI</span> Oman — PIQuick Risk Dashboard</h1>",
    unsafe_allow_html=True
)
st.write("Monitor process parameters, detect anomalies, and visualize ranges. Inputs change color (green = safe, red = out-of-range).")

# ----------------------------
# HELPERS
# ----------------------------
def emoji_for_value(val, param_key):
    low, high = recommended_limits[param_key]
    if val < low:
        return "⚠️"
    elif val > high:
        return "🔥"
    else:
        return "✅"

def health_status_for_value(val, param_key):
    low, high = recommended_limits[param_key]
    if val < low:
        return "Low"
    elif val > high:
        return "High"
    else:
        return "Normal"

def risk_color_css(val):
    if val == "High":
        return "background-color: #e74c3c; color: white; font-weight: bold;"
    if val == "Normal":
        return "background-color: #2ecc71; color: white; font-weight: bold;"
    return "background-color: #ffcc00; color: black; font-weight: bold;"

# ----------------------------
# INPUTS (5 days)
# ----------------------------
st.markdown("## 📝 Input Daily Process Data")
days = 5
params = {k: [] for k in recommended_limits.keys()}

for d in range(days):
    st.markdown(f"### 📅 Day {d+1}")
    for key, (low, high) in recommended_limits.items():
        default_val = (low + high) / 2.0
        label = f"{key.replace('_',' ').title()} ({units[key]}) — recommended {low}–{high} {emoji_for_value(default_val, key)}"
        # keep allowed wide range so users can still enter values outside recommended range
        val = st.number_input(
            label,
            value=float(default_val),
            min_value=float(ALLOWED_MIN),
            max_value=float(ALLOWED_MAX),
            step=1.0,
            key=f"{key}_{d}"
        )
        # color: green if within recommended, red if outside
        color = "#2ecc71" if (low <= val <= high) else "#e74c3c"
        # inject style for this specific number input (works in many Streamlit versions)
        st.markdown(
            f"""
            <style>
            div[data-testid="stNumberInput"] [data-baseweb="input"] input#{key}_{d} {{
                border: 2px solid {color} !important;
                color: {color} !important;
                font-weight: 700 !important;
            }}
            /* fallback: target by the key attribute used earlier */
            div[data-testid="stNumberInput"][key="{key}_{d}"] input {{
                border: 2px solid {color} !important;
                color: {color} !important;
                font-weight: 700 !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
        params[key].append(float(val))

st.markdown("---")

# ----------------------------
# SYSTEM HEALTH TABLE
# ----------------------------
st.markdown("## 💡 System Health Status (table)")
health_rows = []
for d in range(days):
    row = {"Day": f"Day {d+1}"}
    for key, (low, high) in recommended_limits.items():
        val = params[key][d]
        status = health_status_for_value(val, key)
        emoji = emoji_for_value(val, key)
        # include unit in column header by using title() at display stage
        row[f"{key.replace('_',' ').title()} ({units[key]})"] = f"{status} {emoji}"
    health_rows.append(row)

df_health = pd.DataFrame(health_rows)
st.dataframe(df_health, use_container_width=True, height=260)

# ----------------------------
# ANALYZE / RISK TABLE / SUGGESTIONS
# ----------------------------
if st.button("🔍 Analyze Data"):
    # numeric values dataframe
    df_values = pd.DataFrame(params)
    df_values.insert(0, "Day", [f"Day {i+1}" for i in range(days)])

    # Add risk columns (Low/Normal/High)
    for key in recommended_limits.keys():
        df_values[f"{key}_risk"] = df_values[key].apply(lambda x: health_status_for_value(x, key))

    # show raw numeric values (with units in headers)
    display_numeric = df_values.copy()
    # rename numeric columns to include units
    rename_map = {k: f"{k.replace('_',' ').title()} ({units[k]})" for k in recommended_limits.keys()}
    display_numeric = display_numeric.rename(columns=rename_map)
    display_numeric = display_numeric[["Day"] + list(rename_map.values())]
    st.subheader("📊 Numeric Inputs (values)")
    st.dataframe(display_numeric, use_container_width=True, height=260)

    # prepare risk table (only risk cols) and style them
    risk_cols = [c for c in df_values.columns if c.endswith("_risk")]
    df_risks = df_values[["Day"] + risk_cols].copy()
    # rename risk cols to user-friendly names
    df_risks.columns = ["Day"] + [f"{c.replace('_risk','').replace('_',' ').title()} Risk" for c in risk_cols]

    # color styling for risks
    def highlight_risk(s):
        return [risk_color_css(v) for v in s]

    st.subheader("🔴🟡🟢 Risk Classification (colored)")
    styled = df_risks.style.apply(lambda col: highlight_risk(col) if col.name != "Day" else [""]*len(col), axis=0)
    st.dataframe(styled, use_container_width=True, height=260)

    # Suggestions (concise, unit-aware)
    suggestions = []
    for d in range(days):
        day_label = f"Day {d+1}"
        for key, (low, high) in recommended_limits.items():
            val = params[key][d]
            if val < low:
                suggestions.append(f"⚠️ {key.replace('_',' ').title()} ({units[key]}) on {day_label} is below recommended: {val} < {low}. Suggest: increase.")
            elif val > high:
                suggestions.append(f"🔥 {key.replace('_',' ').title()} ({units[key]}) on {day_label} is above recommended: {val} > {high}. Suggest: decrease.")
    if not suggestions:
        suggestions_text = "✅ All parameters are within recommended ranges for all days."
    else:
        suggestions_text = "\n".join(suggestions)

    st.markdown("<div class='suggestion-card'><h4>💬 Suggestions</h4></div>", unsafe_allow_html=True)
    st.code(suggestions_text, language="text")

    # ----------------------------
    # Trend Chart (values plotted with units in legend)
    # ----------------------------
    st.subheader("📈 Process Parameter Trends")
    fig, ax = plt.subplots(figsize=(12, 6))
    x = [f"Day {i+1}" for i in range(days)]
    for key in recommended_limits.keys():
        ax.plot(x, df_values[key], marker='o', label=f"{key.replace('_',' ').title()} ({units[key]})", linewidth=2)
    ax.set_xlabel("Day")
    ax.set_ylabel("Value (units shown in legend)")
    ax.set_title("Process Parameters Over Days")
    ax.grid(alpha=0.3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    st.pyplot(fig)
