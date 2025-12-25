import streamlit as st
import pandas as pd
from io import StringIO

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Analyst Brain Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# DARK TERMINAL THEME (REAPPLIED)
# ==================================================
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top left, #1b1f3b, #0b0e1a);
    color: #eaeaf0;
    font-family: Inter, sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #11142a, #0b0e1a);
}

/* Headers */
h1, h2, h3 {
    color: #ffffff;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.45);
    margin-bottom: 20px;
}

/* Subtle divider */
hr {
    border: 1px solid rgba(255,255,255,0.08);
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

# ==================================================
# TITLE
# ==================================================
st.markdown("<h1>🧠 Analyst Brain Terminal</h1>", unsafe_allow_html=True)
st.caption("Hybrid Equity Research Platform • Screener + Coverage Universe")

# ==================================================
# SIDEBAR MODE SELECT
# ==================================================
mode = st.sidebar.radio(
    "Mode",
    ["🔍 Market Screener", "📘 Coverage Universe (Deep Research)"]
)

# ==================================================
# DATA — SCREENER (WIDE)
# ==================================================
screener_csv = """
Company,MarketCap,RevenueGrowth,ROE,DebtEquity,Sector
Reliance Industries,1800000,12,9,0.6,Conglomerate
TCS,1400000,10,35,0.1,IT Services
Infosys,650000,8,30,0.1,IT Services
HDFC Bank,1200000,14,17,0.9,Banking
ICICI Bank,950000,18,18,1.1,Banking
ITC,550000,9,28,0.0,FMCG
HUL,650000,7,32,0.0,FMCG
Bharti Airtel,900000,20,15,1.8,Telecom
L&T,800000,11,14,1.5,Infrastructure
Asian Paints,750000,6,40,0.0,Consumer
"""
screener_df = pd.read_csv(StringIO(screener_csv))

# ==================================================
# DATA — COVERAGE (DEEP)
# ==================================================
coverage_csv = """
Company,Year,Revenue,EBIT,PAT,OCF,Debt
Reliance Industries,2020,596000,98500,39354,88200,305000
Reliance Industries,2024,1023000,152000,73500,130000,330000
TCS,2020,161541,40200,32430,38200,15000
TCS,2024,240893,56000,45000,49000,11000
ITC,2020,44674,17000,15000,15500,12000
ITC,2024,70500,27000,22000,23500,8000
"""
coverage_df = pd.read_csv(StringIO(coverage_csv))

sector_map = {
    "Reliance Industries": "Conglomerate",
    "TCS": "IT Services",
    "ITC": "FMCG"
}

# ==================================================
# MACRO INPUTS
# ==================================================
st.sidebar.markdown("### 🌍 Macro Assumptions")
interest_rate = st.sidebar.selectbox("Interest Rates", ["Falling", "Stable", "Rising"])
inflation = st.sidebar.selectbox("Inflation", ["Cooling", "Stable", "Elevated"])
gdp = st.sidebar.selectbox("GDP Growth", ["Strong", "Moderate", "Weak"])

# ==================================================
# HELPER FUNCTIONS
# ==================================================
def derive_rating(rev_growth, margin_change, debt_change):
    if rev_growth > 40 and margin_change > 0 and debt_change <= 0:
        return "Positive Bias (Academic Buy-equivalent)"
    elif rev_growth > 20:
        return "Neutral Bias (Academic Hold-equivalent)"
    else:
        return "Cautious Bias (Academic Underperform-equivalent)"

def macro_overlay(sector):
    if sector == "IT Services":
        return (
            f"IT services are sensitive to global demand cycles. "
            f"A {gdp.lower()} growth outlook combined with {interest_rate.lower()} "
            f"interest rates is {'supportive' if gdp != 'Weak' else 'challenging'} "
            f"for revenue visibility."
        )
    if sector == "FMCG":
        return (
            f"FMCG businesses are influenced by consumption and inflation trends. "
            f"{inflation} inflation and {gdp.lower()} GDP growth will directly affect "
            f"volume growth and margin sustainability."
        )
    if sector == "Conglomerate":
        return (
            f"Conglomerates are impacted by capital availability and economic cycles. "
            f"{interest_rate} interest rates and {gdp.lower()} GDP growth will shape "
            f"capital allocation and segment performance."
        )
    return "Macro conditions play a mixed role across business segments."

# ==================================================
# MODE 1 — SCREENER
# ==================================================
if mode == "🔍 Market Screener":
    st.subheader("🔍 Market Screener — Idea Discovery")

    sector_filter = st.multiselect(
        "Filter by Sector",
        screener_df["Sector"].unique(),
        default=screener_df["Sector"].unique().tolist()
    )

    min_growth = st.slider("Minimum Revenue Growth (%)", 0, 25, 5)

    filtered = screener_df[
        (screener_df["Sector"].isin(sector_filter)) &
        (screener_df["RevenueGrowth"] >= min_growth)
    ]

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write(
        "This module is used strictly for **idea discovery**. "
        "No narrative research or ratings are generated at this stage."
    )
    st.dataframe(filtered, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==================================================
# MODE 2 — COVERAGE UNIVERSE
# ==================================================
if mode == "📘 Coverage Universe (Deep Research)":
    st.subheader("📘 Coverage Universe — Full Narrative Research")

    companies = st.multiselect(
        "Select companies under coverage",
        coverage_df["Company"].unique(),
        default=coverage_df["Company"].unique().tolist()
    )

    for company in companies:
        st.divider()
        sector = sector_map.get(company, "General")
        df = coverage_df[coverage_df["Company"] == company].sort_values("Year")

        rev_growth = (df["Revenue"].iloc[-1] / df["Revenue"].iloc[0] - 1) * 100
        margin_change = (
            df["EBIT"].iloc[-1] / df["Revenue"].iloc[-1]
            - df["EBIT"].iloc[0] / df["Revenue"].iloc[0]
        )
        debt_change = df["Debt"].iloc[-1] - df["Debt"].iloc[0]

        rating = derive_rating(rev_growth, margin_change, debt_change)

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.subheader(company)
        st.caption(f"Sector: {sector} | Rating: {rating}")

        st.markdown("**Executive Summary**")
        st.write(
            f"{company} operates within the {sector} sector and has delivered "
            f"{rev_growth:.1f}% revenue growth over the analysis period. "
            f"The stock is currently assessed with a **{rating}**."
        )

        st.markdown("**Business & Financial Analysis**")
        st.write(
            f"Growth has been supported by operating scale and "
            f"{'improving' if margin_change > 0 else 'stable'} margins, "
            "indicating reasonable operating leverage."
        )

        st.markdown("**Balance Sheet & Capital Allocation**")
        st.write(
            f"Debt levels have {'increased' if debt_change > 0 else 'remained controlled'}, "
            "making capital allocation discipline an important monitorable."
        )

        st.markdown("**Macro Overlay**")
        st.write(macro_overlay(sector))

        st.markdown("**Conclusion**")
        st.write(
            f"Overall, {company} presents a "
            f"{'constructive' if 'Positive' in rating else 'balanced'} "
            "fundamental profile and remains part of the active coverage universe."
        )

        st.markdown('</div>', unsafe_allow_html=True)

# ==================================================
# FOOTER
# ==================================================
st.caption("⚠️ Educational hybrid equity research terminal. Not investment advice.")
