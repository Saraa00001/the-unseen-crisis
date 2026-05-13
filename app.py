"""
Part 2 Prototype - Silent Crisis: The Unequal Global Mental Health Crisis
=======================================================================
A simplified Streamlit prototype for the 5-minute Persuasion Pitch.

Run with:
    streamlit run prototype_app.py

Put your CSV in one of these locations:
    1) same folder as this file: final mental health and gdp dataset.csv
    2) data/final mental health and gdp dataset.csv
    3) data/merged_dataset.csv
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="Silent Crisis Prototype",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Simple design system
# -----------------------------
THEME = {
    "bg": "#0B1220",
    "panel": "#131B2E",
    "text": "#ECEFF7",
    "muted": "#92A0BA",
    "teal": "#5CA9B8",
    "coral": "#D26D6F",
    "amber": "#D9A85C",
    "lavender": "#9A8BC2",
}

CRISIS_SCALE = [
    [0.0, "#1A2540"],
    [0.35, "#4A527C"],
    [0.7, "#B07578"],
    [1.0, "#D26D6F"],
]

INCOME_PALETTE = {
    "Low": "#D26D6F",
    "Low income": "#D26D6F",
    "Lower-middle income": "#D9A85C",
    "Upper-middle income": "#9A8BC2",
    "High income": "#5CA9B8",
    "High": "#5CA9B8",
}

st.markdown(
    f"""
    <style>
    .stApp {{ background: {THEME['bg']}; color: {THEME['text']}; }}
    h1, h2, h3 {{ color: {THEME['text']}; }}
    .hero {{
        padding: 2rem;
        border-radius: 20px;
        background: linear-gradient(135deg, rgba(210,109,111,0.13), rgba(92,169,184,0.08)), {THEME['panel']};
        border: 1px solid #243049;
        margin-bottom: 1.2rem;
    }}
    .eyebrow {{ color: {THEME['teal']}; font-size: 0.78rem; letter-spacing: 0.18em; text-transform: uppercase; font-weight: 700; }}
    .subtitle {{ color: {THEME['muted']}; font-size: 1.08rem; line-height: 1.55; max-width: 900px; }}
    .kpi {{
        background: {THEME['panel']};
        border: 1px solid #243049;
        border-radius: 16px;
        padding: 1rem 1.15rem;
        min-height: 105px;
    }}
    .kpi-label {{ color: {THEME['muted']}; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.12em; font-weight: 700; }}
    .kpi-value {{ font-size: 1.8rem; font-weight: 800; color: {THEME['text']}; margin-top: 0.4rem; }}
    .kpi-note {{ color: {THEME['muted']}; font-size: 0.78rem; margin-top: 0.2rem; }}
    .chapter {{
        margin-top: 2rem;
        padding-top: 0.8rem;
        border-top: 1px solid #243049;
    }}
    .chapter-tag {{ color: {THEME['teal']}; font-size: 0.75rem; letter-spacing: 0.16em; text-transform: uppercase; font-weight: 700; }}
    .callout {{
        background: rgba(210,109,111,0.10);
        border-left: 4px solid {THEME['coral']};
        padding: 1rem 1.2rem;
        border-radius: 10px;
        color: {THEME['text']};
        margin: 1rem 0;
        font-size: 1rem;
        line-height: 1.5;
    }}
    .small-note {{ color: {THEME['muted']}; font-size: 0.85rem; line-height: 1.45; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Data loading
# -----------------------------
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    possible_paths = [
    "final mental health and gdp dataset.csv",
    "data/final mental health and gdp dataset.csv",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            break
    else:
        st.error("Dataset not found. Place the CSV next to this app or inside a data/ folder.")
        st.stop()

    # Clean text columns
    for col in ["country", "iso3", "region", "income_group"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Make sure key numeric columns are numeric
    numeric_cols = [
        "gdp_per_capita_usd", "population_millions", "total_affected_millions",
        "mh_crisis_index", "treatment_gap_pct", "psychiatrists_per100k",
        "mh_spend_usd_per_capita", "mh_system_score", "depression_pct",
        "anxiety_pct", "suicide_rate_per100k"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


df = load_data()

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.title("🌍 Silent Crisis")
st.sidebar.caption("Part 2 persuasion pitch prototype")

regions = sorted(df["region"].dropna().unique())
incomes = sorted(df["income_group"].dropna().unique())

selected_regions = st.sidebar.multiselect("Filter by region", regions, default=regions)
selected_incomes = st.sidebar.multiselect("Filter by income group", incomes, default=incomes)

# Safe fallback: if presenter accidentally clears filters, show full data.
if not selected_regions:
    selected_regions = regions
if not selected_incomes:
    selected_incomes = incomes

view = df[df["region"].isin(selected_regions) & df["income_group"].isin(selected_incomes)].copy()
if view.empty:
    view = df.copy()
    st.sidebar.warning("No records matched. Showing global view.")

countries = sorted(view["country"].dropna().unique())
default_country = view.sort_values("mh_crisis_index", ascending=False)["country"].iloc[0]
selected_country = st.sidebar.selectbox(
    "Country spotlight",
    countries,
    index=countries.index(default_country) if default_country in countries else 0,
)

investment_increase = st.sidebar.slider(
    "What-if: increase mental health spending",
    min_value=0,
    max_value=100,
    value=25,
    step=5,
    format="+%d%%",
)

# -----------------------------
# Helper functions
# -----------------------------
def fmt(value, digits=1, suffix=""):
    if pd.isna(value):
        return "-"
    return f"{value:,.{digits}f}{suffix}"


def kpi(label, value, note=""):
    return f"""
    <div class='kpi'>
        <div class='kpi-label'>{label}</div>
        <div class='kpi-value'>{value}</div>
        <div class='kpi-note'>{note}</div>
    </div>
    """


def style_fig(fig, height=460):
    fig.update_layout(
        height=height,
        paper_bgcolor=THEME["panel"],
        plot_bgcolor="#0F1727",
        font=dict(color=THEME["text"], family="Inter, Arial"),
        margin=dict(l=20, r=20, t=55, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=THEME["muted"])),
        hoverlabel=dict(bgcolor="#1A2440", font=dict(color=THEME["text"])),
    )
    fig.update_xaxes(gridcolor="#243049", color=THEME["muted"])
    fig.update_yaxes(gridcolor="#243049", color=THEME["muted"])
    return fig

# -----------------------------
# Hero
# -----------------------------
st.markdown(
    """
    <div class='hero'>
        <div class='eyebrow'>WHO Global Mental Health Response Council · Prototype Briefing</div>
        <h1>Mental Health Shouldn’t Depend on Where You’re Born</h1>
        <p class='subtitle'>
            Mental health challenges are global, but access to care is deeply unequal.
            This prototype shows how burden, income, treatment gaps and workforce capacity
            combine to reveal which countries are most at risk — and where intervention can change outcomes.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# KPI row
# -----------------------------
total_countries = view["country"].nunique()
total_affected = view["total_affected_millions"].sum()
avg_gap = view["treatment_gap_pct"].mean()
avg_system = view["mh_system_score"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.markdown(kpi("Countries in view", f"{total_countries}", "filtered scope"), unsafe_allow_html=True)
c2.markdown(kpi("People affected", fmt(total_affected, 0, "M"), "approximate total"), unsafe_allow_html=True)
c3.markdown(kpi("Average treatment gap", fmt(avg_gap, 1, "%"), "untreated despite need"), unsafe_allow_html=True)
c4.markdown(kpi("Average system score", fmt(avg_system, 1), "system readiness"), unsafe_allow_html=True)

# -----------------------------
# Visual 1: Global map
# -----------------------------
st.markdown("<div class='chapter'><div class='chapter-tag'>01 · A silent global crisis</div><h2>The crisis is global, but the burden is uneven</h2></div>", unsafe_allow_html=True)
st.markdown("<p class='small-note'>Use this map as your opening visual in Part 2. It quickly shows that mental health pressure is not isolated to one region.</p>", unsafe_allow_html=True)

fig_map = px.choropleth(
    view,
    locations="iso3",
    color="mh_crisis_index",
    hover_name="country",
    color_continuous_scale=CRISIS_SCALE,
    custom_data=["region", "income_group", "population_millions", "total_affected_millions", "gdp_per_capita_usd", "treatment_gap_pct"],
    title="Global Mental Health Crisis Index",
)
fig_map.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "%{customdata[0]} · %{customdata[1]}<br><br>"
        "Crisis index: <b>%{z:.1f}</b><br>"
        "Population: <b>%{customdata[2]:,.1f}M</b><br>"
        "Affected: <b>%{customdata[3]:,.1f}M</b><br>"
        "GDP/capita: <b>$%{customdata[4]:,.0f}</b><br>"
        "Treatment gap: <b>%{customdata[5]:.1f}%</b>"
        "<extra></extra>"
    )
)
fig_map.update_geos(showframe=False, showcoastlines=False, projection_type="natural earth")
fig_map = style_fig(fig_map, height=520)
st.plotly_chart(fig_map, use_container_width=True)

# -----------------------------
# Visual 2: GDP vs treatment gap
# -----------------------------
st.markdown("<div class='chapter'><div class='chapter-tag'>02 · Not all countries suffer equally</div><h2>Lower economic capacity often means a larger treatment gap</h2></div>", unsafe_allow_html=True)

fig_gap = px.scatter(
    view.dropna(subset=["gdp_per_capita_usd", "treatment_gap_pct", "total_affected_millions"]),
    x="gdp_per_capita_usd",
    y="treatment_gap_pct",
    size="total_affected_millions",
    color="income_group",
    color_discrete_map=INCOME_PALETTE,
    hover_name="country",
    log_x=True,
    size_max=48,
    custom_data=["region", "psychiatrists_per100k", "mh_spend_usd_per_capita"],
    title="GDP per capita vs Treatment Gap · Bubble size = people affected",
)
fig_gap.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "%{customdata[0]}<br><br>"
        "GDP/capita: <b>$%{x:,.0f}</b><br>"
        "Treatment gap: <b>%{y:.1f}%</b><br>"
        "Psychiatrists: <b>%{customdata[1]:.1f} per 100k</b><br>"
        "MH spend: <b>$%{customdata[2]:,.2f} per capita</b>"
        "<extra></extra>"
    )
)
fig_gap.update_layout(xaxis_title="GDP per capita (USD, log scale)", yaxis_title="Treatment gap (%)")
fig_gap = style_fig(fig_gap, height=520)
st.plotly_chart(fig_gap, use_container_width=True)

st.markdown(
    """
    <div class='callout'>
        <b>Persuasion point:</b> The crisis is not only about how many people are affected.
        The real injustice is that many high-need countries also have the weakest ability to deliver care.
    </div>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# Visual 3: Country spotlight
# -----------------------------
st.markdown("<div class='chapter'><div class='chapter-tag'>03 · Access to care is the real divide</div><h2>Country spotlight: show one nation’s care gap clearly</h2></div>", unsafe_allow_html=True)

country_row = view[view["country"] == selected_country].iloc[0]

s1, s2, s3, s4 = st.columns(4)
s1.markdown(kpi("Selected country", selected_country, country_row["region"]), unsafe_allow_html=True)
s2.markdown(kpi("Treatment gap", fmt(country_row["treatment_gap_pct"], 1, "%"), "untreated need"), unsafe_allow_html=True)
s3.markdown(kpi("Psychiatrists", fmt(country_row["psychiatrists_per100k"], 1), "per 100k people"), unsafe_allow_html=True)
s4.markdown(kpi("MH spend", "$" + fmt(country_row["mh_spend_usd_per_capita"], 2), "per person"), unsafe_allow_html=True)

country_compare = pd.DataFrame({
    "Metric": ["Depression %", "Anxiety %", "Suicide rate /100k", "Treatment gap %", "Crisis index"],
    selected_country: [
        country_row["depression_pct"],
        country_row["anxiety_pct"],
        country_row["suicide_rate_per100k"],
        country_row["treatment_gap_pct"],
        country_row["mh_crisis_index"],
    ],
    "Global average": [
        df["depression_pct"].mean(),
        df["anxiety_pct"].mean(),
        df["suicide_rate_per100k"].mean(),
        df["treatment_gap_pct"].mean(),
        df["mh_crisis_index"].mean(),
    ],
})
long_compare = country_compare.melt("Metric", var_name="Series", value_name="Value")

fig_country = px.bar(
    long_compare,
    x="Value",
    y="Metric",
    color="Series",
    orientation="h",
    barmode="group",
    title=f"{selected_country} vs Global Average",
    color_discrete_map={selected_country: THEME["coral"], "Global average": THEME["teal"]},
)
fig_country.update_layout(xaxis_title="Value", yaxis_title="")
fig_country = style_fig(fig_country, height=430)
st.plotly_chart(fig_country, use_container_width=True)

# -----------------------------
# Visual 4: Intervention simulator
# -----------------------------
st.markdown("<div class='chapter'><div class='chapter-tag'>04 · Intervention can change outcomes</div><h2>What if policy investment increased?</h2></div>", unsafe_allow_html=True)

sim = view.copy()
sim["projected_system_score"] = (sim["mh_system_score"] + investment_increase * 0.25).clip(upper=100)
sim["projected_treatment_gap"] = (sim["treatment_gap_pct"] - investment_increase * 0.30).clip(lower=0)
sim["projected_spend"] = sim["mh_spend_usd_per_capita"] * (1 + investment_increase / 100)

current_gap = sim["treatment_gap_pct"].mean()
projected_gap = sim["projected_treatment_gap"].mean()
current_score = sim["mh_system_score"].mean()
projected_score = sim["projected_system_score"].mean()

p1, p2, p3, p4 = st.columns(4)
p1.markdown(kpi("Investment scenario", f"+{investment_increase}%", "spending uplift"), unsafe_allow_html=True)
p2.markdown(kpi("Treatment gap change", f"-{current_gap - projected_gap:.1f} pts", f"{current_gap:.1f}% → {projected_gap:.1f}%"), unsafe_allow_html=True)
p3.markdown(kpi("System score change", f"+{projected_score - current_score:.1f} pts", f"{current_score:.1f} → {projected_score:.1f}"), unsafe_allow_html=True)
p4.markdown(kpi("Countries modelled", f"{total_countries}", "current filter"), unsafe_allow_html=True)

fig_sim = px.scatter(
    sim,
    x="projected_spend",
    y="projected_system_score",
    size="population_millions",
    color="income_group",
    color_discrete_map=INCOME_PALETTE,
    hover_name="country",
    size_max=46,
    custom_data=["mh_spend_usd_per_capita", "mh_system_score", "treatment_gap_pct", "projected_treatment_gap"],
    title=f"Projected system readiness after +{investment_increase}% investment",
)
fig_sim.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br><br>"
        "Spend: <b>$%{customdata[0]:,.2f}</b> → <b>$%{x:,.2f}</b><br>"
        "System score: <b>%{customdata[1]:.1f}</b> → <b>%{y:.1f}</b><br>"
        "Treatment gap: <b>%{customdata[2]:.1f}%</b> → <b>%{customdata[3]:.1f}%</b>"
        "<extra></extra>"
    )
)
fig_sim.update_layout(xaxis_title="Projected mental health spend per capita", yaxis_title="Projected system readiness score")
fig_sim = style_fig(fig_sim, height=500)
st.plotly_chart(fig_sim, use_container_width=True)

st.markdown(
    """
    <div class='callout'>
        <b>Call to action:</b> mental health inequality is not only a health problem — it is a resource allocation problem.
        The dashboard helps policymakers identify where investment could have the greatest impact.
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Prototype note: the what-if model is intentionally simple for pitch demonstration. "
    "It uses linear assumptions to show direction, not clinical prediction."
)