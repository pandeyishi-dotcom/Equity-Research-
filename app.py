import streamlit as st
import yfinance as yf
import pandas as pd

# ----------------------------------
# APP CONFIG
# ----------------------------------
st.set_page_config(page_title="Analyst Brain", layout="wide")
st.title("🧠 Analyst Brain")
st.caption("Autonomous Equity Research Intelligence | NSE/BSE Listed Companies")

# ----------------------------------
# COMPANY UNIVERSE
# ----------------------------------
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

# ----------------------------------
# DATA LOADER
# ----------------------------------
@st.cache_data
def load_data(ticker):
    stock = yf.Ticker(ticker)
    fin = stock.financials.T
    cf = stock.cashflow.T
    bs = stock.balance_sheet.T
    return fin, cf, bs

financials, cashflow, balance = load_data(ticker)

# ----------------------------------
# SAFE COLUMN EXTRACTION
# ----------------------------------
def safe_col(df, possible_names):
    for col in possible_names:
        if col in df.columns:
            return df[col]
    return None

revenue = safe_col(financials, ["Total Revenue", "Revenue"])
ebit = safe_col(financials, ["Ebit", "Operating Income"])
pat = safe_col(financials, ["Net Income"])
ocf = safe_col(cashflow, ["Total Cash From Operating Activities"])
debt = safe_col(balance, ["Total Debt"])

# ----------------------------------
# BUILD CLEAN ANALYSIS DF
# ----------------------------------
df = pd.DataFrame()
df["Revenue"] = revenue
df["PAT"] = pat

if ebit is not None:
    df["EBIT"] = ebit
    df["EBIT Margin %"] = (df["EBIT"] / df["Revenue"]) * 100
else:
    df["EBIT Margin %"] = None

df["Revenue Growth %"] = df["Revenue"].pct_change() * 100
df = df.dropna().tail(5)

# ----------------------------------
# SNAPSHOT
# ----------------------------------
st.subheader(f"📊 Company Snapshot — {company_name}")
st.dataframe(df.round(2), use_container_width=True)

# ----------------------------------
# ANALYST LOGIC
# ----------------------------------
def earnings_quality(pat, ocf):
    try:
        if pat.iloc[-1] > pat.iloc[-2] and ocf.iloc[-1] < ocf.iloc[-2]:
            return "⚠️ Profit rising but cash flow weakening"
        else:
            return "Earnings supported by cash flow"
    except:
        return "Cash flow data insufficient"

def leverage_check(debt):
    try:
        if debt.iloc[-1] > debt.iloc[-2]:
            return "⚠️ Rising leverage"
        else:
            return "Debt stable"
    except:
        return "Debt data unavailable"

def revenue_trend(growth):
    if growth.iloc[-1] > 10:
        return "Strong revenue momentum"
    elif growth.iloc[-1] > 0:
        return "Moderating growth"
    else:
        return "⚠️ Revenue contraction"

# ----------------------------------
# WHAT CHANGED
# ----------------------------------
st.subheader("🔍 What Changed Recently")

col1, col2 = st.columns(2)

with col1:
    st.metric("Revenue Trend", revenue_trend(df["Revenue Growth %"]))
    st.metric("Margin Trend",
              "Expanding" if df["EBIT Margin %"].iloc[-1] > df["EBIT Margin %"].iloc[-2]
              if df["EBIT Margin %"].notna().all()
              else "Margin data unavailable")

with col2:
    st.metric("Earnings Quality", earnings_quality(pat, ocf))
    st.metric("Balance Sheet", leverage_check(debt))

# ----------------------------------
# LIVING THESIS
# ----------------------------------
st.subheader("🧾 Living Investment Thesis")

st.markdown("**Bull Case**")
st.write("• Established business with strong market presence")
st.write("• Consistent revenue generation across cycles")

st.markdown("**Bear Case**")
st.write("• Margin or leverage pressures may impact returns")
st.write("• Cash flow discipline needs monitoring")

# ----------------------------------
# CONVICTION METER
# ----------------------------------
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

# ----------------------------------
# ANALYST SUMMARY
# ----------------------------------
st.subheader("🧠 Analyst Summary")

st.write(
    f"{company_name} shows stable operating fundamentals with consistent revenue performance. "
    "However, balance sheet trends and cash flow quality remain key variables to track. "
    "Long-term conviction depends on sustaining profitability without increasing financial risk."
)

st.caption("⚠️ Educational equity research tool. Not investment advice.")
