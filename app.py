import streamlit as st
import pandas as pd

# --------------------------------
# APP CONFIG
# --------------------------------
st.set_page_config(page_title="Analyst Brain", layout="wide")
st.title("🧠 Analyst Brain")
st.caption("Equity Research Intelligence | Fundamentals-Based Analysis")

# --------------------------------
# LOAD FUNDAMENTALS
# --------------------------------
@st.cache_data
def load_fundamentals():
    return pd.read_csv("fundamentals.csv")

data = load_fundamentals()

companies = data["Company"].unique().tolist()
company = st.selectbox("Select Company", companies)

df = data[data["Company"] == company].sort_values("Year")

# --------------------------------
# METRICS
# --------------------------------
df["Revenue Growth %"] = df["Revenue"].pct_change() * 100
df["EBIT Margin %"] = (df["EBIT"] / df["Revenue"]) * 100

# --------------------------------
# SNAPSHOT
# --------------------------------
st.subheader(f"📊 Company Snapshot — {company}")
st.dataframe(df.round(2), use_container_width=True)

# --------------------------------
# ANALYST LOGIC
# --------------------------------
def revenue_trend(series):
    if series.iloc[-1] > 10:
        return "Strong revenue momentum"
    elif series.iloc[-1] > 0:
        return "Moderating growth"
    else:
        return "⚠️ Revenue slowdown"

def margin_trend(series):
    if series.iloc[-1] > series.iloc[-2]:
        return "Expanding"
    else:
        return "Compressing"

def earnings_quality(pat, ocf):
    if pat.iloc[-1] > pat.iloc[-2] and ocf.iloc[-1] < ocf.iloc[-2]:
        return "⚠️ Profit rising but cash flow weakening"
    return "Earnings supported by cash flow"

def leverage_check(debt):
    if debt.iloc[-1] > debt.iloc[-2]:
        return "⚠️ Rising leverage"
    return "Debt stable"

# --------------------------------
# WHAT CHANGED
# --------------------------------
st.subheader("🔍 What Changed Recently")

col1, col2 = st.columns(2)

with col1:
    st.metric("Revenue Trend", revenue_trend(df["Revenue Growth %"]))
    st.metric("Margin Trend", margin_trend(df["EBIT Margin %"]))

with col2:
    st.metric("Earnings Quality", earnings_quality(df["PAT"], df["OCF"]))
    st.metric("Balance Sheet", leverage_check(df["Debt"]))

# --------------------------------
# THESIS
# --------------------------------
st.subheader("🧾 Living Investment Thesis")

st.markdown("**Bull Case**")
st.write("• Stable revenue growth with operating leverage")
st.write("• Improving profitability metrics")

st.markdown("**Bear Case**")
st.write("• Margin pressure or leverage risk")
st.write("• Cash flow divergence risk")

# --------------------------------
# CONVICTION
# --------------------------------
st.subheader("📈 Conviction Meter")

warnings = 0
if "⚠️" in earnings_quality(df["PAT"], df["OCF"]):
    warnings += 1
if "⚠️" in leverage_check(df["Debt"]):
    warnings += 1

if warnings >= 2:
    st.error("Conviction Weakening")
elif warnings == 1:
    st.warning("Conviction Neutral — Monitor Closely")
else:
    st.success("Conviction Strong")

# --------------------------------
# SUMMARY
# --------------------------------
st.subheader("🧠 Analyst Summary")

st.write(
    f"{company} demonstrates consistent operating performance with visible trends in revenue "
    "and margins. Key risks remain linked to leverage and cash flow sustainability. "
    "Ongoing monitoring of fundamentals is essential."
)

st.caption("⚠️ Educational equity research prototype. Not investment advice.")
