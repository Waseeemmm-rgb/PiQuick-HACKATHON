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
# Custom CSS
# ----------------------------
st.markdown("""
<style>
body, .main, .block-container {
    background-color: #d0e7f9;
    color: #003366;
}
h1, h2, h3, h4 {
    color: #003366;
}
.summary-card, .suggestion-card {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 10px;
    margin-top: 10px;
}
.stDataFrame tbody tr th {
    background-color: #ffb366;
}
.stDataFrame tbody tr td {
    color: #003366;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Header
# ----------------------------
st.markdown("""
<h1 style='text-align:center;'>
<b><span style='color:#ffb366;'>OQBI</span></b> Oman - PIQuick Risk Dashboard
</h1>
""", unsafe_allow_html=True)
st.write("Monitor industrial parameters, detect anomalies, and visualize trends easily.")

# ----------------------------
# Parameter Setup
# ----------------------------
days = 5

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

limits = {
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

# Emoji helper for input labels
def get_emoji(value, param):
    low, high = limits[param]
    if value < low:
        return "⚠️"
    elif value > high:
        return "🔥"
    else:
        return "✅"

# ----------------------------
# Input Section
# ----------------------------
st.markdown("<h3>📝 Input Daily Process Data (5 Days)</h3>", unsafe_allow_html=True)

for i in range(days):
    st.markdown(f"<h4>Day {i+1}</h4>", unsafe_allow_html=True)
    for param in params.keys():
        min_val, max_val = limits[param]
        default = (min_val + max_val) / 2
        emoji = get_emoji(default, param)
        params[param].append(st.number_input(
            f"{param.replace('_',' ').title()} ({min_val}-{max_val}) {emoji} - Day {i+1}",
            value=float(default),
            min_value=float(min_val),
            max_value=float(max_val),
            step=1.0
        ))

# ----------------------------
# System Health Status
# ----------------------------
st.markdown("<h3>💡 System Health Status</h3>", unsafe_allow_html=True)

health_data = []
for i in range(days):
    day_status = {"Day": f"Day {i+1}"}
    for param in params.keys():
        val = params[param][i]
        low, high = limits[param]
        if val < low:
            status = "Low ⚠️"
        elif val > high:
            status = "High 🔥"
        else:
            status = "Normal ✅"
        day_status[param.replace("_"," ").title()] = status
    health_data.append(day_status)

df_health = pd.DataFrame(health_data)
st.dataframe(df_health, height=200)

# ----------------------------
# Risk Classification
# ----------------------------
def classify_risk(value, param):
    low, high = limits[param]
    if value < low:
        return "Low"
    elif value > high:
        return "High"
    else:
        return "Normal"

# ----------------------------
# Analyze Button
# ----------------------------
if st.button("Analyze Data"):
    df = pd.DataFrame(params)
    df.insert(0, "Day", [f"Day {i+1}" for i in range(days)])

    # Risk columns
    for param in params.keys():
        df[param+"_risk"] = df[param].apply(lambda x: classify_risk(x, param))

    # Color map for risks
    def color_risk(val):
        if val == "High":
            return 'background-color: red; color:white; font-weight:bold;'
        elif val == "Normal":
            return 'background-color: green; color:white; font-weight:bold;'
        else:
            return 'background-color: yellow; color:black; font-weight:bold;'

    st.subheader("📊 Process Data & Risk Levels")
    st.dataframe(df.style.applymap(color_risk, subset=[col for col in df.columns if "_risk" in col]), height=400)

    # ----------------------------
    # Suggestion Panel
    # ----------------------------
    suggestions = ""
    for i in range(days):
        day = f"Day {i+1}"
        for param in params.keys():
            val = params[param][i]
            low, high = limits[param]
            if val < low:
                suggestions += f"⚠️ {param.replace('_',' ').title()} on {day} is below minimum. Consider increasing it.\n"
            elif val > high:
                suggestions += f"🔥 {param.replace('_',' ').title()} on {day} is above maximum. Consider decreasing it.\n"
    if suggestions == "":
        suggestions = "✅ All parameters within normal range."

    st.markdown(f"""
    <div class='suggestion-card'>
        <h4>💡 Suggestions</h4>
        <pre>{suggestions}</pre>
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------
    # Trend Chart
    # ----------------------------
    fig, ax = plt.subplots(figsize=(12,6))
    for param in params.keys():
        ax.plot(df['Day'], df[param], marker='o', label=param.replace('_',' ').title(), linewidth=2)
    ax.set_title("Process Parameter Trends", fontsize=16, color='#ffb366')
    ax.set_xlabel("Day")
    ax.set_ylabel("Value")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    st.pyplot(fig)
