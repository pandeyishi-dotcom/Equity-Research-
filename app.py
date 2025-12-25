import streamlit as st
import pandas as pd
from io import StringIO

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Analyst Brain Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# DARK TERMINAL + INFOGRAPHIC CSS
# ==================================================
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top left, #1b1f3b, #0b0e1a);
    color: #eaeaf0;
    font-family: Inter, sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #11142a, #0b0e1a);
}

/* Headers */
h1, h2, h3 {
    color: #ffffff;
}

/* Infographic cards */
.infocard {
    background: linear-gradient(135deg, rgba(127,92,255,0.12), rgba(77,220,255,0.05));
    border-radius: 18px;
    padding: 26px;
    margin-bottom: 28px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 15px 40px rgba(0,0,0,0.45);
}

/* Section strips */
.strip {
    background: rgba(255,255,255,0.05);
    border-left: 5px solid #7f5cff;
    padding: 16px 20px;
    border-radius: 12px;
    margin-bottom: 16px;
}

/* Signals */
.signal-good {
    background: rgba(0,200,150,0.14);
    border-left: 5px solid #00c896;
    padding: 16px;
    border-radius: 12px;
}
.signal-watch {
    background: rgba(255,180,0,0.14);
    border-left: 5px solid #ffb400;
    padding: 16px;
    border-radius: 12px;
}

/* Labels */
.label {
    color: #b0b3c7;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Final take */
.final-take {
    background: linear-gradient(90deg, #7f5cff, #4ddcff);
    color: black;
    padding: 18px;
    border-radius: 14px;
    font-weight: 600;
    margin-top: 18px;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #7f5cff, #4ddcff);
    color: black;
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 600;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# TITLE
# ==================================================
st.markdown("<h1>🧠 Analyst Brain Terminal</h1>", unsafe_allow_html=True)
st.caption("Hybrid Equity Research Platform • Screener + Infographic Coverage")

# ==================================================
# SIDEBAR MODE
# ==================================================
mode = st.sidebar.radio(
    "Mode",
    ["🔍 Market Screener", "📘 Coverage Universe (Infographic Research)"]
)

# ==================================================
# DATA — SCREENER (WIDE)
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
# DATA — COVERAGE (DEEP)
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
# MACRO INPUTS
# ==================================================
st.sidebar.markdown("### 🌍 Macro Assumptions")
interest_rate = st.sidebar.selectbox("Interest Rates", ["Falling", "Stable", "Rising"])
inflation = st.sidebar.selectbox("Inflation", ["Cooling", "Stable", "Elevated"])
gdp = st.sidebar.selectbox("GDP Growth", ["Strong", "Moderate", "Weak"])

# ==================================================
# HELPER FUNCTIONS
# ==================================================
def derive_rating(rev_growth, margin_change, debt_change):
    if rev_growth > 40 and margin_change > 0 and debt_change <= 0:
        return "Positive Bias (Academic Buy-equivalent)"
    elif rev_growth > 20:
        return "Neutral Bias (Academic Hold-equivalent)"
    else:
        return "Cautious Bias (Academic Underperform-equivalent)"

def macro_overlay(sector):
    if sector == "IT Services":
        return f"Global demand cycles dominate IT services. A {gdp.lower()} growth outlook with {interest_rate.lower()} rates is {'supportive' if gdp != 'Weak' else 'challenging'}."
    if sector == "FMCG":
        return f"Consumption and inflation trends drive FMCG performance. {inflation} inflation and {gdp.lower()} GDP growth influence volume and margin stability."
    if sector == "Conglomerate":
        return f"Conglomerates are sensitive to capital availability. {interest_rate} rates and {gdp.lower()} GDP growth affect allocation and execution."
    return "Macro conditions remain mixed."

# ==================================================
# MODE 1 — SCREENER
# ==================================================
if mode == "🔍 Market Screener":
    st.subheader("🔍 Market Screener — Idea Discovery")

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

    st.markdown('<div class="infocard">', unsafe_allow_html=True)
    st.write(
        "This module is strictly for **idea discovery**. "
        "Stocks shortlisted here can be promoted into the Coverage Universe."
    )
    st.dataframe(filtered, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==================================================
# MODE 2 — INFOGRAPHIC COVERAGE
# ==================================================
if mode == "📘 Coverage Universe (Infographic Research)":
    st.subheader("📘 Coverage Universe — Visual Research Notes")

    companies = st.multiselect(
        "Select companies under coverage",
        coverage_df["Company"].unique(),
        default=coverage_df["Company"].unique().tolist()
    )

    for company in companies:
        sector = sector_map.get(company, "General")
        df = coverage_df[coverage_df["Company"] == company].sort_values("Year")

        rev_growth = (df["Revenue"].iloc[-1] / df["Revenue"].iloc[0] - 1) * 100
        margin_change = (df["EBIT"].iloc[-1] / df["Revenue"].iloc[-1]) - \
                        (df["EBIT"].iloc[0] / df["Revenue"].iloc[0])
        debt_change = df["Debt"].iloc[-1] - df["Debt"].iloc[0]

        rating = derive_rating(rev_growth, margin_change, debt_change)

        st.markdown('<div class="infocard">', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="label">Coverage Snapshot</div>
        <h2>{company}</h2>
        <p><b>Sector:</b> {sector} &nbsp; | &nbsp; <b>Rating:</b> {rating}</p>
        """, unsafe_allow_html=True)

        st.markdown('<div class="strip">', unsafe_allow_html=True)
        st.markdown("**📈 Growth**")
        st.write(f"Revenue expanded by {rev_growth:.1f}%, indicating sustained scale expansion.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="strip">', unsafe_allow_html=True)
        st.markdown("**💰 Profitability**")
        st.write(f"Margins have {'improved' if margin_change > 0 else 'remained stable'}, reflecting operating discipline.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="strip">', unsafe_allow_html=True)
        st.markdown("**🏦 Balance Sheet**")
        st.write(f"Debt levels have {'risen' if debt_change > 0 else 'remained controlled'}, making leverage a key monitorable.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="strip">', unsafe_allow_html=True)
        st.markdown("**🌍 Macro Overlay**")
        st.write(macro_overlay(sector))
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="signal-good">', unsafe_allow_html=True)
            st.markdown("**What’s Working**")
            st.write("• Scale\n• Margin stability\n• Business resilience")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="signal-watch">', unsafe_allow_html=True)
            st.markdown("**What to Watch**")
            st.write("• Capital allocation\n• Debt trajectory\n• Macro sensitivity")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="final-take">', unsafe_allow_html=True)
        st.write(
            f"{company} shows a "
            f"{'constructive' if 'Positive' in rating else 'balanced'} "
            "fundamental setup, with execution quality and macro alignment as key drivers."
        )
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

st.caption("⚠️ Educational equity research terminal. Not investment advice.")
