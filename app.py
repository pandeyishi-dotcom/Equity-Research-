import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# ----------------------------
# APP CONFIG
# ----------------------------
st.set_page_config(page_title="Analyst Brain", layout="wide")
st.title("🧠 Analyst Brain")
st.caption("Autonomous Equity Research Intelligence | NSE/BSE Companies")

# ----------------------------
# COMPANY UNIVERSE (REAL NSE)
# ----------------------------
companies = {
    "Reliance Industries": "RELIANCE.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "ITC": "ITC.NS",
    "ICICI Bank": "ICICIBANK.NS"
}

company_name = st.selectbox("Select Company", list(companies.keys()))
ticker = companies[company_name]

# ----------------------------
# FETCH DATA (AUTO)
# ----------------------------
@st.cache_data
def load_data(ticker):
    stock = yf.Ticker(ticker)
    financials = stock.financials.T
    cashflow = stock.cashflow.T
    balance = stock.balance_sheet.T
    info = stock.info
    return financials, cashflow, balance, info

financials, cashflow, balance, info = load_data(ticker)

# ----------------------------
# CLEAN DATA
# ----------------------------
df = financials.copy()
df["Revenue"] = df["Total Revenue"]
df["EBIT"] = df["Ebit"]
df["PAT"] = df["Net Income"]

df = df[["Revenue", "EBIT", "PAT"]].dropna().tail(5)

df["Revenue Growth %"] = df["Revenue"].pct_change() * 100
df["EBIT Margin %"] = (df["EBIT"] / df["Revenue"]) * 100

# ----------------------------
# SNAPSHOT
# ----------------------------
st.subheader(f"📊 Company Snapshot — {company_name}")
st.dataframe(df.round(2), use_container_width=True)

# ----------------------------
# ANALYST LOGIC
# ----------------------------
def earnings_quality(fin, cf):
    try:
        profit_growth = fin["PAT"].iloc[-1] - fin["PAT"].iloc[-2]
        cash = cf["Total Cash From Operating Activities"].dropna().tail(2)
        cash_growth = cash.iloc[-1] - cash.iloc[-2]
        if profit_growth > 0 and cash_growth < 0:
            return "⚠️ Profit rising but operating cash flow weakening"
        else:
            return "Healthy earnings backed by cash flow"
    except:
        return "Cash flow data insufficient"

def leverage_check(balance):
    try:
        debt = balance["Total Debt"].dropna().tail(2)
        if debt.iloc[-1] > debt.iloc[-2]:
            return "⚠️ Rising leverage observed"
        else:
            return "Debt levels stable"
    except:
        return "Debt data unavailable"

def revenue_trend(df):
    if df["Revenue Growth %"].iloc[-1] > 10:
        return "Revenue momentum strong"
    elif df["Revenue Growth %"].iloc[-1] > 0:
        return "Revenue growth moderating"
    else:
        return "⚠️ Revenue contraction"

# ----------------------------
# WHAT CHANGED
# ----------------------------
st.subheader("🔍 What Changed Recently")

col1, col2 = st.columns(2)

with col1:
    st.metric("Revenue Trend", revenue_trend(df))
    st.metric("Margin Trend",
              "Expanding" if df["EBIT Margin %"].iloc[-1] > df["EBIT Margin %"].iloc[-2]
              else "Compressing")

with col2:
    st.metric("Earnings Quality", earnings_quality(df, cashflow))
    st.metric("Balance Sheet", leverage_check(balance))

# ----------------------------
# LIVING THESIS
# ----------------------------
st.subheader("🧾 Living Investment Thesis")

bull = [
    "Established business with strong market presence",
    "Consistent revenue generation across cycles"
]

bear = [
    "Margin pressure or leverage could impact returns",
    "Cash flow discipline remains a key monitor"
]

st.markdown("**Bull Case**")
for b in bull:
    st.write("•", b)

st.markdown("**Bear Case**")
for b in bear:
    st.write("•", b)

# ----------------------------
# CONVICTION METER
# ----------------------------
st.subheader("📈 Conviction Meter")

warnings = 0
if "⚠️" in earnings_quality(df, cashflow):
    warnings += 1
if "⚠️" in leverage_check(balance):
    warnings += 1

if warnings >= 2:
    st.error("Conviction Weakening")
elif warnings == 1:
    st.warning("Conviction Neutral — Monitor Closely")
else:
    st.success("Conviction Stable to Improving")

# ----------------------------
# ANALYST SUMMARY
# ----------------------------
st.subheader("🧠 Analyst Summary")

summary = f"""
{company_name} continues to demonstrate stable business fundamentals with consistent revenue performance.
However, changes in leverage and cash flow quality require monitoring.
Long-term conviction depends on sustaining margins and balance sheet discipline.
"""

st.write(summary)

st.caption("⚠️ Educational equity research tool. Not investment advice.")
