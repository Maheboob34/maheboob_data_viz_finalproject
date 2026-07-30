# 🏥 U.S. Hospital Quality Dashboard

## Overview

This project presents an interactive Streamlit dashboard that explores hospital quality, patient experience, and readmission outcomes across more than 3,000 hospitals in the United States. Using publicly available Centers for Medicare & Medicaid Services (CMS) data, the dashboard investigates how organizational characteristics and patient experience factors are associated with hospital performance.

---

## Project Title

**U.S. Hospital Quality and Readmission Analysis: Exploring Organizational and Patient Experience Factors**

---

## Research Objective

The primary objective of this project is to investigate the organizational and patient experience factors associated with hospital readmission performance in U.S. hospitals.

The analysis focuses on the following questions:

- Do hospitals with higher CMS ratings achieve lower readmission ratios?
- Which patient experience dimensions are most strongly associated with readmission performance?
- How does hospital ownership affect readmission outcomes?
- Does the presence of emergency services influence patient experience?
- Which states perform best in terms of patient experience and readmission outcomes?
- Do different medical conditions have different readmission patterns?
- How do 1-star and 5-star hospitals compare?
- Which hospitals achieve the highest overall quality scores?
- Is patient experience associated with objective clinical quality?
- Which organizational factors best explain variation in readmission performance?

---

## Dataset

The project uses publicly available datasets from the Centers for Medicare & Medicaid Services (CMS):

- Hospital General Information
- HCAHPS Patient Experience Data
- Hospital Readmissions Reduction Program Data

The datasets were merged using the **Facility ID**.

### Key Variables

- Facility ID
- Facility Name
- State
- Hospital Overall Rating
- Hospital Ownership
- Emergency Services
- Excess Readmission Ratio
- Patient Experience Index
- Doctor Communication
- Nurse Communication
- Care Transition
- Cleanliness
- Overall Patient Rating
- Readmission Quality Measures
- Mortality Measures
- Safety Measures

---

## Technologies Used

- Python
- Streamlit
- Pandas
- Plotly
- Statsmodels
- NumPy

---

## Dashboard Features

✅ Interactive sidebar filters

✅ Key performance indicators (KPIs)

✅ State-level hospital analysis

✅ Readmission and patient experience visualizations

✅ Hospital ownership comparisons

✅ Correlation analysis

✅ Top-performing hospitals ranking

✅ Regression analysis results

---

## Project Structure

```text
Hospital_Quality_Dashboard/

├── app.py
├── hospital_quality_final.csv
├── requirements.txt
├── README.md
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/your-repository-name.git
```

Move into the project directory:

```bash
cd your-repository-name
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit application:

```bash
streamlit run app.py
```



## Dashboard Preview

The dashboard provides an interactive environment for exploring hospital quality, patient experience, and readmission outcomes across U.S. hospitals.

---

## License

This project is for academic and educational purposes only.

---

