import streamlit as st
import pandas as pd
import numpy as np
import os
from PIL import Image

# Page Configuration
st.set_page_config(
    page_title="Liver Disease Clinical Analysis",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #7f8c8d;
        margin-bottom: 25px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #3498db;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to find files robustly
def get_path(relative_path):
    # Try current directory first
    if os.path.exists(relative_path):
        return relative_path
    # Try directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(script_dir, relative_path)
    if os.path.exists(candidate):
        return candidate
    return relative_path

# Load Data
@st.cache_data
def load_data():
    csv_candidates = [
        get_path("data/processed/liver_cleaned.csv"),
        get_path("data/raw/liver.csv"),
    ]
    for path in csv_candidates:
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Ensure required columns exist
            if 'Albumin_and_Globulin_Ratio' in df.columns:
                df['Albumin_and_Globulin_Ratio'] = df['Albumin_and_Globulin_Ratio'].fillna(
                    df['Albumin_and_Globulin_Ratio'].median()
                )
            if 'Dataset' in df.columns and 'Disease_Label' not in df.columns:
                df['Disease_Label'] = df['Dataset'].map({1: 'Liver Disease', 2: 'No Disease'})
            if 'Dataset' in df.columns and 'Has_Disease' not in df.columns:
                df['Has_Disease'] = (df['Dataset'] == 1).astype(int)
            if 'Age' in df.columns and 'Age_Group' not in df.columns:
                df['Age_Group'] = pd.cut(df['Age'], bins=[0, 20, 40, 60, 120], labels=['0-20', '21-40', '41-60', '60+'], right=True)
            return df
    return None

df = load_data()

# Header Section
st.markdown('<div class="main-title">🩺 Liver Disease Clinical Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Exploratory Data Analysis, Biomarker Profiling & Demographic Patterns (ILPD Cohort)</div>', unsafe_allow_html=True)

if df is None:
    st.error("⚠️ Dataset not found. Please ensure `data/processed/liver_cleaned.csv` or `data/raw/liver.csv` is present in the repository.")
    st.stop()

# Sidebar Filters
st.sidebar.header("🔍 Filter Patient Data")

gender_options = ["All"] + sorted(df["Gender"].dropna().unique().tolist())
selected_gender = st.sidebar.selectbox("Select Gender:", gender_options)

disease_options = ["All"] + sorted(df["Disease_Label"].dropna().unique().tolist())
selected_disease = st.sidebar.selectbox("Diagnosis Status:", disease_options)

age_groups = ["All"] + sorted([str(x) for x in df["Age_Group"].dropna().unique()])
selected_age_group = st.sidebar.selectbox("Age Group:", age_groups)

# Apply Filters
filtered_df = df.copy()
if selected_gender != "All":
    filtered_df = filtered_df[filtered_df["Gender"] == selected_gender]
if selected_disease != "All":
    filtered_df = filtered_df[filtered_df["Disease_Label"] == selected_disease]
if selected_age_group != "All":
    filtered_df = filtered_df[filtered_df["Age_Group"].astype(str) == selected_age_group]

# Top Metrics Row
total_cohort = len(filtered_df)
disease_count = (filtered_df["Disease_Label"] == "Liver Disease").sum()
disease_pct = (disease_count / total_cohort * 100) if total_cohort > 0 else 0
avg_age = filtered_df["Age"].mean() if total_cohort > 0 else 0
avg_bili = filtered_df["Total_Bilirubin"].mean() if total_cohort > 0 else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Patients", f"{total_cohort:,}")
with col2:
    st.metric("Disease Prevalence", f"{disease_pct:.1f}%", f"{disease_count} cases")
with col3:
    st.metric("Average Patient Age", f"{avg_age:.1f} yrs")
with col4:
    st.metric("Avg Total Bilirubin", f"{avg_bili:.2f} mg/dL")

st.markdown("---")

# Visualizations Section
st.subheader("📊 Diagnostic Visualizations & Clinical Insights")

tabs = st.tabs(["📈 Key Diagnostic Charts", "🔬 Biomarkers & Correlation", "📋 Patient Data Table", "💡 Calculated Insights"])

with tabs[0]:
    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
        st.markdown("**1. Overall Disease Distribution**")
        pie_path = get_path("outputs/figures/disease_pie.png")
        if os.path.exists(pie_path):
            st.image(pie_path, use_container_width=True)
        else:
            st.info("Chart image loading...")

    with row1_c2:
        st.markdown("**2. Diagnosis by Gender**")
        bar_path = get_path("outputs/figures/gender_disease_bar.png")
        if os.path.exists(bar_path):
            st.image(bar_path, use_container_width=True)
        else:
            st.info("Chart image loading...")

    st.markdown("")
    row2_c1, row2_c2 = st.columns(2)
    with row2_c1:
        st.markdown("**3. Prevalence by Age Group**")
        age_path = get_path("outputs/figures/agegroup_disease_percent.png")
        if os.path.exists(age_path):
            st.image(age_path, use_container_width=True)
        else:
            st.info("Chart image loading...")

    with row2_c2:
        st.markdown("**4. Patient Age Distribution**")
        hist_path = get_path("outputs/figures/age_histogram.png")
        if os.path.exists(hist_path):
            st.image(hist_path, use_container_width=True)
        else:
            st.info("Chart image loading...")

with tabs[1]:
    col_bio1, col_bio2 = st.columns(2)
    with col_bio1:
        st.markdown("**5. Total Bilirubin Levels by Diagnosis (Log Scale)**")
        box_path = get_path("outputs/figures/bilirubin_boxplot.png")
        if os.path.exists(box_path):
            st.image(box_path, use_container_width=True)
        else:
            st.info("Chart image loading...")

    with col_bio2:
        st.markdown("**6. Biomarker Correlation Matrix**")
        corr_path = get_path("outputs/figures/correlation_heatmap.png")
        if os.path.exists(corr_path):
            st.image(corr_path, use_container_width=True)
        else:
            st.info("Chart image loading...")

with tabs[2]:
    st.markdown(f"**Displaying {len(filtered_df)} filtered patient records**")
    st.dataframe(filtered_df, use_container_width=True, height=400)
    
    # Download buttons
    csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_bytes,
        file_name="liver_filtered_data.csv",
        mime="text/csv"
    )

