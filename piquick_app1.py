import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="PIQuick Dashboard - OQBI Oman", layout="wide")

# ----------------------------
# PARAMETER RANGES
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

# ----------------------------
# STYLING
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
.stDataFrame tbody tr:nth-child(even) {
    background-color: #f2f7ff !important;
}
.stDataFrame tbody tr:hover {
    background-color: #ffe8cc !important;
}
input[type=number] {
    border-radius: 8px;
    padding: 6px;
    font-weight: 600;
    font-size: 15px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# HEADER
# ----------------------------
st.markdown(
    "<h1 style='text-align:center;'><span class='oq'>OQBI</span> Oman — PIQuick Risk Dashboard</h1>",
    unsafe_allow_html=True
)
st.write("Monitor process parameters, detect anomalies, and visualize safe ranges dynamically.")

# ----------------------------
# INPUT SECTION
# ----------------------------
st.markdown("## 🧭 Input Process Data")

days = 5
params = {key: [] for key in recommended_limits.keys()}

for d in range(days):
    st.markdown(f"### 📅 Day {d+1}")
    for key, (low, high) in recommended_limits.items():
        default_val = (low + high) / 2
        label = f"{key.replace('_', ' ').title()} (Recommended {low}–{high})"
        val = st.number_input(
            label,
            value=float(default_val),
            min_value=float(-1e6),
            max_value=float(1e6),
            step=1.0,
            key=f"{key}_{d}"
        )
        
        # Choose color based on range
        if low <= val <= high:
            color = "#2ecc71"  # green
        else:
            color = "#e74c3c"  # red
        
        # Inject dynamic style for that specific input
        st.markdown(
            f"""
            <style>
            div[data-testid="stNumberInput"][key="{key}_{d}"] input {{
                border: 2px solid {color} !important;
                color: {color} !important;
                font-weight: 700 !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        params[key].append(val)

st.markdown("---")

# ----------------------------
# SYSTEM HEALTH STATUS TABLE
# ----------------------------
st.markdown("## 💡 System Health Status")

def get_status(val, low, high):
    if val < low:
        return "Low ⚠️"
    elif val > high:
        return "High 🔥"
    return "Normal ✅"

health_data = []
for d in range(days):
    row = {"Day": f"Day {d+1}"}
    for key, (low, high) in recommended_limits.items():
        row[key.replace('_', ' ').title()] = get_status(params[key][d], low, high)
    health_data.append(row)

df_health = pd.DataFrame(health_data)
st.dataframe(df_health, use_container_width=True, height=250)

# ----------------------------
# ANALYZE BUTTON
# ----------------------------
if st.button("🔍 Analyze Data"):
    df_values = pd.DataFrame(params)
    df_values.insert(0, "Day", [f"Day {i+1}" for i in range(days)])
    
    # Generate risk column colors
    def risk_color(val, low, high):
        if val < low:
            return "background-color: #f39c12; color: black;"
        elif val > high:
            return "background-color: #e74c3c; color: white;"
        else:
            return "background-color: #2ecc71; color: white;"
    
    styled = df_values.style.apply(
        lambda df: [
            risk_color(df.iloc[i], *recommended_limits[df.index.name]) 
            if df.name in recommended_limits else "" for i in range(len(df))
        ], axis=0
    )

    st.markdown("### 📊 Parameter Data with Risk Levels")
    st.dataframe(df_values, use_container_width=True, height=350)

    # ----------------------------
    # SUGGESTIONS
    # ----------------------------
    st.markdown("### 💬 Smart Suggestions")
    suggestions = []
    for d in range(days):
        for key, (low, high) in recommended_limits.items():
            val = params[key][d]
            if val < low:
                suggestions.append(f"⚠️ {key.replace('_',' ').title()} (Day {d+1}) is low ({val} < {low}) → Increase slightly.")
            elif val > high:
                suggestions.append(f"🔥 {key.replace('_',' ').title()} (Day {d+1}) is high ({val} > {high}) → Reduce slightly.")
    if not suggestions:
        st.success("✅ All parameters are within safe operating ranges.")
    else:
        for s in suggestions:
            st.markdown(f"- {s}")

    # ----------------------------
    # TREND CHART
    # ----------------------------
    st.markdown("### 📈 Parameter Trends Over Days")
    fig, ax = plt.subplots(figsize=(10, 5))
    x = [f"Day {i+1}" for i in range(days)]
    for key in recommended_limits.keys():
        ax.plot(x, params[key], marker='o', label=key.replace('_', ' ').title(), linewidth=2)
    ax.set_xlabel("Day")
    ax.set_ylabel("Value")
    ax.set_title("Parameter Trends Over Time")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    ax.grid(alpha=0.3)
    st.pyplot(fig)
