import streamlit as st
import pandas as pd
from io import StringIO
import matplotlib.pyplot as plt

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Analyst Brain X",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# GLOBAL CSS (DASHBOARD STYLE)
# ----------------------------
st.markdown("""
<style>
/* Background */
.stApp {
    background: radial-gradient(circle at top left, #1b1f3b, #0b0e1a);
    color: #eaeaf0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #11142a, #0b0e1a);
}

/* Cards */
.card {
    background: rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    margin-bottom: 20px;
}

/* Headings */
h1, h2, h3 {
    color: #ffffff;
}

/* Metrics */
.metric {
    font-size: 26px;
    font-weight: 600;
}
.metric-label {
    font-size: 14px;
    color: #b0b3c7;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #7f5cff, #4ddcff);
    color: black;
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 600;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# DATA (CONTROLLED)
# ----------------------------
csv_data = """
Company,Year,Revenue,EBIT,PAT,Debt
Reliance Industries,2020,596000,98500,39354,305000
Reliance Industries,2021,539238,97500,53739,280000
Reliance Industries,2022,792756,135000,60705,310000
Reliance Industries,2023,976524,145000,66702,325000
Reliance Industries,2024,1023000,152000,73500,330000
TCS,2020,161541,40200,32430,15000
TCS,2021,164177,43000,32496,14000
TCS,2022,191754,47000,38327,13000
TCS,2023,225458,52000,42147,12000
TCS,2024,240893,56000,45000,11000
"""

df_all = pd.read_csv(StringIO(csv_data))

# ----------------------------
# SIDEBAR
# ----------------------------
st.sidebar.markdown("## 🧠 Analyst Brain X")
company = st.sidebar.selectbox(
    "Select Company",
    df_all["Company"].unique()
)

df = df_all[df_all["Company"] == company].sort_values("Year")
df["Revenue Growth %"] = df["Revenue"].pct_change() * 100
df["EBIT Margin %"] = df["EBIT"] / df["Revenue"] * 100

latest = df.iloc[-1]

# ----------------------------
# HEADER
# ----------------------------
st.markdown(f"""
<h1>📊 {company} Dashboard</h1>
<p style="color:#b0b3c7;">Autonomous Equity Research Overview</p>
""", unsafe_allow_html=True)

# ----------------------------
# KPI CARDS ROW
# ----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Revenue (₹ Cr)</div>
        <div class="metric">{int(latest['Revenue']):,}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">EBIT Margin</div>
        <div class="metric">{latest['EBIT Margin %']:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">PAT (₹ Cr)</div>
        <div class="metric">{int(latest['PAT']):,}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Debt (₹ Cr)</div>
        <div class="metric">{int(latest['Debt']):,}</div>
    </div>
    """, unsafe_allow_html=True)

# ----------------------------
# CHARTS SECTION
# ----------------------------
left, right = st.columns([2,1])

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📈 Revenue & Profit Trend")

    fig, ax = plt.subplots()
    ax.plot(df["Year"], df["Revenue"], label="Revenue")
    ax.plot(df["Year"], df["EBIT"], label="EBIT")
    ax.plot(df["Year"], df["PAT"], label="PAT")
    ax.legend()
    ax.grid(alpha=0.3)

    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🧠 Analyst Insight")

    insight = (
        "Strong operating leverage visible."
        if latest["EBIT Margin %"] > df["EBIT Margin %"].mean()
        else "Margin pressure observed."
    )

    st.write(insight)
    st.write("• Revenue scale improving")
    st.write("• Balance sheet manageable")
    st.write("• Monitor margin sustainability")

    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# TABLE SECTION
# ----------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("### 📑 Financial History")
st.dataframe(df.round(2), use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------
# FOOTER
# ----------------------------
st.caption("⚠️ Educational equity research dashboard. Not investment advice.")
