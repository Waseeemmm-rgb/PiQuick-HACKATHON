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
# Custom CSS for Styling
# ----------------------------
st.markdown("""
<style>
body, .main, .block-container {
    background-color: #d0e7f9;
    color: #003366;
}
h1, h2, h3, h4 {
    color: #ffb366;
}
.summary-card {
    background-color: #ffffff90;
    padding: 15px;
    border-radius: 10px;
    margin-top: 10px;
}
.stDataFrame thead th {
    background-color: #ffb366;
    color: #003366;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Header with OQ in orange bold
# ----------------------------
st.markdown("<h1 style='text-align:center;'><span style='color:orange; font-weight:bold;'>OQ</span>BI Oman - PIQuick Risk Dashboard</h1>", unsafe_allow_html=True)
st.write("Monitor industrial parameters, detect anomalies, and visualize trends easily.")

# ----------------------------
# Parameter Setup
# ----------------------------
days = 5

params = {
    "pressure": {"unit":"bar", "values":[]},
    "temperature": {"unit":"°C", "values":[]},
    "flow": {"unit":"Kg/hour", "values":[]},
    "vibration": {"unit":"Hz", "values":[]},
    "oil_condition": {"unit":"Index", "values":[]},
    "chemical_concentration": {"unit":"%", "values":[]},
    "energy_consumption": {"unit":"GJ", "values":[]},
    "emissions": {"unit":"%", "values":[]},
    "production_unit": {"unit":"ton/day", "values":[]}
}

limits = {
    "pressure": (20.0, 50.0),
    "temperature": (200.0, 300.0),
    "flow": (1.0, 100.0),
    "vibration": (10.0, 80.0),
    "oil_condition": (20.0, 80.0),
    "chemical_concentration": (30.0, 90.0),
    "energy_consumption": (25.0, 50.0),
    "emissions": (1.0, 30.0),  # updated
    "production_unit": (50.0, 500.0)
}

# ----------------------------
# Interactive Day Selection
# ----------------------------
selected_day = st.selectbox("Select Day to Input Values", [f"Day {i+1}" for i in range(days)])
day_index = int(selected_day.split()[1])-1

st.markdown(f"<h3>📝 Input Parameters for {selected_day}</h3>", unsafe_allow_html=True)

# ----------------------------
# Helper function for input box color
# ----------------------------
def input_style(value, param):
    lower, upper = limits[param]
    if lower <= value <= upper:
        return f"color:green; font-weight:bold;"
    else:
        return f"color:red; font-weight:bold;"

# Input parameters for selected day
for param in params.keys():
    val = st.number_input(
        f"{param.replace('_',' ').title()} ({params[param]['unit']}) - {selected_day}",
        value=35.0,
        step=1.0,
        key=f"{param}_{day_index}"
    )
    params[param]["values"].append(val)

# ----------------------------
# System Health Table
# ----------------------------
st.markdown("<h3>💡 System Health Status</h3>", unsafe_allow_html=True)

health_data = {}
for param in params.keys():
    lower, upper = limits[param]
    status_list = []
    for val in params[param]["values"]:
        if val < lower:
            status_list.append("⚠️ Low")
        elif val > upper:
            status_list.append("🔥 High")
        else:
            status_list.append("✅ Normal")
    health_data[param] = status_list

health_df = pd.DataFrame(health_data, index=[f"Day {i+1}" for i in range(len(params["pressure"]["values"]))])

st.dataframe(health_df.style.set_properties(**{'text-align':'center'}))

# ----------------------------
# Risk Classification
# ----------------------------
def classify_risk(value, param):
    lower, upper = limits[param]
    if value < lower:
        return "Low"
    elif value > upper:
        return "High"
    else:
        return "Normal"

# Build full data
df_data = {}
for param in params.keys():
    df_data[param] = params[param]["values"]
df = pd.DataFrame(df_data)
df.insert(0, "Day", [f"Day {i+1}" for i in range(len(df))])

# Add risk columns
for param in params.keys():
    df[param+"_risk"] = df[param].apply(lambda x: classify_risk(x,param))

# ----------------------------
# Style numeric input table
# ----------------------------
def style_cell(v, param):
    lower, upper = limits[param]
    if v < lower or v > upper:
        return "color:red; font-weight:bold; text-align:center;"
    else:
        return "color:green; text-align:center;"

styled_df = df.style
for param in params.keys():
    styled_df = styled_df.applymap(lambda v: style_cell(v, param), subset=[param])

def style_risk(v):
    if v=="High":
        return "color:red; font-weight:bold; text-align:center;"
    elif v=="Low":
        return "color:orange; font-weight:bold; text-align:center;"
    else:
        return "color:green; font-weight:bold; text-align:center;"

for param in params.keys():
    styled_df = styled_df.applymap(style_risk, subset=[param+"_risk"])

st.subheader("📊 Process Data & Risk Levels")
st.dataframe(styled_df, height=500)

# ----------------------------
# Suggestions
# ----------------------------
st.markdown("<h3>💡 Suggestions</h3>", unsafe_allow_html=True)
suggestions = ""
for param in params.keys():
    lower, upper = limits[param]
    for i,val in enumerate(params[param]["values"]):
        if val < lower:
            suggestions += f"Day {i+1} - {param.replace('_',' ').title()}: Increase value (below {lower})\n"
        elif val > upper:
            suggestions += f"Day {i+1} - {param.replace('_',' ').title()}: Decrease value (above {upper})\n"
if suggestions=="":
    suggestions="✅ All parameters within range"

st.markdown(f"<div style='background-color:white; padding:10px; border-radius:10px'><pre>{suggestions}</pre></div>", unsafe_allow_html=True)

# ----------------------------
# Trend Chart
# ----------------------------
fig, ax = plt.subplots(figsize=(12,6))
for param in params.keys():
    ax.plot(df['Day'], df[param], marker='o', label=f"{param.replace('_',' ').title()} ({params[param]['unit']})", linewidth=2)
ax.set_title("Process Parameter Trends", fontsize=16, color='#ffb366')
ax.set_xlabel("Day")
ax.set_ylabel("Value")
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend()
st.pyplot(fig)
