# Power BI Dashboard Guide - Liver Disease Analysis

This guide provides step-by-step instructions for building a healthcare analytics dashboard in **Power BI Desktop** using the cleaned Indian Liver Patient Dataset (`liver_cleaned.csv`).

---

## 1. Data Ingestion
1. Open **Power BI Desktop**.
2. Click **Get Data** > **Text/CSV**.
3. Select `data/processed/liver_cleaned.csv`.
4. Click **Load** (or **Transform Data** to verify column data types:
   - `Age`, `Total_Bilirubin`, `Direct_Bilirubin`, `Alkaline_Phosphotase`, `Alamine_Aminotransferase`, `Aspartate_Aminotransferase`, `Total_Protiens`, `Albumin`, `Albumin_and_Globulin_Ratio`: **Decimal Number / Whole Number**
   - `Gender`: **Text** (`Male` / `Female`)
   - `Disease_Label`: **Text** (`Liver Disease` / `No Disease`)
   - `Age_Group`: **Text** (`0-20`, `21-40`, `41-60`, `60+`)

---

## 2. Core DAX Measures
Create a dedicated table named `_Measures` or add the following DAX measures to `liver_cleaned`:

### Measure 1: Total Patients
```dax
Total Patients = COUNTROWS(liver_cleaned)
```

### Measure 2: Disease %
```dax
Disease % = 
DIVIDE(
    CALCULATE(
        COUNTROWS(liver_cleaned),
        liver_cleaned[Disease_Label] = "Liver Disease"
    ),
    [Total Patients],
    0
)
```
*(Format as Percentage with 1 decimal place, e.g., `71.4%`)*

### Measure 3: Average Bilirubin
```dax
Avg Bilirubin = AVERAGE(liver_cleaned[Total_Bilirubin])
```
*(Format as Decimal with 2 decimal places)*

### Measure 4: Average Age
```dax
Avg Age = AVERAGE(liver_cleaned[Age])
```
*(Format as Decimal with 1 decimal place)*

### Measure 5: Male Patient Count
```dax
Male Patients = CALCULATE(COUNTROWS(liver_cleaned), liver_cleaned[Gender] = "Male")
```

### Measure 6: Female Patient Count
```dax
Female Patients = CALCULATE(COUNTROWS(liver_cleaned), liver_cleaned[Gender] = "Female")
```

---

## 3. Visualizations Layout

### Header / Title Banner
- Add a text box: `LIVER DISEASE CLINICAL ANALYTICS DASHBOARD`
- Subtitle: `Diagnostic Insights & Biomarker Analysis (ILPD Cohort - 583 Patients)`

### Row 1: KPI Cards (Card Visuals)
1. **Total Patients**: Displays `583`
2. **Disease Prevalence %**: Displays `71.4%`
3. **Average Patient Age**: Displays `44.7 Years`
4. **Average Total Bilirubin**: Displays `3.30 mg/dL`

### Row 2: Charts & Breakdown
1. **Pie / Donut Chart**: Disease Distribution
   - **Legend**: `Disease_Label`
   - **Values**: `[Total Patients]`
   - **Colors**: Red (`#e74c3c`) for Liver Disease, Green (`#2ecc71`) for No Disease.
2. **Clustered Column Chart**: Gender vs Diagnosis
   - **X-axis**: `Gender`
   - **Legend**: `Disease_Label`
   - **Y-axis**: `[Total Patients]`
3. **Stacked Bar Chart**: Disease Prevalence by Age Group
   - **Y-axis**: `Age_Group`
   - **X-axis**: `[Total Patients]`
   - **Legend**: `Disease_Label`

### Row 3: Interactive Slicers & Filters
- **Gender Slicer**: Tile / Dropdown (`All`, `Male`, `Female`)
- **Age Group Slicer**: Multi-select buttons (`0-20`, `21-40`, `41-60`, `60+`)
- **Disease Status Slicer**: Dropdown (`Liver Disease`, `No Disease`)

---

## 4. Verification Check
- Selecting **Male** on the slicer should filter total patients to **441** and Disease % to **73.5%**.
- Selecting **Female** should filter total patients to **142** and Disease % to **64.8%**.
- Selecting **41-60** age group should show **245** patients with **74.3%** disease prevalence.
