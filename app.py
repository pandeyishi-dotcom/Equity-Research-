import streamlit as st
import pandas as pd
from io import StringIO, BytesIO
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Analyst Brain Terminal",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# GLOBAL CSS + JS (ANIMATION + TERMINAL FEEL)
# ==================================================
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top left, #1b1f3b, #0b0e1a);
    color: #eaeaf0;
    font-family: 'Inter', sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #11142a, #0b0e1a);
}

/* Cards */
.card {
    background: rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.4);
    margin-bottom: 20px;
    transition: all 0.4s ease-in-out;
}
.card:hover {
    transform: translateY(-4px);
}

/* Animated metrics */
.metric {
    font-size: 28px;
    font-weight: 600;
    transition: all 0.6s ease;
}
.metric-label {
    font-size: 13px;
    color: #b0b3c7;
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

/* Tables */
thead tr th {
    background-color: #1b1f3b !important;
    color: white !important;
}
</style>

<script>
// Bloomberg-style keyboard navigation
document.addEventListener("keydown", function(e) {
    if (e.key === "1") {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
    if (e.key === "2") {
        document.querySelectorAll("section")[1]?.scrollIntoView({behavior: "smooth"});
    }
    if (e.key === "3") {
        document.querySelectorAll("section")[2]?.scrollIntoView({behavior: "smooth"});
    }
});
</script>
""", unsafe_allow_html=True)

# ==================================================
# DATA
# ==================================================
csv_data = """
Company,Year,Revenue,EBIT,PAT,Debt
Reliance Industries,2020,596000,98500,39354,305000
Reliance Industries,2021,539238,97500,53739,280000
Reliance Industries,2022,792756,135000,60705,310000
Reliance Industries,2023,976524,145000,66702,325000
Reliance Industries,2024,1023000,152000,73500,330000
TCS,2020,161541,40200,32430,15000
TCS,2021,164177,43000,32496,14000
TCS,2022,191754,47000,38327,13000
TCS,2023,225458,52000,42147,12000
TCS,2024,240893,56000,45000,11000
ITC,2020,44674,17000,15000,12000
ITC,2021,46395,18000,16000,11000
ITC,2022,54752,21000,18000,10000
ITC,2023,62615,24000,20000,9000
ITC,2024,70500,27000,22000,8000
"""

df_all = pd.read_csv(StringIO(csv_data))

# ==================================================
# SIDEBAR (MULTI-COMPANY MODE)
# ==================================================
st.sidebar.markdown("## 🧠 Analyst Brain Terminal")
mode = st.sidebar.radio("Mode", ["Single Company", "Compare Companies"])

companies = st.sidebar.multiselect(
    "Select Companies",
    df_all["Company"].unique(),
    default=["Reliance Industries"]
)

# ==================================================
# DATA PROCESS
# ==================================================
df_all["Revenue Growth %"] = df_all.groupby("Company")["Revenue"].pct_change() * 100
df_all["EBIT Margin %"] = df_all["EBIT"] / df_all["Revenue"] * 100

# ==================================================
# KPI DASHBOARD
# ==================================================
st.markdown("## 📊 Key Metrics")

cols = st.columns(len(companies))
for col, comp in zip(cols, companies):
    d = df_all[df_all["Company"] == comp].iloc[-1]
    with col:
        st.markdown(f"""
        <div class="card">
            <div class="metric-label">{comp}</div>
            <div class="metric">₹{int(d["Revenue"]):,}</div>
            <div class="metric-label">EBIT Margin: {d["EBIT Margin %"]:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

# ==================================================
# COMPARISON CHART
# ==================================================
st.markdown("## 📈 Revenue Comparison")

fig, ax = plt.subplots()
for comp in companies:
    d = df_all[df_all["Company"] == comp]
    ax.plot(d["Year"], d["Revenue"], label=comp)

ax.legend()
ax.grid(alpha=0.3)
ax.set_facecolor("#0b0e1a")
fig.patch.set_facecolor("#0b0e1a")
ax.tick_params(colors="white")
ax.yaxis.label.set_color("white")
ax.xaxis.label.set_color("white")
ax.title.set_color("white")

st.pyplot(fig)

# ==================================================
# REPORT-READY PRINT MODE
# ==================================================
st.markdown("## 🖨 Report Preview (Print-Ready)")
st.dataframe(
    df_all[df_all["Company"].isin(companies)].round(2),
    use_container_width=True
)

# ==================================================
# PDF EXPORT (DARK THEME)
# ==================================================
def export_pdf(df, companies):
    buffer = BytesIO()
    with PdfPages(buffer) as pdf:
        fig, ax = plt.subplots(figsize=(8, 11))
        ax.axis("off")
        ax.text(0.5, 0.7, "Equity Research Report", ha="center", fontsize=20)
        ax.text(0.5, 0.6, ", ".join(companies), ha="center", fontsize=14)
        pdf.savefig(fig)
        plt.close(fig)

        for comp in companies:
            d = df[df["Company"] == comp]
            fig, ax = plt.subplots(figsize=(8, 11))
            ax.axis("off")
            ax.text(0.05, 0.95, comp, fontsize=16, weight="bold")
            ax.text(
                0.05, 0.9,
                f"Revenue: {int(d.iloc[-1]['Revenue']):,}\n"
                f"EBIT Margin: {d.iloc[-1]['EBIT Margin %']:.2f}%\n"
                f"Debt: {int(d.iloc[-1]['Debt']):,}",
                fontsize=12,
                va="top"
            )
            pdf.savefig(fig)
            plt.close(fig)

    buffer.seek(0)
    return buffer

if st.button("📄 Export Dark-Themed Research PDF"):
    pdf = export_pdf(df_all, companies)
    st.download_button(
        "Download PDF",
        pdf,
        file_name="Equity_Research_Report.pdf",
        mime="application/pdf"
    )

# ==================================================
# FOOTER
# ==================================================
st.caption("⚠️ Educational, analyst-style research terminal. Not investment advice.")
