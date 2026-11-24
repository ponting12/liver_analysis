import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Liver Disease Analysis",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

sns.set_theme(style="whitegrid", palette="muted")

# ── Locate project root (works both locally and on Streamlit Cloud) ───────────
ROOT = os.path.dirname(os.path.abspath(__file__))


# ── Load & clean data ─────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading dataset…")
def load_data():
    for rel in ["data/processed/liver_cleaned.csv", "data/raw/liver.csv"]:
        path = os.path.join(ROOT, rel)
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Fill missing A/G ratio
            if "Albumin_and_Globulin_Ratio" in df.columns:
                df["Albumin_and_Globulin_Ratio"] = df[
                    "Albumin_and_Globulin_Ratio"
                ].fillna(df["Albumin_and_Globulin_Ratio"].median())
            # Disease label
            if "Dataset" in df.columns and "Disease_Label" not in df.columns:
                df["Disease_Label"] = df["Dataset"].map(
                    {1: "Liver Disease", 2: "No Disease"}
                )
            if "Dataset" in df.columns and "Has_Disease" not in df.columns:
                df["Has_Disease"] = (df["Dataset"] == 1).astype(int)
            # Age groups
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

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🩺 Liver Disease Clinical Analytics Dashboard")
st.caption(
    "Exploratory Data Analysis · Biomarker Profiling · Demographic Patterns  "
    "| Indian Liver Patient Dataset (ILPD) — 583 patients"
)

if df is None:
    st.error(
        "⚠️ Dataset not found. "
        "Make sure `data/processed/liver_cleaned.csv` or `data/raw/liver.csv` "
        "is present in the repository."
    )
    st.stop()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.header("🔍 Filter Patients")

gender_opts = ["All"] + sorted(df["Gender"].dropna().unique().tolist())
sel_gender = st.sidebar.selectbox("Gender", gender_opts)

disease_opts = ["All"] + sorted(df["Disease_Label"].dropna().unique().tolist())
sel_disease = st.sidebar.selectbox("Diagnosis", disease_opts)

age_opts = ["All"] + ["0-20", "21-40", "41-60", "60+"]
sel_age = st.sidebar.selectbox("Age Group", age_opts)

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
n_dis = int((fdf["Disease_Label"] == "Liver Disease").sum())
pct = round(n_dis / n * 100, 1) if n else 0
avg_age = round(fdf["Age"].mean(), 1) if n else 0
avg_bili = round(fdf["Total_Bilirubin"].mean(), 2) if n else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Patients", f"{n:,}")
c2.metric("Disease Prevalence", f"{pct}%", f"{n_dis} cases")
c3.metric("Average Age", f"{avg_age} yrs")
c4.metric("Avg Total Bilirubin", f"{avg_bili} mg/dL")

st.markdown("---")


# ── Chart helpers (always use matplotlib/seaborn — no pre-saved PNGs needed) ──
def fig_pie(data):
    counts = data["Disease_Label"].value_counts()
    fig, ax = plt.subplots(figsize=(5, 5))
    colors = ["#e74c3c", "#2ecc71"]
    ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=colors,
        startangle=140,
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    ax.set_title("Disease Distribution", fontsize=13, fontweight="bold")
    plt.tight_layout()
    return fig


def fig_gender_bar(data):
    fig, ax = plt.subplots(figsize=(6, 4))
    palette = {"Liver Disease": "#e74c3c", "No Disease": "#2ecc71"}
    sns.countplot(data=data, x="Gender", hue="Disease_Label", palette=palette, ax=ax)
    ax.set_title("Diagnosis by Gender", fontsize=13, fontweight="bold")
    ax.set_xlabel("Gender")
    ax.set_ylabel("Patient Count")
    ax.legend(title="Condition")
    for p in ax.patches:
        h = p.get_height()
        if h > 0:
            ax.annotate(
                f"{int(h)}",
                (p.get_x() + p.get_width() / 2, h),
                ha="center", va="bottom", fontsize=9, fontweight="bold",
                xytext=(0, 3), textcoords="offset points",
            )
    plt.tight_layout()
    return fig


