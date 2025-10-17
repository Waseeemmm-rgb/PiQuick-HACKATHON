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
# Recommended parameter ranges
# ----------------------------
recommended_limits = {
    "pressure": (20.0, 50.0),
    "temperature": (200.0, 300.0),
    "flow": (1.0, 100.0),
    "vibration": (10.0, 80.0),
    "oil_condition": (20.0, 80.0),
    "chemical_concentration": (30.0, 90.0),
    "energy_consumption": (25.0, 50.0),
    "emissions": (1.0, 100.0),
    "production_unit": (50.0, 500.0)
}

ALLOWED_MIN = -1e6
ALLOWED_MAX = 1e6

# ----------------------------
# CSS STYLING
# ----------------------------
st.markdown(
    """
    <style>
    body, .main, .block-container { background-color: #d0e7f9; color: #003366; }
    h1 span.oq { color: #ffb366; font-weight: 700; }
    .summary-card, .suggestion-card {
        background-color: #ffffff;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 0 8px rgba(0,0,0,0.1);
        margin-top: 10px;
    }
    .stDataFrame table {
        border-collapse: collapse !important;
        border-radius: 10px !important;
        overflow: hidden;
    }
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #f9f9f9 !important;
    }
    .stDataFrame tbody tr:hover {
        background-color: #ffe8cc !important;
    }
    .stDataFrame th {
        background-color: #ffb366 !important;
        color: #003366 !important;
        font-weight: bold;
    }
    input[type=number] {
        border-radius: 6px;
        border: 2px solid #ccc;
        padding: 5px;
        font-weight: 600;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Header
# ----------------------------
st.markdown(
    "<h1 style='text-align:center;'><span class='oq'>OQBI</span> Oman - PIQuick Risk Dashboard</h1>",
    unsafe_allow_html=True,
)
st.write("Monitor process parameters, detect anomalies, and get instant feedback.")

# ----------------------------
# Helper functions
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
        return "background-color: #ff4d4d; color: white; font-weight: bold;"
    if val == "Normal":
        return "background-color: #28a745; color: white; font-weight: bold;"
    return "background-color: #ffcc00; color: black; font-weight: bold;"

# ----------------------------
# Inputs with Dynamic Feedback
# ----------------------------
st.markdown("<h3>📝 Input Daily Process Data (5 Days)</h3>", unsafe_allow_html=True)
days = 5
params = {key: [] for key in recommended_limits.keys()}

for d in range(days):
    st.markdown(f"### Day {d+1}")
    for key in recommended_limits.keys():
        rec_min, rec_max = recommended_limits[key]
        default = float((rec_min + rec_max) / 2)
        label = f"{key.replace('_',' ').title()} (recommended {rec_min}–{rec_max}) {emoji_for_value(default, key)}"
        val = st.number_input(
            label,
            value=default,
            min_value=float(ALLOWED_MIN),
            max_value=float(ALLOWED_MAX),
            step=1.0,
            key=f"{key}_{d}"
        )
        # Color feedback (within range -> green, else red)
        color = "#2ecc71" if rec_min <= val <= rec_max else "#e74c3c"
        st.markdown(
            f"""
            <style>
            div[data-testid="stNumberInput"][key="{key}_{d}"] input {{
                border: 2px solid {color} !important;
                color: {color} !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
        params[key].append(float(val))

st.markdown("---")

# ----------------------------
# System Health Table
# ----------------------------
st.markdown("<h3>💡 System Health Status</h3>", unsafe_allow_html=True)
health_rows = []
for d in range(days):
    row = {"Day": f"Day {d+1}"}
    for key in recommended_limits.keys():
        val = params[key][d]
        row[key.replace("_", " ").title()] = f"{health_status_for_value(val, key)} {emoji_for_value(val, key)}"
    health_rows.append(row)

df_health = pd.DataFrame(health_rows)
st.dataframe(df_health, use_container_width=True, height=220)

# ----------------------------
# Analysis Button
# ----------------------------
if st.button("Analyze Data"):
    df_values = pd.DataFrame(params)
    df_values.insert(0, "Day", [f"Day {i+1}" for i in range(days)])
    for key in recommended_limits.keys():
        df_values[key + "_risk"] = df_values[key].apply(lambda x: health_status_for_value(x, key))

    st.subheader("📊 Process Data & Risk Levels")

    # Style risk columns
    def apply_risk_styles(s):
        return [risk_color_css(v) for v in s]

    styled = df_values.style.apply(
        lambda col: apply_risk_styles(col) if col.name.endswith("_risk") else ["" for _ in col],
        axis=0
    )
    st.dataframe(styled, use_container_width=True, height=350)

    # ----------------------------
    # Suggestions Section
    # ----------------------------
    suggestions = []
    for d in range(days):
        for key in recommended_limits.keys():
            val = params[key][d]
            low, high = recommended_limits[key]
            if val < low:
                suggestions.append(f"⚠️ {key.replace('_',' ').title()} on Day {d+1} is low ({val} < {low}) → Increase slightly.")
            elif val > high:
                suggestions.append(f"🔥 {key.replace('_',' ').title()} on Day {d+1} is high ({val} > {high}) → Decrease slightly.")
    if not suggestions:
        suggestions_text = "✅ All parameters are within safe ranges."
    else:
        suggestions_text = "\n".join(suggestions)

    st.markdown("<div class='suggestion-card'><h4>💬 Suggestions</h4></div>", unsafe_allow_html=True)
    st.code(suggestions_text, language="text")

    # ----------------------------
    # Trend Chart
    # ----------------------------
    st.subheader("📈 Process Parameter Trends")
    fig, ax = plt.subplots(figsize=(12, 6))
    x = [f"Day {i+1}" for i in range(days)]
    for key in recommended_limits.keys():
        ax.plot(x, df_values[key], marker='o', label=key.replace("_", " ").title(), linewidth=2)
    ax.set_title("Process Parameter Trends", fontsize=16, color="#ffb366")
    ax.set_xlabel("Day")
    ax.set_ylabel("Value")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    st.pyplot(fig)
