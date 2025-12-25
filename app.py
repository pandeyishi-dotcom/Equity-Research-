import streamlit as st
import pandas as pd
from io import StringIO
from math import sqrt

# --------------------------------------------------
# APP CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Analyst Brain X", layout="wide")
st.title("🧠 Analyst Brain X")
st.caption("Institutional-Style Equity Research Intelligence")

# --------------------------------------------------
# EMBEDDED FUNDAMENTALS (CONTROLLED DATA)
# --------------------------------------------------
csv_data = """
Company,Year,Revenue,EBIT,PAT,OCF,Debt
Reliance Industries,2020,596000,98500,39354,88200,305000
Reliance Industries,2021,539238,97500,53739,91000,280000
Reliance Industries,2022,792756,135000,60705,118000,310000
Reliance Industries,2023,976524,145000,66702,121000,325000
Reliance Industries,2024,1023000,152000,73500,130000,330000
HDFC Bank,2020,122000,54000,31000,48000,120000
HDFC Bank,2021,138000,60000,35000,52000,130000
HDFC Bank,2022,156000,69000,41000,61000,150000
HDFC Bank,2023,176000,77000,44000,68000,165000
HDFC Bank,2024,196000,85000,50000,72000,180000
TCS,2020,161541,40200,32430,38200,15000
TCS,2021,164177,43000,32496,39000,14000
TCS,2022,191754,47000,38327,42000,13000
TCS,2023,225458,52000,42147,46000,12000
TCS,2024,240893,56000,45000,49000,11000
ITC,2020,44674,17000,15000,15500,12000
ITC,2021,46395,18000,16000,16500,11000
ITC,2022,54752,21000,18000,19500,10000
ITC,2023,62615,24000,20000,21500,9000
ITC,2024,70500,27000,22000,23500,8000
"""

data = pd.read_csv(StringIO(csv_data))

# --------------------------------------------------
# SECTOR MAP
# --------------------------------------------------
sector_map = {
    "Reliance Industries": "Conglomerate",
    "HDFC Bank": "Banking",
    "TCS": "IT Services",
    "ITC": "FMCG"
}

# --------------------------------------------------
# COMPANY SELECTION
# --------------------------------------------------
company = st.selectbox("Select Company", data["Company"].unique())
sector = sector_map.get(company, "General")
st.caption(f"Sector: {sector}")

df = data[data["Company"] == company].sort_values("Year")

# --------------------------------------------------
# CORE METRICS
# --------------------------------------------------
df["Revenue Growth %"] = df["Revenue"].pct_change() * 100
df["PAT Growth %"] = df["PAT"].pct_change() * 100
df["EBIT Margin %"] = (df["EBIT"] / df["Revenue"]) * 100
df["Capital Employed"] = df["Debt"] + 0.3 * df["Revenue"]
df["ROCE %"] = (df["EBIT"] / df["Capital Employed"]) * 100

# --------------------------------------------------
# MACRO STRESS TESTING (ADVANCED)
# --------------------------------------------------
st.subheader("🌍 Macro Stress Testing")

inflation = st.slider("Inflation Shock (%)", -5.0, 10.0, 0.0)
rates = st.slider("Interest Rate Shock (%)", -3.0, 5.0, 0.0)
growth = st.slider("GDP Growth Shock (%)", -5.0, 5.0, 0.0)

def macro_impact(sector, inf, rate, gdp):
    impact = 0
    if sector == "Banking":
        impact += rate * 0.6 + gdp * 0.4
    elif sector == "IT Services":
        impact += gdp * 0.7 - inf * 0.3
    elif sector == "FMCG":
        impact -= inf * 0.6 + gdp * 0.2
    else:
        impact += gdp * 0.5 - rate * 0.2
    return impact

macro_score = macro_impact(sector, inflation, rates, growth)
st.metric("Macro Sensitivity Score", round(macro_score, 2))

# --------------------------------------------------
# FACTOR ATTRIBUTION (VERY BUY-SIDE)
# --------------------------------------------------
st.subheader("🧬 Factor Attribution")

factors = {
    "Growth": df["Revenue Growth %"].iloc[-1],
    "Profitability": df["EBIT Margin %"].iloc[-1],
    "Capital Efficiency": df["ROCE %"].iloc[-1],
    "Balance Sheet": -df["Debt"].iloc[-1] / df["Revenue"].iloc[-1]
}

factor_df = pd.DataFrame.from_dict(factors, orient="index", columns=["Impact Score"])
st.dataframe(factor_df.round(2), use_container_width=True)

# --------------------------------------------------
# CONFIDENCE-WEIGHTED THESIS SCORE
# --------------------------------------------------
st.subheader("🎯 Conviction Scoring Model")

score = 0
score += 1 if df["Revenue Growth %"].iloc[-1] > 5 else -1
score += 1 if df["ROCE %"].iloc[-1] > 15 else -1
score += 1 if df["EBIT Margin %"].iloc[-1] > df["EBIT Margin %"].mean() else -1
score += 1 if macro_score > 0 else -1

confidence = (score + 4) / 8  # normalize 0–1

st.metric("Confidence Score", round(confidence, 2))

# --------------------------------------------------
# POSITION SIZING LOGIC (NO RECOMMENDATIONS)
# --------------------------------------------------
st.subheader("📐 Portfolio Context (Analyst View)")

def position_guidance(conf):
    if conf > 0.75:
        return "High-conviction candidate (core position)"
    elif conf > 0.5:
        return "Moderate conviction (satellite position)"
    else:
        return "Low conviction (watchlist only)"

st.info(position_guidance(confidence))

# --------------------------------------------------
# EXECUTIVE SUMMARY (AUTO)
# --------------------------------------------------
st.subheader("🧾 Executive Summary")

st.write(
    f"{company} operates in the {sector} sector with recent revenue growth of "
    f"{round(df['Revenue Growth %'].iloc[-1],2)}% and ROCE of "
    f"{round(df['ROCE %'].iloc[-1],2)}%. "
    f"Macro sensitivity under current assumptions is assessed as "
    f"{'favorable' if macro_score > 0 else 'challenging'}. "
    f"Overall confidence score stands at {round(confidence,2)}, suggesting "
    f"{position_guidance(confidence).lower()}."
)

st.caption("⚠️ Educational, analyst-style research system. Not investment advice.")
