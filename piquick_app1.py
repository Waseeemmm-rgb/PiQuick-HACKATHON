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
recommended_limits = {
    "pressure": (20.0, 50.0),                 # bar
    "temperature": (200.0, 300.0),           # °C
    "flow": (1.0, 100.0),                    # Kg/hour
    "vibration": (10.0, 80.0),               # Hz
    "oil_condition": (20.0, 80.0),           # index
    "chemical_concentration": (30.0, 90.0),  # %
    "energy_consumption": (25.0, 50.0),      # GJ
    "emissions": (1.0, 30.0),                # % (updated)
    "production_unit": (50.0, 500.0)         # ton/day
}

units = {
    "pressure": "bar",
    "temperature": "°C",
    "flow": "Kg/hour",
    "vibration": "Hz",
    "oil_condition": "index",
    "chemical_concentration": "%",
    "energy_consumption": "GJ",
    "emissions": "%",
    "production_unit": "ton/day"
}

ALLOWED_MIN = -1e6
ALLOWED_MAX = 1e6

# ----------------------------
# STYLES
# ----------------------------
st.markdown("""
<style>
body, .main, .block-container {
    background-color: #d7ecff;
    color: #002b5b;
}
h1 span.oq {
    color: #ff9933;
    font-weight: 700;
}
.stDataFrame th {
    background-color: #ff9933 !important;
    color: white !important;
    font-weight: bold;
}
.stDataFrame tbody tr:nth-child(even) {background-color: #f2f7ff !important;}
.stDataFrame tbody tr:hover {background-color: #ffe8cc !important;}
input[type=number] {
    border-radius: 8px;
    padding: 6px;
    font-weight: 700;
    font-size: 15px;
}
.suggestion-card {
    background-color: #ffffff;
    padding: 12px;
    border-radius: 8px;
    box-shadow: 0 0 8px rgba(0,0,0,0.08);
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# HEADER
# ----------------------------
st.markdown("<h1 style='text-align:center;'><span class='oq'>OQBI</span> Oman — PIQuick Risk Dashboard</h1>", unsafe_allow_html=True)
st.write("Monitor process parameters, detect anomalies, and visualize trends. Inputs change color (green = safe, red = out-of-range).")

# ----------------------------
# HELPERS
# ----------------------------
def classify(value, param):
    low, high = recommended_limits[param]
    if value < low:
        return "Low"
    elif value > high:
        return "High"
    else:
        return "Normal"

def emoji(value, param):
    low, high = recommended_limits[param]
    if value < low:
        return "⚠️"
    elif value > high:
        return "🔥"
    else:
        return "✅"

def color_for_risk(risk):
    if risk == "High":
        return "#e74c3c"  # red
    elif risk == "Low":
        return "#ffcc00"  # yellow
    else:
        return "#2ecc71"  # green

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
        label = f"{key.replace('_',' ').title()} ({units[key]}) — recommended {low}–{high}"
        val = st.number_input(
            label,
            value=float(default_val),
            min_value=float(ALLOWED_MIN),
            max_value=float(ALLOWED_MAX),
            step=1.0,
            key=f"{key}_{d}"
        )
        color = "#2ecc71" if (low <= val <= high) else "#e74c3c"
        st.markdown(f"""
        <style>
        div[data-testid="stNumberInput"][key="{key}_{d}"] input {{
            border: 2px solid {color} !important;
            color: {color} !important;
            font-weight: 700 !important;
        }}
        </style>
        """, unsafe_allow_html=True)
        params[key].append(val)

st.markdown("---")

# ----------------------------
# ANALYZE + COMBINED RISK TABLE
# ----------------------------
if st.button("🔍 Analyze Data"):
    df = pd.DataFrame(params)
    df.insert(0, "Day", [f"Day {i+1}" for i in range(days)])

    # Risk and emoji processing
    display_df = pd.DataFrame()
    display_df["Day"] = df["Day"]

    for param in recommended_limits.keys():
        risk_col = []
        for val in df[param]:
            r = classify(val, param)
            e = emoji(val, param)
            risk_col.append(f"{val:.1f} {units[param]} {e}")
        display_df[param.replace('_', ' ').title()] = risk_col

    # Apply background color based on risk
    def style_combined(s):
        styled = []
        for val in s:
            if isinstance(val, str):
                if "🔥" in val:
                    styled.append("background-color: #e74c3c; color:white; font-weight:700;")
                elif "⚠️" in val:
                    styled.append("background-color: #ffcc00; color:black; font-weight:700;")
                else:
                    styled.append("background-color: #2ecc71; color:white; font-weight:700;")
            else:
                styled.append("")
        return styled

    st.subheader("📊 Process Data with Risk Coloring")
    st.dataframe(display_df.style.apply(style_combined, axis=0), use_container_width=True, height=300)

    # ----------------------------
    # Suggestions
    # ----------------------------
    suggestions = []
    for d in range(days):
        for key, (low, high) in recommended_limits.items():
            val = params[key][d]
            if val < low:
                suggestions.append(f"⚠️ {key.replace('_',' ').title()} ({units[key]}) on Day {d+1} is below range ({val} < {low}) → Increase value.")
            elif val > high:
                suggestions.append(f"🔥 {key.replace('_',' ').title()} ({units[key]}) on Day {d+1} exceeds range ({val} > {high}) → Decrease value.")
    if not suggestions:
        st.markdown("<div class='suggestion-card'><b>✅ All parameters within range.</b></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='suggestion-card'><h4>💬 Suggestions</h4></div>", unsafe_allow_html=True)
        st.code("\n".join(suggestions), language="text")

    # ----------------------------
    # Trend Chart
    # ----------------------------
    st.subheader("📈 Process Parameter Trends")
    fig, ax = plt.subplots(figsize=(12, 6))
    x = [f"Day {i+1}" for i in range(days)]
    for key in recommended_limits.keys():
        ax.plot(x, df[key], marker='o', linewidth=2, label=f"{key.replace('_',' ').title()} ({units[key]})")
    ax.set_xlabel("Day")
    ax.set_ylabel("Value")
    ax.set_title("Process Parameters Over Days")
    ax.grid(alpha=0.3)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    st.pyplot(fig)