def fig_age_bar(data):
    age_sum = (
        data.groupby("Age_Group", observed=False)
        .agg(Total=("Has_Disease", "count"), Disease=("Has_Disease", "sum"))
    )
    age_sum["Rate"] = (age_sum["Disease"] / age_sum["Total"] * 100).round(1)
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(
        age_sum.index.astype(str), age_sum["Rate"],
        color=["#3498db", "#e67e22", "#e74c3c", "#9b59b6"],
        edgecolor="white", linewidth=0.8,
    )
    for bar, rate in zip(bars, age_sum["Rate"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.5,
            f"{rate:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold",
        )
    ax.set_ylim(0, 100)
    ax.set_title("Disease Prevalence by Age Group (%)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Age Group (Years)")
    ax.set_ylabel("Disease Prevalence (%)")
    plt.tight_layout()
    return fig


def fig_hist(data):
    fig, ax = plt.subplots(figsize=(6, 4))
    palette = {"Liver Disease": "#e74c3c", "No Disease": "#3498db"}
    sns.histplot(
        data=data, x="Age", hue="Disease_Label", kde=True, bins=25,
        palette=palette, element="step", ax=ax,
    )
    ax.set_title("Age Distribution with Density Curves", fontsize=13, fontweight="bold")
    ax.set_xlabel("Patient Age (Years)")
    ax.set_ylabel("Count")
    plt.tight_layout()
    return fig


def fig_boxplot(data):
    fig, ax = plt.subplots(figsize=(6, 4))
    palette = {"Liver Disease": "#e74c3c", "No Disease": "#2ecc71"}
    sns.boxplot(
        data=data, x="Disease_Label", y="Total_Bilirubin",
        palette=palette, showmeans=True, ax=ax,
    )
    ax.set_yscale("log")
    ax.set_title("Total Bilirubin by Diagnosis (Log Scale)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Diagnosis")
    ax.set_ylabel("Total Bilirubin mg/dL (log)")
    plt.tight_layout()
    return fig


def fig_heatmap(data):
    numeric_cols = [
        "Age", "Total_Bilirubin", "Direct_Bilirubin",
        "Alkaline_Phosphotase", "Alamine_Aminotransferase",
        "Aspartate_Aminotransferase", "Total_Protiens",
        "Albumin", "Albumin_and_Globulin_Ratio", "Has_Disease",
    ]
    available = [c for c in numeric_cols if c in data.columns]
    corr = data[available].corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="coolwarm",
        vmin=-1, vmax=1, linewidths=0.4, ax=ax,
        cbar_kws={"shrink": 0.8},
    )
    ax.set_title("Biomarker Correlation Matrix", fontsize=13, fontweight="bold")
    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(fontsize=8)
    plt.tight_layout()
    return fig


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Diagnostic Charts", "🔬 Biomarkers", "📋 Data Table", "💡 Insights"]
)

with tab1:
    st.subheader("Key Diagnostic Visualizations")
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.markdown("**1. Disease Distribution**")
        st.pyplot(fig_pie(fdf), use_container_width=True)
    with r1c2:
        st.markdown("**2. Diagnosis by Gender**")
        st.pyplot(fig_gender_bar(fdf), use_container_width=True)

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.markdown("**3. Disease Prevalence by Age Group**")
        st.pyplot(fig_age_bar(fdf), use_container_width=True)
    with r2c2:
        st.markdown("**4. Patient Age Distribution**")
        st.pyplot(fig_hist(fdf), use_container_width=True)

with tab2:
    st.subheader("Biomarker Analysis")
    bc1, bc2 = st.columns(2)
    with bc1:
        st.markdown("**5. Total Bilirubin by Diagnosis**")
        st.pyplot(fig_boxplot(fdf), use_container_width=True)
    with bc2:
        st.markdown("**6. Biomarker Correlation Heatmap**")
        st.pyplot(fig_heatmap(fdf), use_container_width=True)

with tab3:
    st.subheader(f"Patient Data Table — {n:,} records shown")
    st.dataframe(fdf.reset_index(drop=True), use_container_width=True, height=420)
    st.download_button(
        "📥 Download Filtered CSV",
        data=fdf.to_csv(index=False).encode("utf-8"),
        file_name="liver_filtered_data.csv",
        mime="text/csv",
    )

with tab4:
    st.subheader("Calculated Clinical Insights (from real ILPD data)")
    
    # Compute from FULL (unfiltered) df
    total_full = len(df)
    dis_full = int((df["Disease_Label"] == "Liver Disease").sum())
    no_dis_full = total_full - dis_full
    dis_pct_full = round(dis_full / total_full * 100, 2)

    male_df = df[df["Gender"] == "Male"]
    female_df = df[df["Gender"] == "Female"]
    male_dis_pct = round((male_df["Has_Disease"].sum() / len(male_df)) * 100, 2)
    female_dis_pct = round((female_df["Has_Disease"].sum() / len(female_df)) * 100, 2)

    age_grp = df.groupby("Age_Group", observed=False).agg(
        Total=("Has_Disease", "count"), Disease=("Has_Disease", "sum")
    )
    age_grp["Rate"] = (age_grp["Disease"] / age_grp["Total"] * 100).round(2)
    highest_age = str(age_grp["Rate"].idxmax())
    highest_rate = float(age_grp["Rate"].max())

    mean_bili_dis = round(df[df["Has_Disease"] == 1]["Total_Bilirubin"].mean(), 2)
    mean_bili_no = round(df[df["Has_Disease"] == 0]["Total_Bilirubin"].mean(), 2)
    corr_bili = round(df["Total_Bilirubin"].corr(df["Direct_Bilirubin"]), 2)
    corr_enzyme = round(
        df["Alamine_Aminotransferase"].corr(df["Aspartate_Aminotransferase"]), 2
    )

    st.markdown(f"""
| # | Insight | Finding |
|---|---------|---------|
| 1 | **Disease Prevalence** | {dis_full} of {total_full} patients ({dis_pct_full}%) diagnosed with Liver Disease |
| 2 | **Gender Disparity** | Males: {male_dis_pct}% disease rate &nbsp;·&nbsp; Females: {female_dis_pct}% disease rate |
| 3 | **Highest Risk Age Group** | **{highest_age} years** — {highest_rate}% disease prevalence |
| 4 | **Bilirubin Elevation** | Liver Disease avg: **{mean_bili_dis} mg/dL** vs Healthy: **{mean_bili_no} mg/dL** |
| 5 | **Biomarker Collinearity** | Bilirubin pair r = **{corr_bili}** · Transaminase pair r = **{corr_enzyme}** |
""")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "🩺 Liver Disease Analytics · ILPD Dataset · "
    "Built with Streamlit, Pandas, Matplotlib & Seaborn"
)
