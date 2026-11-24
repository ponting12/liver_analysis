import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# ── Page config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Liver Disease Analysis",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Seaborn theme ─────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid")

# ── Find the repo root (works locally AND on Streamlit Cloud) ─────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))


# ── Load & preprocess data ────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading dataset…")
def load_data():
    candidates = [
        os.path.join(ROOT, "data", "processed", "liver_cleaned.csv"),
        os.path.join(ROOT, "data", "raw", "liver.csv"),
    ]
    for path in candidates:
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Fill missing A/G ratio
            col = "Albumin_and_Globulin_Ratio"
            if col in df.columns:
                df[col] = df[col].fillna(df[col].median())
            # Create Disease_Label if missing
            if "Dataset" in df.columns and "Disease_Label" not in df.columns:
                df["Disease_Label"] = df["Dataset"].map(
                    {1: "Liver Disease", 2: "No Disease"}
                )
            # Create Has_Disease flag
            if "Dataset" in df.columns and "Has_Disease" not in df.columns:
                df["Has_Disease"] = (df["Dataset"] == 1).astype(int)
            # Create Age_Group
            if "Age" in df.columns and "Age_Group" not in df.columns:
                df["Age_Group"] = pd.cut(
                    df["Age"],
                    bins=[0, 20, 40, 60, 120],
                    labels=["0-20", "21-40", "41-60", "60+"],
                    right=True,
                )
            return df
    return None


df = load_data()

# ── App header ────────────────────────────────────────────────────────────────
st.title("🩺 Liver Disease Clinical Analytics")
st.markdown(
    "**Indian Liver Patient Dataset (ILPD)** · 583 patients · "
    "EDA, Biomarker Profiling & Demographic Patterns"
)

if df is None:
    st.error(
        "Dataset not found. "
        "Ensure `data/processed/liver_cleaned.csv` exists in the repository."
    )
    st.stop()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Filter Patients")

    gender_opts = ["All"] + sorted(df["Gender"].dropna().unique().tolist())
    sel_gender = st.selectbox("Gender", gender_opts)

    disease_opts = ["All"] + sorted(df["Disease_Label"].dropna().unique().tolist())
    sel_disease = st.selectbox("Diagnosis", disease_opts)

    age_opts = ["All", "0-20", "21-40", "41-60", "60+"]
    sel_age = st.selectbox("Age Group", age_opts)

    st.markdown("---")
    st.info(f"Total in dataset: **{len(df):,}** patients")

# Apply filters
fdf = df.copy()
if sel_gender != "All":
    fdf = fdf[fdf["Gender"] == sel_gender]
if sel_disease != "All":
    fdf = fdf[fdf["Disease_Label"] == sel_disease]
if sel_age != "All":
    fdf = fdf[fdf["Age_Group"].astype(str) == sel_age]

# ── KPI metrics ───────────────────────────────────────────────────────────────
n = len(fdf)
n_dis = int((fdf["Disease_Label"] == "Liver Disease").sum()) if n else 0
pct = round(n_dis / n * 100, 1) if n else 0
avg_age = round(float(fdf["Age"].mean()), 1) if n else 0
avg_bili = round(float(fdf["Total_Bilirubin"].mean()), 2) if n else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Total Patients", f"{n:,}")
col2.metric("🔴 Disease Prevalence", f"{pct}%", f"{n_dis} cases")
col3.metric("📅 Average Age", f"{avg_age} yrs")
col4.metric("🧪 Avg Bilirubin", f"{avg_bili} mg/dL")

st.markdown("---")


# ── Chart generators ──────────────────────────────────────────────────────────
def chart_pie(data):
    counts = data["Disease_Label"].value_counts()
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=["#e74c3c", "#2ecc71"],
        startangle=140,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    ax.set_title("Disease Distribution", fontsize=12, fontweight="bold", pad=10)
    fig.tight_layout()
    return fig


