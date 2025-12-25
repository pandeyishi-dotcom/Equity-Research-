import streamlit as st
import pandas as pd
from io import StringIO, BytesIO
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

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
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #11142a, #0b0e1a);
}
.infocard {
    background: linear-gradient(135deg, rgba(127,92,255,0.15), rgba(77,220,255,0.07));
    border-radius: 20px;
    padding: 26px;
    margin-bottom: 30px;
    border: 1px solid rgba(255,255,255,0.08);
}
.strip {
    background: rgba(255,255,255,0.06);
    border-left: 6px solid #7f5cff;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 14px;
}
.badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
.badge-init { background:#00c896; color:black; }
.badge-up { background:#7f5cff; color:black; }
.badge-down { background:#ff6b6b; color:black; }
.badge-maintain { background:rgba(255,255,255,0.25); color:white; }
.final-take {
    background: linear-gradient(90deg,#7f5cff,#4ddcff);
    color:black;
    padding:18px;
    border-radius:14px;
    font-weight:600;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# TITLE
# ==================================================
st.markdown("## 🧠 Analyst Brain Terminal")
st.caption("Institutional-Style Infographic Equity Research")

# ==================================================
# DATA
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
df = pd.read_csv(StringIO(coverage_csv))

sector_map = {
    "Reliance Industries": "Conglomerate",
    "TCS": "IT Services",
    "ITC": "FMCG"
}

# ==================================================
# LOGIC
# ==================================================
def rating_logic(g, m, d):
    if g > 40 and m > 0 and d <= 0:
        return "Positive Bias", "Upgrade", "badge-up"
    if g < 20 and m < 0:
        return "Cautious Bias", "Downgrade", "badge-down"
    if g > 20:
        return "Neutral Bias", "Maintained", "badge-maintain"
    return "Neutral Bias", "Initiating Coverage", "badge-init"

# ==================================================
# COMPANY SELECT
# ==================================================
companies = st.multiselect(
    "Select companies",
    df["Company"].unique(),
    default=df["Company"].unique().tolist(),
    key="companies"
)

# ==================================================
# MAIN LOOP
# ==================================================
for company in companies:
    dfx = df[df["Company"] == company].sort_values("Year")
    sector = sector_map.get(company, "General")

    g = (dfx["Revenue"].iloc[-1] / dfx["Revenue"].iloc[0] - 1) * 100
    m = (dfx["EBIT"].iloc[-1] / dfx["Revenue"].iloc[-1]) - \
        (dfx["EBIT"].iloc[0] / dfx["Revenue"].iloc[0])
    d = dfx["Debt"].iloc[-1] - dfx["Debt"].iloc[0]

    rating, badge_text, badge_class = rating_logic(g, m, d)

    st.markdown('<div class="infocard">', unsafe_allow_html=True)
    st.markdown(f"### {company}")
    st.markdown(f"<span class='badge {badge_class}'>{badge_text}</span>  **{rating}**", unsafe_allow_html=True)
    st.caption(f"Sector: {sector}")

    st.markdown('<div class="strip">📈 Growth</div>', unsafe_allow_html=True)
    st.write(f"Revenue grew {g:.1f}% over the period.")

    st.markdown('<div class="strip">💰 Profitability</div>', unsafe_allow_html=True)
    st.write("Margins have " + ("expanded." if m > 0 else "remained stable."))

    st.markdown('<div class="strip">🏦 Balance Sheet</div>', unsafe_allow_html=True)
    st.write("Debt has " + ("increased." if d > 0 else "remained controlled."))

    st.markdown("**Variant View**")
    st.write("Bull: Margin expansion")
    st.write("Base: Stable execution")
    st.write("Bear: Leverage risk")

    st.markdown('<div class="final-take">', unsafe_allow_html=True)
    st.write(f"{company} remains a {rating.lower()} idea in coverage.")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button(f"📄 Export {company} PDF", key=f"pdf_{company}"):
        buffer = BytesIO()
        with PdfPages(buffer) as pdf:
            fig, ax = plt.subplots(figsize=(8.5, 11))
            ax.axis("off")
            ax.text(0.05, 0.9, f"{company} Research Note", fontsize=18)
            ax.text(0.05, 0.85, f"Rating: {rating}", fontsize=12)
            ax.text(0.05, 0.8, f"Revenue Growth: {g:.1f}%", fontsize=12)
            pdf.savefig(fig)
            plt.close(fig)
        buffer.seek(0)
        st.download_button(
            "⬇️ Download PDF",
            buffer,
            file_name=f"{company}_Research.pdf",
            mime="application/pdf",
            key=f"dl_{company}"
        )

    st.markdown('</div>', unsafe_allow_html=True)

st.caption("⚠️ Educational use only. Not investment advice.")
