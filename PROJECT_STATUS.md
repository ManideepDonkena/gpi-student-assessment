# Project Status: Guna Personality Inventory (GPI)

## 🚀 Mission & Goal
**Mission**: To scientize and validate Ancient Indian Knowledge Systems (IKS) by integrating the *Triguna* framework (Sattva, Rajas, Tamas) with modern psychometric standards.

**Goal**: Develop a validated, reliable, and bias-free assessment tool ("The Guna Personality Inventory") to help potential students and researchers understand personality archetypes through an indigenous lens.

---

## 📅 Current Status: **Analysis Complete / Validation Successful**
*As of February 14, 2026*

The project has moved from **Data Collection** to **Final Validation**. The GPI has been proven to be a statistically valid instrument with high reliability and strong convergent validity with Western models (Big Five).

---

## ✅ Completed Sub-Tasks & Milestones

### 1. Assessment Development 🛠️
- [x] **Questionnaire Design**: Curated and refined item bank for Sattva, Rajas, and Tamas.
- [x] **Web Application Built**: Developed a responsive, interactive web app (`index.html`, `src/`) for data collection.
- [x] **Real-time Scoring**: Implemented client-side scoring logic (`scoring.js`) for immediate user feedback.

### 2. Data Collection 💾
- [x] **Pilot Study**: Collected responses from university cohorts.
- [x] **Data Processing Pipeline**: Built scripts (`extract_firebase_data.py`, `clean_and_analyze.py`) to automate data cleaning.
- [x] **Integration**: Merged Guna scores with Big Five (BFI-44) data for cross-validation.

### 3. Psychometric Validation (The Core Science) 📊
- [x] **Reliability Testing**: Achieved Cronbach's Alpha > 0.90 for all three subscales (Excellent consistency).
- [x] **Refinement**: Removed weak items to strictly define factor boundaries.
- [x] **Exploratory Factor Analysis (EFA)**:
    - Confirmed the 3-Factor structure (Sattva vs. Tamas vs. Rajas).
    - Identified "Inertia" (Tamas) as the dominant primary factor.

### 4. Advanced Analysis 🧠
- [x] **Convergent Validity**: Mapped Gunas to Big Five traits:
    - *Sattva* ↔ *Conscientiousness* ($r=0.61$)
    - *Tamas* ↔ *Neuroticism* ($r=0.65$)
- [x] **Cluster Analysis**: Identified 3 distinct student archetypes using K-Means clustering:
    1.  *The Sattvic Ideal* (Balanced/Yogi)
    2.  *The Distressed/Anxious* (High Tamas/Rajas)
    3.  *Sattva-Dominant* (Average/Typical)
- [x] **Demographic Analysis**:
    - **Gender**: Confirmed no significant gender bias ($p > 0.27$).
    - **Maturation Effect**: Discovered significant personality growth (Standardization) from Year 1 to Year 4.

### 5. Reporting 📝
- [x] Generated detailed `FINAL_COMPREHENSIVE_REPORT.md`.
- [x] Created visual assets (Scree Plots, Heatmaps, Radar Charts).

---

## 🔮 Next Steps
- [ ] **Publication**: Prepare a research paper titled *"Psychometric Validation of the Guna Personality Inventory in Higher Education"*.
- [ ] **Intervention Design**: Create support programs for the "Distressed" cluster identified in the analysis.
- [ ] **Longitudinal Study**: Track the current Year 1 cohort through their graduation to verify the "Maturation Effect".
