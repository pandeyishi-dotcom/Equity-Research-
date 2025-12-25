import streamlit as st
import yfinance as yf
import pandas as pd

# -------------------------------------------------
# APP CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Analyst Brain", layout="wide")
st.title("🧠 Analyst Brain")
st.caption("Autonomous Equity Research Intelligence | NSE Listed Companies")

# -------------------------------------------------
# COMPANY UNIVERSE
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
# LOAD DATA
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
# SAFE COLUMN FETCH
# -------------------------------------------------
def get_column(df, names):
    for n in names:
        if n in df.columns:
            return df[n]
    return None

revenue = get_column(financials, ["Total Revenue", "Revenue"])
pat = get_column(financials, ["Net Income"])
ebit = get_column(financials, ["Ebit", "Operating Income"])
ocf = get_column(cashflow, ["Total Cash From Operating Activities"])
debt = get_column(balance, ["Total Debt"])

# -------------------------------------------------
# BUILD ANALYSIS TABLE
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
# ANALYST LOGIC
# -------------------------------------------------
def revenue_trend(series):
    if len(series) < 1:
        return "Revenue data unavailable"
    last = series.iloc[-1]
    if last > 10:
        return "Strong revenue momentum"
    elif last > 0:
        return "Moderating growth"
    else:
        return "⚠️ Revenue contraction"

def margin_trend(df):
    if "EBIT Margin %" not in df.columns:
        return "Margin data unavailable"
    if df["EBIT Margin %"].isna().any():
        return "Margin data unavailable"
    if len(df) < 2:
        return "Margin data insufficient"
    if df["EBIT Margin %"].iloc[-1] > df["EBIT Margin %"].iloc[-2]:
        return "Expanding"
    else:
        return "Compressing"

def earnings_quality(pat, ocf):
    if pat is None or ocf is None:
        return "Cash flow data unavailable"
    if len(pat) < 2 or len(ocf) < 2:
        return "Cash flow data insufficient"
    if pat.iloc[-1] > pat.iloc[-2] and ocf.iloc[-1] < ocf.iloc[-2]:
        return "⚠️ Profit rising but cash flow weakening"
    return "Earnings supported by cash flow"

def leverage_check(debt):
    if debt is None or len(debt) < 2:
        return "Debt data unavailable"
    if debt.iloc[-1] > debt.iloc[-2]:
        return "⚠️ Rising leverage"
    return "Debt stable"

# -------------------------------------------------
# WHAT CHANGED
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
# INVESTMENT THESIS
# -------------------------------------------------
st.subheader("🧾 Living Investment Thesis")

st.markdown("**Bull Case**")
st.write("• Strong business franchise")
st.write("• Consistent revenue generation")

st.markdown("**Bear Case**")
st.write("• Margin or leverage pressure")
st.write("• Cash flow discipline risk")

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
    f"{company_name} shows stable operating performance. "
    "However, balance sheet trends and cash flow quality require monitoring. "
    "Long-term conviction depends on sustainable profitability."
)

st.caption("⚠️ Educational equity research tool. Not investment advice.")