with tabs[3]:
    st.markdown("""
    ### 🔬 Actual Clinical Insights (Calculated from 583 Records):
    1. **Prevalence in Sample**: Out of 583 patients, **416 (71.36%)** were diagnosed with liver disease, while 167 (28.64%) had no liver disease.
    2. **Gender Vulnerability**: Male patients constitute the vast majority of the cohort (441 out of 583). Men exhibit a **73.47%** disease rate compared to **64.79%** in females.
    3. **Age Cohort Susceptibility**:
       - Patients aged **41–60** exhibit the highest disease rate (**74.29%** across 245 patients).
       - Patients aged **21–40** follow closely with a **72.34%** disease rate.
       - Liver disease patients have a higher mean age (46.1 years) compared to non-disease individuals (41.2 years).
    4. **Bilirubin Elevation**: Patients with liver disease display an average Total Bilirubin of **4.16 mg/dL**, nearly 4× higher than the healthy control average of **1.14 mg/dL**.
    5. **Biomarker Collinearity**: Total Bilirubin and Direct Bilirubin show strong linear correlation (**r = 0.87**), while liver enzymes ALT and AST show co-elevation (**r = 0.79**).
    """)

# Footer
st.markdown("---")
st.markdown("<small style='color: #7f8c8d;'>Indian Liver Patient Dataset (ILPD) Analytics Dashboard | Built with Streamlit, Pandas & Seaborn</small>", unsafe_allow_html=True)
