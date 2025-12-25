import streamlit as st
import pandas as pd
from io import StringIO

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Analyst Brain – Hybrid Research Platform", layout="wide")
st.title("🧠 Analyst Brain")
st.caption("Hybrid Equity Research Platform: Screener + Coverage")

# --------------------------------------------------
# SIDEBAR: MODE SELECTION
# --------------------------------------------------
mode = st.sidebar.radio(
    "Select Mode",
    ["Market Screener", "Coverage Universe (Deep Research)"]
)

# ==================================================
# DATA LAYER 1: SCREENER (WIDE & LIGHT)
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
# DATA LAYER 2: COVERAGE (DEEP & CLEAN)
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
# MODE 1: MARKET SCREENER
# ==================================================
if mode == "Market Screener":
    st.subheader("🔍 Market Screener (Idea Discovery)")

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

    st.write(
        "This screener is used **only for idea discovery**. "
        "No narrative research or ratings are generated at this stage."
    )

    st.dataframe(filtered, use_container_width=True)

    st.info(
        "➡️ Stocks shortlisted here can be moved into the "
        "**Coverage Universe** for deep research."
    )

# ==================================================
# MODE 2: COVERAGE UNIVERSE
# ==================================================
if mode == "Coverage Universe (Deep Research)":
    st.subheader("📘 Coverage Universe – Full Equity Research")

    companies = st.multiselect(
        "Select companies for coverage",
        coverage_df["Company"].unique(),
        default=coverage_df["Company"].unique().tolist()
    )

    for company in companies:
        st.divider()
        sector = sector_map.get(company, "General")
        df = coverage_df[coverage_df["Company"] == company].sort_values("Year")

        rev_growth = (df["Revenue"].iloc[-1] / df["Revenue"].iloc[0] - 1) * 100
        margin_change = (df["EBIT"].iloc[-1] / df["Revenue"].iloc[-1]) - \
                        (df["EBIT"].iloc[0] / df["Revenue"].iloc[0])
        debt_change = df["Debt"].iloc[-1] - df["Debt"].iloc[0]

        rating = (
            "Positive Bias (Academic Buy-equivalent)"
            if rev_growth > 40 and margin_change > 0
            else "Neutral Bias (Academic Hold-equivalent)"
        )

        st.subheader(f"{company} – Equity Research Coverage")
        st.caption(f"Sector: {sector}")

        st.markdown("### Executive Summary")
        st.write(
            f"{company} is part of the {sector} sector and has delivered "
            f"{rev_growth:.1f}% revenue growth over the analysis period. "
            f"The company is currently assessed with a **{rating}**."
        )

        st.markdown("### Financial & Business Analysis")
        st.write(
            "Growth has been supported by operating scale and stable profitability. "
            f"Margins have {'improved' if margin_change > 0 else 'remained stable'}, "
            "indicating reasonable operating leverage."
        )

        st.markdown("### Balance Sheet & Capital Allocation")
        st.write(
            f"Debt levels have {'increased' if debt_change > 0 else 'remained controlled'}, "
            "making capital allocation discipline an important monitorable."
        )

        st.markdown("### Conclusion")
        st.write(
            f"Overall, {company} presents a "
            f"{'constructive' if 'Positive' in rating else 'balanced'} "
            "fundamental profile. The stock remains part of the active coverage universe."
        )

st.caption("⚠️ Educational hybrid research platform. Not investment advice.")
