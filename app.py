"""
U.S. 3000 plus Hospital Quality and Readmission Analysis: Exploring Organizational and Patient Experience Factors
----------------------------------------------------
Interactive Streamlit companion to the "Hospital Quality and Readmission
Analysis" notebook. Built on CMS Care Compare data (Hospital General
Information, HCAHPS patient survey, and the Hospital Readmissions
Reduction Program).

Run locally:    streamlit run app.py
Deploy:         push this folder to a public GitHub repo, then deploy on
                Streamlit Community Cloud pointing at app.py
"""

import json
import math
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------
# Page config + CVD-safe design system (mirrors the notebook's palette)
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="U.S. Hospital Quality Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

GREY = "#B7B7B7"        # context / muted ink
HIGHLIGHT = "#2C6E9E"    # single focus colour (blue, CVD-safe)
HIGHLIGHT_WARM = "#D9782D"  # secondary focus colour (orange, CVD-safe pair)
GOOD = "#2E7D6B"
BAD = "#C25B4A"
DIVERGING = "RdBu_r"
SEQUENTIAL = "Blues"

PLOTLY_TEMPLATE = "plotly_white"

st.markdown(
    """
    <style>
    .metric-card {
        background-color: #FAFAFA;
        border: 1px solid #ECECEC;
        border-radius: 10px;
        padding: 14px 16px;
    }
    div[data-testid="stMetricValue"] { font-size: 1.6rem; }
    .block-container { padding-top: 1.6rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------
@st.cache_data
def load_data():
    data_path = Path(__file__).parent / "data.json"
    with open(data_path) as f:
        raw = json.load(f)

    hosp = pd.DataFrame(raw["hospital_rating_readmission"])
    hosp = hosp.replace({float("nan"): None})

    state = pd.DataFrame(raw["state_summary"])
    top10 = pd.DataFrame(raw["top10_composite"])
    reg = pd.DataFrame(raw["regression_coefficients"])
    cond = pd.DataFrame(raw["condition_summary"])
    ownership = raw["ownership_readmission"]
    emergency = raw["emergency_patient_experience"]
    corr_exp_readm = raw["corr_experience_readmission"]
    corr_exp_clin = raw["corr_experience_clinical"]

    return hosp, state, top10, reg, cond, ownership, emergency, corr_exp_readm, corr_exp_clin


hosp, state_df, top10, reg, cond, ownership, emergency, corr_exp_readm, corr_exp_clin = load_data()

OWNERSHIP_ORDER = [
    "Voluntary non-profit - Church",
    "Voluntary non-profit - Other",
    "Voluntary non-profit - Private",
    "Government - Local",
    "Government - State",
    "Government - Hospital District or Authority",
    "Proprietary",
]

# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.title("🏥 Hospital Quality and Readmission Analysis")
st.caption(
    "Exploring organizational and patient-experience factors associated with hospital "
    "performance — CMS Care Compare data (Hospital General Information · HCAHPS · "
    "Hospital Readmissions Reduction Program, FY 2026)."
)

# ----------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------
st.sidebar.header("Explore the data")

all_states = sorted(hosp["State"].dropna().unique().tolist())
selected_states = st.sidebar.multiselect(
    "State(s)", options=all_states, default=[],
    help="Leave empty to include all states.",
)

rating_min, rating_max = st.sidebar.slider(
    "CMS overall hospital rating", min_value=1, max_value=5, value=(1, 5), step=1
)

selected_ownership = st.sidebar.multiselect(
    "Hospital ownership (for the ownership chart)",
    options=OWNERSHIP_ORDER, default=OWNERSHIP_ORDER,
)

er_options = st.sidebar.radio(
    "Emergency services (for the patient-experience chart)",
    options=["Both", "Yes", "No"], index=0,
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data reconstructed from the analysis notebook's own published figures — every "
    "number here matches the notebook's research-question findings 1:1."
)

# Apply filters to the hospital-level scatter dataset
filtered = hosp.copy()
if selected_states:
    filtered = filtered[filtered["State"].isin(selected_states)]
filtered = filtered[
    filtered["Rating"].isna() | filtered["Rating"].between(rating_min, rating_max)
]
if rating_min > 1 or rating_max < 5:
    filtered = filtered[filtered["Rating"].between(rating_min, rating_max)]

# ----------------------------------------------------------------------
# KPI row
# ----------------------------------------------------------------------
valid_ratings = hosp["Rating"].dropna()
valid_err = hosp["ExcessReadmissionRatio"].dropna()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Hospitals analyzed", f"{hosp[['Facility Name','State']].drop_duplicates().shape[0]:,}")
k2.metric("States covered", f"{hosp['State'].nunique()}")
k3.metric("Avg. CMS rating", f"{valid_ratings.mean():.2f} / 5")
k4.metric("Avg. excess readmission ratio", f"{valid_err.mean():.3f}", help="1.00 = performing at the national expected rate")
best_state = state_df.sort_values("AvgPatientExperience", ascending=False).iloc[0]
k5.metric("Top state (patient experience)", best_state["State"], f"{best_state['AvgPatientExperience']:.1f} index")

st.markdown("---")

# ----------------------------------------------------------------------
# 1. Rating vs Excess Readmission Ratio
# ----------------------------------------------------------------------
st.subheader("1 · Do higher-rated hospitals have lower excess readmissions?")
st.caption(
    f"Showing {len(filtered):,} of {len(hosp):,} hospitals based on your state and rating filters. "
    "Each point is one hospital. Trend line shows the overall relationship (r ≈ -0.27)."
)

scatter_data = filtered.dropna(subset=["Rating", "ExcessReadmissionRatio"])
fig1 = go.Figure()
fig1.add_trace(
    go.Scattergl(
        x=scatter_data["Rating"], y=scatter_data["ExcessReadmissionRatio"],
        mode="markers",
        marker=dict(color=HIGHLIGHT, opacity=0.45, size=7,
                    line=dict(width=0)),
        text=scatter_data["Facility Name"] + " (" + scatter_data["State"] + ")",
        hovertemplate="%{text}<br>Rating: %{x}<br>Excess Readmission Ratio: %{y:.3f}<extra></extra>",
        name="Hospitals",
    )
)
if len(scatter_data) > 1:
    z = pd.Series(scatter_data["ExcessReadmissionRatio"].values).astype(float)
    x = pd.Series(scatter_data["Rating"].values).astype(float)
    if x.std() > 0:
        slope = ((x - x.mean()) * (z - z.mean())).sum() / ((x - x.mean()) ** 2).sum()
        intercept = z.mean() - slope * x.mean()
        xs = [x.min(), x.max()]
        ys = [slope * v + intercept for v in xs]
        fig1.add_trace(
            go.Scatter(x=xs, y=ys, mode="lines", line=dict(color=HIGHLIGHT_WARM, width=3),
                        name="Trend")
        )
fig1.update_layout(
    template=PLOTLY_TEMPLATE, height=460, showlegend=False,
    xaxis_title="CMS Overall Hospital Rating", yaxis_title="Excess Readmission Ratio",
    margin=dict(t=10, b=10),
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ----------------------------------------------------------------------
# 2. State performance map
# ----------------------------------------------------------------------
st.subheader("2 · Which states balance strong patient experience with low readmissions?")
st.caption(
    "Bubble size = number of hospitals in the state. Selected states (sidebar) are highlighted; "
    "the rest stay muted for context."
)

state_plot = state_df.copy()
state_plot["highlighted"] = state_plot["State"].isin(selected_states) if selected_states else True

fig2 = go.Figure()
base = state_plot[~state_plot["highlighted"]] if selected_states else pd.DataFrame(columns=state_plot.columns)
hi = state_plot[state_plot["highlighted"]] if selected_states else state_plot

if len(base):
    fig2.add_trace(go.Scatter(
        x=base["AvgPatientExperience"], y=base["AvgReadmission"],
        mode="markers+text", text=base["State"], textposition="top center",
        marker=dict(size=base["Hospitals"].clip(lower=6), color=GREY, sizemode="area",
                    sizeref=2. * max(state_plot["Hospitals"]) / (40. ** 2), opacity=0.55),
        name="Other states", hovertemplate="%{text}<extra></extra>",
        textfont=dict(size=9, color=GREY),
    ))
fig2.add_trace(go.Scatter(
    x=hi["AvgPatientExperience"], y=hi["AvgReadmission"],
    mode="markers+text", text=hi["State"], textposition="top center",
    marker=dict(size=hi["Hospitals"].clip(lower=6), color=HIGHLIGHT, sizemode="area",
                sizeref=2. * max(state_plot["Hospitals"]) / (40. ** 2), opacity=0.85,
                line=dict(width=1, color="white")),
    name="Selected", hovertemplate="%{text}<br>Patient Experience: %{x:.1f}<br>Excess Readmission: %{y:.3f}<extra></extra>",
    textfont=dict(size=10, color="#333333"),
))
fig2.update_layout(
    template=PLOTLY_TEMPLATE, height=520, showlegend=False,
    xaxis_title="Average Patient Experience Index", yaxis_title="Average Excess Readmission Ratio",
    margin=dict(t=10, b=10),
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ----------------------------------------------------------------------
# 3 & 4 side-by-side: Ownership + Emergency services
# ----------------------------------------------------------------------
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("3 · Readmission performance by ownership")
    st.caption("One-way ANOVA: F = 15.26, p < 0.001 — ownership is significantly associated with performance.")
    fig3 = go.Figure()
    shown = [o for o in OWNERSHIP_ORDER if o in selected_ownership]
    colors = [HIGHLIGHT if "non-profit" in o else (HIGHLIGHT_WARM if o == "Proprietary" else GREY) for o in shown]
    for name, color in zip(shown, colors):
        fig3.add_trace(go.Box(
            y=ownership[name], name=name.replace("Voluntary non-profit", "Non-profit").replace("Government - ", "Gov. "),
            marker_color=color, boxpoints=False,
        ))
    fig3.update_layout(
        template=PLOTLY_TEMPLATE, height=460, showlegend=False,
        yaxis_title="Excess Readmission Ratio", xaxis_title=None,
        margin=dict(t=10, b=10),
    )
    fig3.update_xaxes(tickangle=25)
    st.plotly_chart(fig3, use_container_width=True)

with col_b:
    st.subheader("4 · Patient experience by ER availability")
    st.caption("Welch's t-test: t = -15.12, p < 0.001 — hospitals without an ER score higher.")
    fig4 = go.Figure()
    groups = ["Yes", "No"] if er_options == "Both" else [er_options]
    colors_map = {"Yes": HIGHLIGHT, "No": HIGHLIGHT_WARM}
    for g in groups:
        fig4.add_trace(go.Violin(
            y=emergency[g], name=f"ER: {g}", box_visible=True, meanline_visible=True,
            line_color=colors_map[g], fillcolor=colors_map[g], opacity=0.5, points=False,
        ))
    fig4.update_layout(
        template=PLOTLY_TEMPLATE, height=460, showlegend=False,
        yaxis_title="Patient Experience Index", xaxis_title=None,
        margin=dict(t=10, b=10),
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# ----------------------------------------------------------------------
# 5. Top hospitals
# ----------------------------------------------------------------------
st.subheader("5 · Top 10 hospitals by composite quality score")
st.caption(
    "Composite score blends standardized CMS rating, patient experience, mortality, safety, "
    "and readmission performance. NYU Langone Hospitals (NY) leads the ranking."
)
top10_sorted = top10.sort_values("CompositeScore")
fig5 = go.Figure(go.Bar(
    x=top10_sorted["CompositeScore"], y=top10_sorted["Facility Name"] + " (" + top10_sorted["State"] + ")",
    orientation="h", marker=dict(color=top10_sorted["CompositeScore"], colorscale=SEQUENTIAL),
    hovertemplate="%{y}<br>Score: %{x:.2f}<extra></extra>",
))
fig5.update_layout(
    template=PLOTLY_TEMPLATE, height=460,
    xaxis_title="Composite Quality Score", yaxis_title=None,
    margin=dict(t=10, b=10),
)
st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ----------------------------------------------------------------------
# 6. Regression drivers
# ----------------------------------------------------------------------
st.subheader("6 · What actually predicts excess readmissions?")
st.caption(
    "OLS regression (R² = 0.335, F = 84.36, p < 0.001). Bars left of zero lower the excess "
    "readmission ratio; bars right of zero raise it. Hospital rating and readmission-measure "
    "performance are the strongest, statistically significant levers — patient experience and "
    "ownership are not, once other factors are controlled for."
)
reg_sorted = reg.sort_values("Coefficient")
bar_colors = [GOOD if v < 0 else BAD for v in reg_sorted["Coefficient"]]
fig6 = go.Figure(go.Bar(
    x=reg_sorted["Coefficient"], y=reg_sorted["Predictor"],
    orientation="h", marker=dict(color=bar_colors),
    hovertemplate="%{y}<br>Coefficient: %{x:.3f}<extra></extra>",
))
fig6.add_vline(x=0, line_width=1, line_color="#666666")
fig6.update_layout(
    template=PLOTLY_TEMPLATE, height=480,
    xaxis_title="Regression Coefficient (effect on Excess Readmission Ratio)", yaxis_title=None,
    margin=dict(t=10, b=10),
)
st.plotly_chart(fig6, use_container_width=True)

st.markdown("---")
st.caption(
    "Source: CMS Care Compare (Hospital General Information, HCAHPS, Hospital Readmissions "
    "Reduction Program FY 2026). Built with Streamlit + Plotly · companion to the full analysis "
    "notebook (10 research questions)."
)
