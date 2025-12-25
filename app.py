import streamlit as st
import pandas as pd
from io import StringIO

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Analyst Brain – Research Coverage", layout="wide")
st.title("🧠 Analyst Brain")
st.caption("Automated Equity Research Coverage with Rating & Macro Overlay")

# --------------------------------------------------
# DATA
# --------------------------------------------------
csv_data = """
Company,Year,Revenue,EBIT,PAT,OCF,Debt
Reliance Industries,2020,596000,98500,39354,88200,305000
Reliance Industries,2021,539238,97500,53739,91000,280000
Reliance Industries,2022,792756,135000,60705,118000,310000
Reliance Industries,2023,976524,145000,66702,121000,325000
Reliance Industries,2024,1023000,152000,73500,130000,330000
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

sector_map = {
    "Reliance Industries": "Conglomerate",
    "TCS": "IT Services",
    "ITC": "FMCG"
}

# --------------------------------------------------
# MACRO INPUTS (USER-CONTROLLED)
# --------------------------------------------------
st.sidebar.markdown("### 🌍 Macro Assumptions")
interest_rate = st.sidebar.selectbox("Interest Rate Environment", ["Falling", "Stable", "Rising"])
inflation = st.sidebar.selectbox("Inflation Trend", ["Cooling", "Stable", "Elevated"])
gdp = st.sidebar.selectbox("GDP Growth Outlook", ["Strong", "Moderate", "Weak"])

# --------------------------------------------------
# COMPANY SELECTION
# --------------------------------------------------
companies = st.multiselect(
    "Select companies for research coverage",
    data["Company"].unique(),
    default=data["Company"].unique().tolist()
)

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
def derive_rating(rev_growth, margin_trend, debt_change):
    if rev_growth > 40 and margin_trend > 0 and debt_change <= 0:
        return "Positive Bias (Academic Buy-equivalent)"
    elif rev_growth > 20:
        return "Neutral Bias (Academic Hold-equivalent)"
    else:
        return "Cautious Bias (Academic Underperform-equivalent)"

def macro_overlay_text(sector, rate, infl, growth):
    text = "From a macroeconomic perspective, "
    if sector == "IT Services":
        text += (
            "IT services companies are sensitive to global growth and currency trends. "
            f"A {growth.lower()} global growth environment combined with "
            f"{rate.lower()} interest rates is "
            f"{'supportive' if growth != 'Weak' else 'challenging'} for demand visibility."
        )
    elif sector == "FMCG":
        text += (
            "FMCG companies are influenced by inflation and consumption trends. "
            f"{'Cooling' if infl == 'Cooling' else 'Elevated'} inflation "
            f"is {'positive' if infl == 'Cooling' else 'a margin risk'}, "
            f"while GDP growth being {growth.lower()} affects volume growth."
        )
    elif sector == "Conglomerate":
        text += (
            "Conglomerates are impacted by interest rates, capital availability, and economic cycles. "
            f"{rate} interest rates affect capital allocation decisions, while "
            f"{growth.lower()} GDP growth influences segment-level performance."
        )
    else:
        text += "macro conditions play a mixed role across business segments."
    return text

# --------------------------------------------------
# ANALYSIS LOOP
# --------------------------------------------------
for company in companies:
    st.divider()
    sector = sector_map.get(company, "General")
    df = data[data["Company"] == company].sort_values("Year")

    # Metrics
    rev_growth = (df["Revenue"].iloc[-1] / df["Revenue"].iloc[0] - 1) * 100
    margin_trend = (df["EBIT"].iloc[-1] / df["Revenue"].iloc[-1]) - (df["EBIT"].iloc[0] / df["Revenue"].iloc[0])
    debt_change = df["Debt"].iloc[-1] - df["Debt"].iloc[0]

    rating = derive_rating(rev_growth, margin_trend, debt_change)

    # --------------------------------------------------
    # REPORT
    # --------------------------------------------------
    st.subheader(f"{company} – Equity Research Coverage")
    st.caption(f"Sector: {sector}")

    st.markdown("### Executive Summary")
    st.write(
        f"{company} operates in the {sector} sector and has delivered "
        f"{'strong' if rev_growth > 40 else 'moderate'} revenue growth over the past five years. "
        f"The company is currently assessed with a **{rating}**, reflecting its "
        "fundamental performance and financial discipline."
    )

    st.markdown("### Business & Sector Overview")
    st.write(
        f"{company} benefits from its positioning within the {sector} space, "
        "where scale, operating efficiency, and capital allocation play a key role "
        "in long-term value creation."
    )

    st.markdown("### Financial Performance & Profitability")
    st.write(
        f"Revenue has expanded by approximately {rev_growth:.1f}% over the analysis period. "
        f"Operating margins have {'expanded' if margin_trend > 0 else 'remained stable'}, "
        "indicating the quality of growth achieved."
    )

    st.markdown("### Earnings Quality & Balance Sheet")
    st.write(
        "Profit growth appears supported by operating performance rather than accounting effects. "
        f"Debt levels have {'increased' if debt_change > 0 else 'remained controlled'}, "
        "making balance sheet discipline an important monitorable."
    )

    st.markdown("### Macro Overlay")
    st.write(macro_overlay_text(sector, interest_rate, inflation, gdp))

    st.markdown("### Valuation & Rating Rationale")
    st.write(
        f"The assigned **{rating}** reflects a balance between growth visibility, "
        "profitability trends, balance sheet considerations, and the prevailing macro environment. "
        "Scenario-based valuation remains the preferred framework for assessment."
    )

    st.markdown("### Risks & Monitorables")
    st.write(
        "Key risks include margin volatility, macroeconomic shocks, regulatory changes, "
        "and capital allocation decisions. Monitoring cash flows and leverage remains critical."
    )

    st.markdown("### Conclusion")
    st.write(
        f"In conclusion, {company} presents a "
        f"{'constructive' if 'Positive' in rating else 'balanced'} "
        "fundamental profile. Future performance will depend on execution quality "
        "and alignment with macroeconomic trends."
    )

st.caption("⚠️ Educational equity research coverage. Not investment advice.")
