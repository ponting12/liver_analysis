# Liver Disease Analysis - Exploratory Data Analysis & Analytics Dashboard

A beginner-friendly, end-to-end college Data Analytics project analyzing the **Indian Liver Patient Dataset (ILPD)** from Kaggle using Python, Excel, and Power BI.

---

## 📌 Project Overview
Liver disease is among the leading causes of morbidity worldwide. Early diagnosis using routine biochemical liver function tests significantly improves clinical outcomes. This project conducts a systematic exploratory data analysis (EDA) on patient clinical records to identify demographic trends, abnormal enzyme elevations, and key diagnostic indicators.

### 🎯 Objectives
- **Data Ingestion & Verification**: Validate dataset integrity (583 records, 11 clinical features).
- **Data Preprocessing & Cleaning**: Impute missing biomarker values using median imputation, encode categorical variables, and categorize patients into demographic age groups.
- **Exploratory Data Analysis (EDA)**: Calculate statistical prevalence across age cohorts, genders, and biochemical markers.
- **Diagnostic Visualizations**: Produce professional charts illustrating disease distribution, biomarker boxplots, correlation matrices, and demographic distributions.
- **Business Intelligence & Reporting**: Export clean data pipelines to CSV and multi-sheet Excel workbooks, with DAX-driven Power BI dashboard specifications.

---

## 🗂️ Project Directory Structure

```text
liver_disease_project/
├── liver_analysis.ipynb          # Fully executed Jupyter Notebook with embedded plots & outputs
├── requirements.txt              # Required Python libraries
├── README.md                     # Comprehensive project documentation
├── download_dataset.py           # Automated Kagglehub dataset fetcher
├── .gitignore                    # Git exclusions
├── data/
│   ├── raw/
│   │   └── liver.csv             # Raw ILPD dataset (583 rows x 11 columns)
│   └── processed/
│       ├── liver_cleaned.csv     # Cleaned dataset ready for Power BI
│       └── liver_validation.xlsx # Multi-sheet validation workbook
├── outputs/
│   └── figures/
│       ├── disease_pie.png               # Disease distribution (71.4% vs 28.6%)
│       ├── gender_disease_bar.png        # Gender vs diagnosis comparison
│       ├── agegroup_disease_percent.png  # Disease prevalence across age groups
│       ├── bilirubin_boxplot.png         # Total Bilirubin elevation by diagnosis
│       ├── correlation_heatmap.png       # Correlation matrix of biomarkers
│       └── age_histogram.png             # Age distribution with density curves
└── powerbi/
    └── powerbi_guide.md          # Step-by-step Power BI setup with DAX measures
```

---

## 📊 Dataset Description
The dataset used is the **Indian Liver Patient Dataset (ILPD)** from the UCI Machine Learning Repository / Kaggle.
- **Total Records:** 583 patient records
- **Total Attributes:** 11 features (10 clinical biomarkers + 1 target diagnosis)
- **Target Feature (`Dataset`):**
  - `1`: Liver Disease patient (416 records / 71.36%)
  - `2`: Non-liver patient (167 records / 28.64%)

### Clinical Features:
| Feature | Description | Normal Reference / Type |
| :--- | :--- | :--- |
| `Age` | Age of patient | Numerical (4 to 90 years) |
| `Gender` | Biological sex | Categorical (Male: 441, Female: 142) |
| `Total_Bilirubin` | Total blood bilirubin | Serum biomarker (mg/dL) |
| `Direct_Bilirubin` | Conjugated bilirubin | Serum biomarker (mg/dL) |
| `Alkaline_Phosphotase` | ALP enzyme level | Serum biomarker (IU/L) |
| `Alamine_Aminotransferase` | ALT / SGPT enzyme | Liver enzyme (IU/L) |
| `Aspartate_Aminotransferase`| AST / SGOT enzyme | Liver enzyme (IU/L) |
| `Total_Protiens` | Serum total protein | g/dL |
| `Albumin` | Serum albumin | g/dL |
| `Albumin_and_Globulin_Ratio`| A/G ratio | 4 missing values filled with median (0.93) |
| `Dataset` | Diagnostic class label | 1 = Disease, 2 = No Disease |

---

## 🔬 Key Analytical Findings (Calculated from Real Data)
1. **High Disease Prevalence in Sample:** Out of 583 records, **416 (71.36%)** are diagnosed with liver disease and **167 (28.64%)** have no liver condition.
2. **Gender Breakdown:** Male patients constitute **75.6%** of the cohort (441 patients). Men show a higher disease diagnosis rate (**73.47%**) compared to females (**64.79%**).
3. **Age Cohort Vulnerability:** Liver disease peaks in middle-aged and older adults:
   - **41–60 years:** Highest disease prevalence (**74.29%** across 245 patients)
   - **21–40 years:** Second highest prevalence (**72.34%** across 188 patients)
   - **60+ years:** **67.89%** prevalence (109 patients)
   - **0–20 years:** **58.54%** prevalence (41 patients)
4. **Significant Bilirubin Elevation:** Mean Total Bilirubin among liver patients is **4.16 mg/dL** versus **1.14 mg/dL** in healthy controls.
5. **High Biomarker Co-linearity:**
   - Total Bilirubin and Direct Bilirubin show strong linear correlation ($r = 0.87$).
   - Liver transaminases (ALT and AST) show pronounced co-elevation ($r = 0.79$).

---

## 🛠️ Installation & Execution

### 1. Prerequisites
Ensure Python 3.9+ and Git are installed.

### 2. Setup Environment
```bash
# Clone the repository
git clone https://github.com/ponting12/liver_disease_project.git
cd liver_disease_project

# Install required packages
pip install -r requirements.txt
```

### 3. (Optional) Re-download Dataset
If `data/raw/liver.csv` is not present:
```bash
python download_dataset.py
```

### 4. Run Notebook
```bash
jupyter notebook liver_analysis.ipynb
```
The notebook runs end-to-end and outputs all charts and Excel sheets cleanly.

---

## 📈 Power BI Dashboard Highlights
The processed file `data/processed/liver_cleaned.csv` integrates directly into Power BI:
- **KPI Cards:** Total Patients (583), Disease % (71.4%), Avg Bilirubin (3.30 mg/dL), Avg Age (44.7 years).
- **Interactive Visuals:**
  - Disease Distribution (Pie/Donut)
  - Gender vs. Diagnosis (Clustered Column)
  - Prevalence by Age Group (Bar Chart)
  - Biomarker distribution (Box Plot / Scatter)
- Complete DAX measures and layout steps are documented in [`powerbi/powerbi_guide.md`](powerbi/powerbi_guide.md).

---

## ⚠️ Limitations & Future Scope
- **Limitations:** Modest sample size (583 observations) from a single geographic region; class imbalance towards positive liver disease cases.
- **Future Scope:** Implement supervised classification models (Logistic Regression, Random Forest, XGBoost) to predict liver disease risk with cross-validation and feature importance analysis.

---

## 📜 Technologies Used
- **Language:** Python
- **Libraries:** Pandas, NumPy, Matplotlib, Seaborn, openpyxl, kagglehub
- **BI Tool:** Microsoft Power BI Desktop
- **Spreadsheet:** Microsoft Excel (.xlsx)
