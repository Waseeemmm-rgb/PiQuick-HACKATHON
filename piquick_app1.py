import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# Page Setup
# ----------------------------
st.set_page_config(
    page_title="PIQuick Dashboard - OQBI Oman",
    layout="wide",
)

# ----------------------------
# Recommended parameter ranges (for display & scoring)
# ----------------------------
recommended_limits = {
    "pressure": (20.0, 50.0),                 # bar
    "temperature": (200.0, 300.0),           # °C
    "flow": (1.0, 100.0),                    # Kg/hour (recommended)
    "vibration": (10.0, 80.0),               # Hz
    "oil_condition": (20.0, 80.0),           # index
    "chemical_concentration": (30.0, 90.0),  # %
    "energy_consumption": (25.0, 50.0),      # GJ
    "emissions": (1.0, 100.0),               # ppm
    "production_unit": (50.0, 500.0)         # ton/day
}

# To avoid blocking user from entering larger/smaller values,
# we set the actual allowed min/max quite wide but we show the recommended range in label.
ALLOWED_MIN = -1e6
ALLOWED_MAX = 1e6

# ----------------------------
# Styles / CSS
# ----------------------------
st.markdown(
    """
    <style>
    body, .main, .block-container { background-color: #d0e7f9; color: #003366; }
    .summary-card, .suggestion-card { background-color: #ffffff; padding: 12px; border-radius: 8px; }
    h1 span.oq { color: #ffb366; font-weight: 700; } /* OQ in orange and bold */
    .risk-high { background-color: #ff4d4d !important; color: white !important; font-weight: bold; }
    .risk-normal { background-color: #28a745 !important; color: white !important; font-weight: bold; }
    .risk-low { background-color: #ffcc00 !important; color: black !important; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Header (OQBI orange + bold)
# ----------------------------
st.markdown(
    "<h1 style='text-align:center;'><span class='oq'>OQBI</span> Oman - PIQuick Risk Dashboard</h1>",
    unsafe_allow_html=True,
)
st.write("Monitor daily process parameters, detect anomalies, and get quick suggestions.")

# ----------------------------
# Helper functions
# ----------------------------
def emoji_for_value(val, param_key):
    low, high = recommended_limits[param_key]
    if val < low:
        return "⚠️"   # below recommended -> caution (low)
    elif val > high:
        return "🔥"   # above recommended -> danger (high)
    else:
        return "✅"   # within recommended -> normal

def health_status_for_value(val, param_key):
    low, high = recommended_limits[param_key]
    if val < low:
        return "Low"
    elif val > high:
        return "High"
    else:
        return "Normal"

def risk_color_css(val):
    # used for styling risk cells
    if val == "High":
        return "background-color: #ff4d4d; color: white; font-weight: bold;"
    if val == "Normal":
        return "background-color: #28a745; color: white; font-weight: bold;"
    return "background-color: #ffcc00; color: black; font-weight: bold;"

# ----------------------------
# Inputs: collect numeric values for N days
# ----------------------------
st.markdown("<h3>📝 Input Daily Process Data (5 Days)</h3>", unsafe_allow_html=True)
days = 5

# initialize storage for inputs
params = {
    "pressure": [],
    "temperature": [],
    "flow": [],
    "vibration": [],
    "oil_condition": [],
    "chemical_concentration": [],
    "energy_consumption": [],
    "emissions": [],
    "production_unit": []
}

# build inputs day by day
for d in range(days):
    st.markdown(f"### Day {d+1}")
    # loop through recommended_limits keys to keep an order
    for key in recommended_limits.keys():
        rec_min, rec_max = recommended_limits[key]
        # default set to middle of recommended range
        default = float((rec_min + rec_max) / 2.0)
        label = f"{key.replace('_',' ').title()} (recommended {rec_min}–{rec_max}) • max shown: {rec_max} {emoji_for_value(default,key)} — Day {d+1}"
        # Use wide allowed range to not prevent entering values beyond recommended
        val = st.number_input(label, value=default, min_value=float(ALLOWED_MIN), max_value=float(ALLOWED_MAX), step=1.0, key=f"{key}_{d}")
        params[key].append(float(val))

st.markdown("---")

# ----------------------------
# System Health Status table (show statuses per day, tabular)
# ----------------------------
st.markdown("<h3>💡 System Health Status (table)</h3>", unsafe_allow_html=True)
health_rows = []
for d in range(days):
    row = {"Day": f"Day {d+1}"}
    for key in recommended_limits.keys():
        val = params[key][d]
        status = health_status_for_value(val, key)
        emoji = emoji_for_value(val, key)
        row[key.replace("_"," ").title()] = f"{status} {emoji}"
    health_rows.append(row)

df_health = pd.DataFrame(health_rows)
st.dataframe(df_health, height=200)

# ----------------------------
# Analyze / Risk classification + colored table + suggestions
# ----------------------------
if st.button("Analyze Data"):
    # raw numeric dataframe
    df_values = pd.DataFrame(params)
    df_values.insert(0, "Day", [f"Day {i+1}" for i in range(days)])

    # compute risk columns (Low / Normal / High)
    for key in recommended_limits.keys():
        risk_col = key + "_risk"
        df_values[risk_col] = df_values[key].apply(lambda x: health_status_for_value(x, key))

    # show colored risk columns with pandas Styler
    risk_cols = [c for c in df_values.columns if c.endswith("_risk")]

    st.subheader("📊 Process Data & Risk Levels (values + risk cols)")

    # First show raw numeric values
    st.markdown("**Numeric values (raw inputs)**")
    st.dataframe(df_values[[c for c in df_values.columns if not c.endswith("_risk")]], height=250)

    # Then show risk table with color styling
    st.markdown("**Risk classification (colored)**")
    def apply_risk_styles(s):
        return [risk_color_css(v) for v in s]

    styled = df_values.style.apply(lambda col: apply_risk_styles(col) if col.name.endswith("_risk") else [""]*len(col), axis=0)
    st.dataframe(styled, height=300)

    # ----------------------------
    # Suggestions: produce concise per-day actionable suggestions
    # ----------------------------
    suggestions = []
    for d in range(days):
        day_label = f"Day {d+1}"
        for key in recommended_limits.keys():
            val = params[key][d]
            rec_min, rec_max = recommended_limits[key]
            if val < rec_min:
                suggestions.append(f"⚠️ {key.replace('_',' ').title()} on {day_label} is below recommended ({val} < {rec_min}). Suggest: increase.")
            elif val > rec_max:
                suggestions.append(f"🔥 {key.replace('_',' ').title()} on {day_label} is above recommended ({val} > {rec_max}). Suggest: decrease.")

    if not suggestions:
        suggestions_text = "✅ All parameters are within recommended ranges for all days."
    else:
        suggestions_text = "\n".join(suggestions)

    st.markdown("<div class='suggestion-card'><h4>Suggestions</h4>", unsafe_allow_html=True)
    st.code(suggestions_text)
    st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------
    # Trend Chart for numeric values
    # ----------------------------
    st.subheader("📈 Process Parameter Trends")
    fig, ax = plt.subplots(figsize=(12,6))
    x = [f"Day {i+1}" for i in range(days)]
    for key in recommended_limits.keys():
        ax.plot(x, df_values[key], marker='o', label=key.replace("_"," ").title(), linewidth=2)
    ax.set_title("Process Parameter Trends", fontsize=16, color="#ffb366")
    ax.set_xlabel("Day")
    ax.set_ylabel("Value")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    st.pyplot(fig)