def chart_gender(data):
    fig, ax = plt.subplots(figsize=(6, 4))
    palette = {"Liver Disease": "#e74c3c", "No Disease": "#2ecc71"}
    sns.countplot(
        data=data, x="Gender", hue="Disease_Label",
        palette=palette, ax=ax, order=["Male", "Female"],
    )
    ax.set_title("Diagnosis by Gender", fontsize=12, fontweight="bold")
    ax.set_xlabel("Gender")
    ax.set_ylabel("Count")
    ax.legend(title="Condition", fontsize=9)
    for p in ax.patches:
        h = int(p.get_height())
        if h > 0:
            ax.annotate(
                str(h),
                (p.get_x() + p.get_width() / 2, h + 1),
                ha="center", fontsize=9, fontweight="bold",
            )
    fig.tight_layout()
    return fig


def chart_age_group(data):
    grp = (
        data.groupby("Age_Group", observed=False)
        .agg(Total=("Has_Disease", "count"), Disease=("Has_Disease", "sum"))
    )
    grp["Rate"] = (grp["Disease"] / grp["Total"] * 100).fillna(0).round(1)
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(
        grp.index.astype(str), grp["Rate"],
        color=["#3498db", "#e67e22", "#e74c3c", "#9b59b6"],
        edgecolor="white",
    )
    for bar, rate in zip(bars, grp["Rate"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{rate:.1f}%", ha="center", va="bottom",
            fontsize=9, fontweight="bold",
        )
    ax.set_ylim(0, 105)
    ax.set_title("Disease Prevalence by Age Group", fontsize=12, fontweight="bold")
    ax.set_xlabel("Age Group (Years)")
    ax.set_ylabel("Disease Rate (%)")
    fig.tight_layout()
    return fig


def chart_hist(data):
    fig, ax = plt.subplots(figsize=(6, 4))
    for label, color in [("Liver Disease", "#e74c3c"), ("No Disease", "#3498db")]:
        subset = data[data["Disease_Label"] == label]["Age"]
        ax.hist(subset, bins=20, alpha=0.6, color=color, label=label, edgecolor="white")
    ax.set_title("Patient Age Distribution", fontsize=12, fontweight="bold")
    ax.set_xlabel("Age (Years)")
    ax.set_ylabel("Count")
    ax.legend(fontsize=9)
    fig.tight_layout()
    return fig


def chart_boxplot(data):
    fig, ax = plt.subplots(figsize=(6, 4))
    palette = {"Liver Disease": "#e74c3c", "No Disease": "#2ecc71"}
    order = ["Liver Disease", "No Disease"]
    sns.boxplot(
        data=data[data["Disease_Label"].notna()],
        x="Disease_Label", y="Total_Bilirubin",
        palette=palette, order=order,
        showmeans=True, ax=ax,
    )
    ax.set_yscale("log")
    ax.set_title("Total Bilirubin by Diagnosis", fontsize=12, fontweight="bold")
    ax.set_xlabel("Diagnosis")
    ax.set_ylabel("Total Bilirubin mg/dL (log scale)")
    fig.tight_layout()
    return fig


def chart_heatmap(data):
    cols = [
        "Age", "Total_Bilirubin", "Direct_Bilirubin",
        "Alkaline_Phosphotase", "Alamine_Aminotransferase",
        "Aspartate_Aminotransferase", "Total_Protiens",
        "Albumin", "Albumin_and_Globulin_Ratio", "Has_Disease",
    ]
    available = [c for c in cols if c in data.columns]
    corr = data[available].corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="coolwarm",
        vmin=-1, vmax=1, linewidths=0.4, ax=ax,
        cbar_kws={"shrink": 0.75},
        annot_kws={"size": 7},
    )
    ax.set_title("Biomarker Correlation Matrix", fontsize=12, fontweight="bold")
    plt.xticks(rotation=45, ha="right", fontsize=7)
    plt.yticks(fontsize=7)
    fig.tight_layout()
    return fig


# ── Tabs ──────────────────────────────────────────────────────────────────────
st.subheader("📊 Diagnostic Visualizations")

tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Diagnostic Charts", "🔬 Biomarkers", "📋 Data Table", "💡 Insights"]
)

with tab1:
    r1, r2 = st.columns(2)
    with r1:
        st.markdown("**1. Disease Distribution**")
        st.pyplot(chart_pie(fdf), use_container_width=True)
    with r2:
        st.markdown("**2. Diagnosis by Gender**")
        st.pyplot(chart_gender(fdf), use_container_width=True)

    r3, r4 = st.columns(2)
    with r3:
        st.markdown("**3. Disease Prevalence by Age Group**")
        st.pyplot(chart_age_group(fdf), use_container_width=True)
    with r4:
        st.markdown("**4. Patient Age Distribution**")
        st.pyplot(chart_hist(fdf), use_container_width=True)

with tab2:
    b1, b2 = st.columns(2)
    with b1:
        st.markdown("**5. Total Bilirubin by Diagnosis (Log Scale)**")
        st.pyplot(chart_boxplot(fdf), use_container_width=True)
    with b2:
        st.markdown("**6. Biomarker Correlation Heatmap**")
        st.pyplot(chart_heatmap(fdf), use_container_width=True)

with tab3:
    st.markdown(f"**Showing {n:,} of {len(df):,} records**")
    st.dataframe(fdf.reset_index(drop=True), use_container_width=True, height=420)
    st.download_button(
        "📥 Download Filtered Data as CSV",
        data=fdf.to_csv(index=False).encode("utf-8"),
        file_name="liver_filtered.csv",
        mime="text/csv",
    )

with tab4:
    st.subheader("🔬 Calculated Insights from Real Data (583 records)")

    # Compute from full unfiltered df
    _total = len(df)
    _dis = int((df["Disease_Label"] == "Liver Disease").sum())
    _no = _total - _dis
    _pct = round(_dis / _total * 100, 2)

    _male = df[df["Gender"] == "Male"]
    _female = df[df["Gender"] == "Female"]
    _mpct = round(_male["Has_Disease"].sum() / len(_male) * 100, 2) if len(_male) else 0
    _fpct = round(_female["Has_Disease"].sum() / len(_female) * 100, 2) if len(_female) else 0

    _grp = df.groupby("Age_Group", observed=False).agg(
        T=("Has_Disease", "count"), D=("Has_Disease", "sum")
    )
    _grp["R"] = (_grp["D"] / _grp["T"] * 100).round(2)
    _peak_age = str(_grp["R"].idxmax())
    _peak_rate = float(_grp["R"].max())

    _mbili = round(df[df["Has_Disease"] == 1]["Total_Bilirubin"].mean(), 2)
    _hbili = round(df[df["Has_Disease"] == 0]["Total_Bilirubin"].mean(), 2)
    _r_bili = round(df["Total_Bilirubin"].corr(df["Direct_Bilirubin"]), 2)
    _r_enz = round(
        df["Alamine_Aminotransferase"].corr(df["Aspartate_Aminotransferase"]), 2
    )

    st.markdown(f"""
| # | Finding | Value |
|---|---------|-------|
| 1 | **Disease Prevalence** | {_dis} of {_total} patients have liver disease (**{_pct}%**) |
| 2 | **Gender Disparity** | Males: **{_mpct}%** disease rate · Females: **{_fpct}%** disease rate |
| 3 | **Peak Risk Age Group** | **{_peak_age} years** — {_peak_rate:.1f}% disease prevalence |
| 4 | **Bilirubin Elevation** | Disease avg: **{_mbili} mg/dL** · Healthy avg: **{_hbili} mg/dL** |
| 5 | **Biomarker Collinearity** | Bilirubin pair r = **{_r_bili}** · Transaminase pair r = **{_r_enz}** |
""")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "🩺 Liver Disease Analytics · ILPD Dataset (Kaggle) · "
    "Built with Streamlit · Pandas · Matplotlib · Seaborn"
)
