import streamlit as st
import pandas as pd
from io import StringIO
from fpdf import FPDF

# --------------------------------------------------
# APP CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Analyst Brain Pro", layout="wide")
st.title("🧠 Analyst Brain Pro")
st.caption("Advanced, Sector-Aware Equity Research Intelligence")

# --------------------------------------------------
# EMBEDDED FUNDAMENTAL DATA
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
ICICI Bank,2020,84400,28000,7900,25000,300000
ICICI Bank,2021,102000,35000,16000,34000,290000
ICICI Bank,2022,121000,45000,23000,41000,275000
ICICI Bank,2023,147000,56000,31000,48000,260000
ICICI Bank,2024,172000,68000,40000,56000,245000
TCS,2020,161541,40200,32430,38200,15000
TCS,2021,164177,43000,32496,39000,14000
TCS,2022,191754,47000,38327,42000,13000
TCS,2023,225458,52000,42147,46000,12000
TCS,2024,240893,56000,45000,49000,11000
Infosys,2020,90791,25000,21000,23000,10000
Infosys,2021,100472,28000,23000,26000,9000
Infosys,2022,121641,32000,26000,30000,8000
Infosys,2023,146767,36000,29000,33000,7000
Infosys,2024,156000,38000,31000,35000,6000
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
    "ICICI Bank": "Banking",
    "TCS": "IT Services",
    "Infosys": "IT Services",
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
# METRICS
# --------------------------------------------------
df["Revenue Growth %"] = df["Revenue"].pct_change() * 100
df["PAT Growth %"] = df["PAT"].pct_change() * 100
df["EBIT Margin %"] = (df["EBIT"] / df["Revenue"]) * 100
df["Capital Employed"] = df["Debt"] + (0.3 * df["Revenue"])
df["ROCE %"] = (df["EBIT"] / df["Capital Employed"]) * 100
df["EPS Index"] = df["PAT"] / 1000

# --------------------------------------------------
# SNAPSHOT
# --------------------------------------------------
st.subheader("📊 Financial Snapshot")
st.dataframe(df.round(2), use_container_width=True)

# --------------------------------------------------
# ANALYST FUNCTIONS
# --------------------------------------------------
def consistency(series):
    pos = (series > 0).sum()
    total = len(series.dropna())
    if total == 0:
        return "Insufficient data"
    ratio = pos / total
    if ratio >= 0.8:
        return "Highly Consistent"
    elif ratio >= 0.5:
        return "Moderately Consistent"
    return "Inconsistent"

def growth_quality(rg, pg):
    if rg > 10 and pg > rg:
        return "High Quality Growth"
    if rg > 0 and pg > 0:
        return "Moderate Quality Growth"
    return "Low Quality Growth"

def earnings_quality(pat, ocf):
    if pat.iloc[-1] > pat.iloc[-2] and ocf.iloc[-1] < ocf.iloc[-2]:
        return "⚠️ Profit rising but cash flow weakening"
    return "Earnings supported by cash flow"

def leverage_signal(debt):
    return "⚠️ Rising leverage" if debt.iloc[-1] > debt.iloc[-2] else "Debt stable"

def roce_signal(roce):
    if roce > 20:
        return "Excellent capital efficiency"
    if roce > 12:
        return "Acceptable capital efficiency"
    return "⚠️ Weak capital efficiency"

# --------------------------------------------------
# INSIGHTS
# --------------------------------------------------
st.subheader("🧠 Analytical Insights")

col1, col2 = st.columns(2)
with col1:
    st.metric("Revenue Consistency", consistency(df["Revenue Growth %"]))
    st.metric("Margin Consistency", consistency(df["EBIT Margin %"].diff()))
    st.metric("Growth Quality", growth_quality(df["Revenue Growth %"].iloc[-1], df["PAT Growth %"].iloc[-1]))

with col2:
    st.metric("Earnings Quality", earnings_quality(df["PAT"], df["OCF"]))
    st.metric("Leverage Signal", leverage_signal(df["Debt"]))
    st.metric("ROCE Signal", roce_signal(df["ROCE %"].iloc[-1]))

# --------------------------------------------------
# VALUATION
# --------------------------------------------------
st.subheader("💰 Scenario Valuation")

pe_base = 20 if sector == "IT Services" else 15 if sector == "Banking" else 18
scenarios = {"Bear": pe_base - 3, "Base": pe_base, "Bull": pe_base + 3}

for s, pe in scenarios.items():
    st.write(f"{s} Case ({pe}x):", round(df["EPS Index"].iloc[-1] * pe, 2))

# --------------------------------------------------
# THESIS STABILITY
# --------------------------------------------------
warnings = 0
if "⚠️" in earnings_quality(df["PAT"], df["OCF"]):
    warnings += 1
if "⚠️" in leverage_signal(df["Debt"]):
    warnings += 1
if "⚠️" in roce_signal(df["ROCE %"].iloc[-1]):
    warnings += 1

st.subheader("📈 Thesis Stability")
st.metric("Thesis Status", "Strengthening" if warnings == 0 else "Stable but Fragile" if warnings == 1 else "Weakening")

# --------------------------------------------------
# EXECUTIVE SUMMARY
# --------------------------------------------------
st.subheader("🧾 Auto Executive Summary")

st.write(
    f"{company} operates in the {sector} sector and demonstrates "
    f"{consistency(df['Revenue Growth %'])} revenue performance. "
    f"Growth quality is assessed as {growth_quality(df['Revenue Growth %'].iloc[-1], df['PAT Growth %'].iloc[-1])}. "
    f"Capital efficiency is {roce_signal(df['ROCE %'].iloc[-1])}, while "
    f"{earnings_quality(df['PAT'], df['OCF'])}. "
    f"Overall thesis is currently assessed as "
    f"{'robust' if warnings == 0 else 'moderate' if warnings == 1 else 'under pressure'}."
)

# --------------------------------------------------
# IC NOTE PDF
# --------------------------------------------------
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, f"IC Note – {company}\nSector: {sector}\n\nExecutive Summary:\n" + st.session_state.summary)
    return pdf

st.caption("⚠️ Educational equity research system. Not investment advice.")
