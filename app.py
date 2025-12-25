import streamlit as st
import pandas as pd
from io import StringIO
from fpdf import FPDF

# --------------------------------------------------
# APP CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Analyst Brain", layout="wide")
st.title("🧠 Analyst Brain")
st.caption("Sector-Aware Equity Research Intelligence System")

# --------------------------------------------------
# EMBEDDED FUNDAMENTAL DATA (CONTROLLED DATA LAYER)
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
# SECTOR MAPPING
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
df["EBIT Margin %"] = (df["EBIT"] / df["Revenue"]) * 100

# --------------------------------------------------
# SNAPSHOT
# --------------------------------------------------
st.subheader(f"📊 Company Snapshot — {company}")
st.dataframe(df.round(2), use_container_width=True)

# --------------------------------------------------
# SECTOR INSIGHT
# --------------------------------------------------
def sector_insight(sector):
    if sector == "Banking":
        return "Focus on asset quality, credit growth, and balance sheet strength."
    if sector == "IT Services":
        return "Focus on revenue growth, margins, and cash generation."
    if sector == "FMCG":
        return "Focus on pricing power, margin stability, and demand resilience."
    if sector == "Conglomerate":
        return "Focus on capital allocation, leverage, and segment performance."
    return "Focus on revenue and profitability sustainability."

st.info(sector_insight(sector))

# --------------------------------------------------
# ANALYST LOGIC
# --------------------------------------------------
def revenue_trend(x):
    if x.iloc[-1] > 10:
        return "Strong growth"
    elif x.iloc[-1] > 0:
        return "Moderating growth"
    return "⚠️ Revenue slowdown"

def margin_trend(x):
    return "Expanding" if x.iloc[-1] > x.iloc[-2] else "Compressing"

def earnings_quality(pat, ocf):
    if pat.iloc[-1] > pat.iloc[-2] and ocf.iloc[-1] < ocf.iloc[-2]:
        return "⚠️ Profit rising but cash flow weakening"
    return "Earnings supported by cash flow"

def leverage_check(debt):
    return "⚠️ Rising leverage" if debt.iloc[-1] > debt.iloc[-2] else "Debt stable"

# --------------------------------------------------
# WHAT CHANGED
# --------------------------------------------------
st.subheader("🔍 What Changed Recently")

col1, col2 = st.columns(2)
with col1:
    st.metric("Revenue Trend", revenue_trend(df["Revenue Growth %"]))
    st.metric("Margin Trend", margin_trend(df["EBIT Margin %"]))
with col2:
    st.metric("Earnings Quality", earnings_quality(df["PAT"], df["OCF"]))
    st.metric("Balance Sheet", leverage_check(df["Debt"]))

# --------------------------------------------------
# VALUATION MODULE
# --------------------------------------------------
st.subheader("💰 Valuation Snapshot")

if sector == "IT Services":
    pe = 20
elif sector == "Banking":
    pe = 15
elif sector == "FMCG":
    pe = 25
else:
    pe = 18

df["EPS (Index)"] = df["PAT"] / 1000
df["Implied Value"] = df["EPS (Index)"] * pe

st.write(f"Assumed P/E Multiple: **{pe}x**")
st.metric("Implied Equity Value (Index)", round(df["Implied Value"].iloc[-1], 2))
st.caption("Simplified relative valuation for educational purposes.")

# --------------------------------------------------
# CONVICTION METER
# --------------------------------------------------
st.subheader("📈 Conviction Meter")

warnings = 0
if "⚠️" in earnings_quality(df["PAT"], df["OCF"]):
    warnings += 1
if "⚠️" in leverage_check(df["Debt"]):
    warnings += 1

if warnings >= 2:
    st.error("Conviction Weakening")
elif warnings == 1:
    st.warning("Conviction Neutral")
else:
    st.success("Conviction Strong")

# --------------------------------------------------
# IC NOTE PDF EXPORT
# --------------------------------------------------
def generate_ic_note(company, sector, df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    pdf.cell(0, 10, f"Investment Committee Note: {company}", ln=True)
    pdf.cell(0, 8, f"Sector: {sector}", ln=True)
    pdf.ln(4)

    pdf.multi_cell(0, 8,
        f"Financial Snapshot:\n"
        f"Revenue Growth: {round(df['Revenue Growth %'].iloc[-1],2)}%\n"
        f"EBIT Margin: {round(df['EBIT Margin %'].iloc[-1],2)}%\n"
    )

    pdf.ln(2)
    pdf.multi_cell(0, 8,
        "Key Risks:\n"
        "- Margin pressure\n"
        "- Balance sheet discipline\n"
    )

    pdf.ln(2)
    pdf.multi_cell(0, 8,
        "Conclusion:\n"
        "Company fundamentals remain stable with risks requiring monitoring."
    )

    return pdf

st.subheader("📄 Export IC Note")

if st.button("Download IC Note (PDF)"):
    pdf = generate_ic_note(company, sector, df)
    pdf.output("IC_Note.pdf")
    with open("IC_Note.pdf", "rb") as f:
        st.download_button(
            "Click to Download IC Note",
            f,
            file_name="IC_Note.pdf"
        )

# --------------------------------------------------
# FINAL SUMMARY
# --------------------------------------------------
st.subheader("🧠 Analyst Summary")

st.write(
    f"{company} demonstrates clear trends in revenue and profitability. "
    "Sector-specific factors and balance sheet movements remain key monitorables. "
    "This system is designed to support structured equity research decision-making."
)

st.caption("⚠️ Educational equity research system. Not investment advice.")
