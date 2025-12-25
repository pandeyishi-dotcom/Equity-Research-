import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO, BytesIO
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

# --------------------------------------------------
# APP CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Analyst Brain X", layout="wide")
st.title("🧠 Analyst Brain X")
st.caption("Equity Research System — PDF Report Export Enabled")

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
HDFC Bank,2020,122000,54000,31000,48000,120000
HDFC Bank,2021,138000,60000,35000,52000,130000
HDFC Bank,2022,156000,69000,41000,61000,150000
HDFC Bank,2023,176000,77000,44000,68000,165000
HDFC Bank,2024,196000,85000,50000,72000,180000
"""

data = pd.read_csv(StringIO(csv_data))

sector_map = {
    "Reliance Industries": "Conglomerate",
    "HDFC Bank": "Banking"
}

company = st.selectbox("Select Company", data["Company"].unique())
sector = sector_map.get(company, "General")

df = data[data["Company"] == company].sort_values("Year")

# --------------------------------------------------
# METRICS
# --------------------------------------------------
df["Revenue Growth %"] = df["Revenue"].pct_change() * 100
df["EBIT Margin %"] = (df["EBIT"] / df["Revenue"]) * 100
df["ROCE %"] = df["EBIT"] / (df["Debt"] + 0.3 * df["Revenue"]) * 100
df["EPS Index"] = df["PAT"] / 1000

# --------------------------------------------------
# CHART GENERATION FUNCTIONS
# --------------------------------------------------
def plot_to_image(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf

def chart_revenue_profit(df):
    fig, ax = plt.subplots()
    ax.plot(df["Year"], df["Revenue"], label="Revenue")
    ax.plot(df["Year"], df["EBIT"], label="EBIT")
    ax.plot(df["Year"], df["PAT"], label="PAT")
    ax.legend()
    ax.set_title("Revenue, EBIT & PAT Trend")
    return plot_to_image(fig)

def chart_margin_roce(df):
    fig, ax = plt.subplots()
    ax.plot(df["Year"], df["EBIT Margin %"], label="EBIT Margin %")
    ax.plot(df["Year"], df["ROCE %"], label="ROCE %")
    ax.legend()
    ax.set_title("Margin & ROCE Trend")
    return plot_to_image(fig)

def chart_debt_ocf(df):
    fig, ax1 = plt.subplots()
    ax1.bar(df["Year"], df["Debt"], alpha=0.6, label="Debt")
    ax2 = ax1.twinx()
    ax2.plot(df["Year"], df["OCF"], marker="o", label="OCF")
    ax1.set_title("Debt vs Operating Cash Flow")
    return plot_to_image(fig)

def chart_valuation(df, pe):
    scenarios = ["Bear", "Base", "Bull"]
    values = [
        df["EPS Index"].iloc[-1] * (pe - 3),
        df["EPS Index"].iloc[-1] * pe,
        df["EPS Index"].iloc[-1] * (pe + 3),
    ]
    fig, ax = plt.subplots()
    ax.bar(scenarios, values)
    ax.set_title("Scenario Valuation")
    return plot_to_image(fig)

# --------------------------------------------------
# PDF GENERATOR
# --------------------------------------------------
def generate_pdf(company, sector, df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Cover
    story.append(Paragraph(f"<b>Equity Research Report</b>", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Company:</b> {company}", styles["Normal"]))
    story.append(Paragraph(f"<b>Sector:</b> {sector}", styles["Normal"]))
    story.append(PageBreak())

    # Executive Summary
    story.append(Paragraph("Executive Summary", styles["Heading2"]))
    summary = (
        f"{company} operates in the {sector} sector. "
        f"Recent revenue growth stands at {round(df['Revenue Growth %'].iloc[-1],2)}%, "
        f"with EBIT margin of {round(df['EBIT Margin %'].iloc[-1],2)}%. "
        f"Capital efficiency (ROCE) is {round(df['ROCE %'].iloc[-1],2)}%."
    )
    story.append(Paragraph(summary, styles["Normal"]))
    story.append(PageBreak())

    # Financial Table
    story.append(Paragraph("Financial Performance", styles["Heading2"]))
    table_data = [df.columns.tolist()] + df.round(2).values.tolist()
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey)
    ]))
    story.append(table)
    story.append(PageBreak())

    # Charts
    story.append(Paragraph("Charts & Analysis", styles["Heading2"]))
    story.append(Image(chart_revenue_profit(df), width=400, height=250))
    story.append(Spacer(1, 12))
    story.append(Image(chart_margin_roce(df), width=400, height=250))
    story.append(Spacer(1, 12))
    story.append(Image(chart_debt_ocf(df), width=400, height=250))

    pe = 15 if sector == "Banking" else 18
    story.append(PageBreak())
    story.append(Paragraph("Valuation", styles["Heading2"]))
    story.append(Image(chart_valuation(df, pe), width=400, height=250))

    # Conclusion
    story.append(PageBreak())
    story.append(Paragraph("Conclusion", styles["Heading2"]))
    story.append(Paragraph(
        "The company demonstrates stable fundamentals with identifiable risks "
        "around margins, leverage, and macro sensitivity. Continuous monitoring "
        "of earnings quality and balance sheet discipline is recommended.",
        styles["Normal"]
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer

# --------------------------------------------------
# UI
# --------------------------------------------------
st.subheader("📊 Data Preview")
st.dataframe(df.round(2), use_container_width=True)

st.subheader("📄 Export Full Equity Research Report")

if st.button("Generate Research Report PDF"):
    pdf_buffer = generate_pdf(company, sector, df)
    st.download_button(
        "Download Equity Research Report",
        data=pdf_buffer,
        file_name=f"{company}_Equity_Research_Report.pdf",
        mime="application/pdf"
    )

st.caption("⚠️ Educational equity research system. Not investment advice.")
