import streamlit as st
import yfinance as yf
import pandas as pd

# -------------------------------------------------
# APP CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Analyst Brain", layout="wide")
st.title("🧠 Analyst Brain")
st.caption("Autonomous Equity Research Intelligence | NSE/BSE Listed Companies")

# -------------------------------------------------
# COMPANY UNIVERSE (REAL NSE)
# -------------------------------------------------
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

# -------------------------------------------------
# DATA LOADER
# -------------------------------------------------
@st.cache_data
def load_data(ticker):
    stock = yf.Ticker(ticker)
    fin = stock.financials.T
    cf = stock.cashflow.T
    bs = stock.balance_sheet.T
    return fin, cf, bs

financials, cashflow, balance = load_data(ticker)

# -------------------------------------------------
# SAFE COLUMN FETCHER
# -------------------------------------------------
def safe_column(df, possible_names):
    for col in possible_names:
        if col in df.columns:
            return df[col]
    return None

revenue = safe_column(financials, ["Total Revenue", "Revenue"])
pat = safe_column(financials, ["Net Income"])
ebit = safe_column(financials, ["Ebit", "Operating Income"])
ocf = safe_column(cashflow, ["Total Cash From Operating Activities"])
debt = safe_column(balance, ["Total Debt"])

# -------------------------------------------------
# BUILD ANALYSIS DATAFRAME
# -------------------------------------------------
df = pd.DataFrame()

if revenue is not None:
    df["Revenue"] = revenue

if pat is not None:
    df["PAT"] = pat

if ebit is not None:
    df["EBIT"] = ebit
    df["EBIT Margin %"] = (df["EBIT"] / df["Revenue"]) * 100
else:
    df["EBIT Margin %"] = None

df["Revenue Growth %"] = df["Revenue"].pct_change() * 100
df = df.dropna().tail(5)

# -------------------------------------------------
# SNAPSHOT
# -------------------------------------------------
st.subheader(f"📊 Company Snapshot — {company_name}")
st.dataframe(df.round(2), use_container_width=True)

# -------------------------------------------------
# ANALYST LOGIC FUNCTIONS
# -------------------------------------------------
def revenue_trend(growth):
    try:
        if growth.iloc[-1] > 10:
            return "Strong revenue momentum"
        elif growth.iloc[-1] > 0:
            return "Moderating growth"
        else:
            return "⚠️ Revenue contraction"
    except:
        return "Revenue data insufficient"

def earnings_quality(pat, ocf):
    try:
        if pat.iloc[-1] > pat.iloc[-2] and ocf.iloc[-1] < ocf.iloc[-2]:
            return "⚠️ Profit rising but cash flow weakening"
        else:
            return "Earnings supported by cash flow"
    except:
        return "Cash flow data unavailable"

def leverage_check(debt):
    try:
        if debt.iloc[-1] > debt.iloc[-2]:
            return "⚠️ Rising leverage"
        else:
            return "Debt levels stable"
    except:
        return "Debt data unavailable"

def margin_trend(df):
    try:
        if df["EBIT Margin %"].notna().all() and len(df) >= 2:
            if df["EBIT Margin %"].iloc[-1] > df["EBIT Margin %"].iloc[-2]:
                return "Expanding"
            else:
                return "Compressing"
        else:
            return "Margin data unavailable"
    except:
        return "Margin data unavailable"

# -------------------------------------------------
# WHAT CHANGED SECTION
# -------------------------------------------------
st.subheader("🔍 What Changed Recently")

col1, col2 = st.columns(2)

with col1:
    st.metric("Revenue Trend", revenue_trend(df["Revenue Growth %"]))
    st.metric("Margin Trend", margin_trend(df))

with col2:
    st.metric("Earnings Quality", earnings_quality(pat, ocf))
    st.metric("Balance Sheet", leverage_check(debt))

# -------------------------------------------------
# LIVING INVESTMENT THESIS
# -------------------------------------------------
st.subheader("🧾 Living Investment Thesis")

st.markdown("**Bull Case**")
st.write("• Established business with strong market positioning")
st.write("• Consistent revenue generation across cycles")

st.markdown("**Bear Case**")
st.write("• Margin pressure or leverage may impact returns")
st.write("• Cash flow discipline remains a key monitor")

# -------------------------------------------------
# CONVICTION METER
# -------------------------------------------------
st.subheader("📈 Conviction Meter")

warnings = 0
if "⚠️" in earnings_quality(pat, ocf):
    warnings += 1
if "⚠️" in leverage_check(debt):
    warnings += 1

if warnings >= 2:
    st.error("Conviction Weakening")
elif warnings == 1:
    st.warning("Conviction Neutral — Monitor Closely")
else:
    st.success("Conviction Stable")

# -------------------------------------------------
# ANALYST SUMMARY
# -------------------------------------------------
st.subheader("🧠 Analyst Summary")

st.write(
    f"{company_name} exhibits stable operating fundamentals supported by consistent revenue trends. "
    "However, balance sheet movement and cash flow quality remain key variables to monitor. "
    "Long-term conviction depends on sustaining profitability without increasing financial risk."
)

st.caption("⚠️ Educational equity research tool. Not investment advice.")

