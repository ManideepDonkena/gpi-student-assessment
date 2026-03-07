import json
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np
import os

# --- PATH CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ANALYSIS_DIR = os.path.dirname(SCRIPT_DIR) # Parent of scripts/ is analysis/
DATA_DIR = os.path.join(ANALYSIS_DIR, "data")
REPORTS_DIR = os.path.join(ANALYSIS_DIR, "reports")
IMAGES_DIR = os.path.join(ANALYSIS_DIR, "images")

# Ensure dirs exist
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def df_to_markdown(df):
    """
    Simple helper to convert DataFrame to Markdown table without 'tabulate' dependency.
    """
    if df.empty:
        return ""
    
    # Headers
    headers = list(df.columns)
    header_row = "| " + " | ".join(map(str, headers)) + " |"
    separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
    
    # Rows
    rows = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(map(str, row.values)) + " |")
    
    return "\n".join([header_row, separator_row] + rows)

def analyze_phase1():
    print("Starting Phase 1: Descriptive Statistics & Normality Analysis...")
    
    # Load cleaned BFI-44 data
    json_path = os.path.join(DATA_DIR, "bfi44_cleaned.json")
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found. Run clean_and_analyze.py first.")
        return

    with open(json_path, "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    
    # --- Data Prep ---
    # Safely extract score dictionaries
    def get_score(row, category):
        return row.get('recalculated_guna', {}).get(category, None)

    def get_bfi_score(row, trait):
        return row.get('recalculated_bfi', {}).get(trait, None)
        
    df['Sattva'] = df.apply(lambda r: get_score(r, 'Sattva'), axis=1)
    df['Rajas'] = df.apply(lambda r: get_score(r, 'Rajas'), axis=1)
    df['Tamas'] = df.apply(lambda r: get_score(r, 'Tamas'), axis=1)
    
    # Big Five
    bfi_traits = ['Extraversion', 'Agreeableness', 'Conscientiousness', 'Neuroticism', 'Openness']
    for trait in bfi_traits:
        df[trait] = df.apply(lambda r: get_bfi_score(r, trait), axis=1)
    
    # Demographics Normalization
    if 'demographics' in df.columns:
        # Extract demographics from the nested dict if columns don't exist
        demos = pd.json_normalize(df['demographics'])
        for col in demos.columns:
            df[col.capitalize()] = demos[col]

    # Normalize Gender strings
    if 'Gender' in df.columns:
        df['Gender'] = df['Gender'].str.title().str.strip()

    # --- REPORT GENERATION ---
    report = []
    
    # 1. Title & Objectives
    report.append("# Phase 1: Descriptive Statistics & Data Screening 📊\n")
    report.append(f"**Sample Size**: $N = {len(df)}$ (Cleaned Dataset)\n")
    
    report.append("## 1. Objectives of Phase 1")
    report.append("In personality research (like the Big Five or GPI), Phase 1 serves three critical functions:")
    report.append("1.  **Demographic Profiling**: Ensuring the sample is representative and identifying relevant subgroups (e.g., Gender, Year of Study).")
    report.append("2.  **Descriptive Baselines**: Establishing the 'norm' for the population. What is the average Sattva score for a university student?")
    report.append("3.  **Distributional Analysis (Normality Check)**:")
    report.append("    *   *Why it matters*: Most advanced statistical tests (ANOVA, Pearson Correlation, Factor Analysis) assume data follows a normal 'Bell Curve'.")
    report.append("    *   *Deviation*: Significant skewness indicates the need for non-parametric tests (e.g., Spearman Correlation instead of Pearson) or data transformation.")
    report.append("\n---")

    # 2. Demographics
    report.append("\n## 2. Demographic Profile")
    
    # Gender
    if 'Gender' in df.columns:
        gender_counts = df['Gender'].value_counts()
        gender_pct = df['Gender'].value_counts(normalize=True) * 100
        
        gender_df = pd.DataFrame({'Count': gender_counts, 'Percentage (%)': gender_pct.round(1)}).reset_index()
        gender_df.columns = ['Gender', 'Count', 'Percentage (%)']
        
        report.append("\n### Gender Distribution")
        report.append(df_to_markdown(gender_df))
    
    # Age (if numeric)
    if 'Age' in df.columns:
        df['Age_Num'] = pd.to_numeric(df['Age'], errors='coerce')
        stats_age = df['Age_Num'].describe()
        report.append(f"\n### Age Statistics")
        report.append(f"- **Mean**: {stats_age['mean']:.1f} years")
        report.append(f"- **Range**: {stats_age['min']} - {stats_age['max']} years")
        report.append(f"- **Std Dev**: {stats_age['std']:.2f}")

    report.append("\n---")
    
    # 3. Psychometric Profile (Descriptive Statistics)
    report.append("\n## 3. Psychometric Profile (Descriptive Statistics)")
    report.append("Detailed statistics for the three Guna traits and the Big Five personality traits.")
    
    # Table Header
    report.append("\n| Trait | Mean | Std. Error | Std. Dev | Skewness | Kurtosis | Shapiro-Wilk ($p$) | Normality |")
    report.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    
    # Combine lists
    all_traits = ['Sattva', 'Rajas', 'Tamas'] + bfi_traits
    
    table_rows = []
    detailed_sections = []

    for trait in all_traits:
        scores = df[trait].dropna()
        if len(scores) < 3: continue
        
        # Calculate Stats
        mean = scores.mean()
        # median = scores.median()
        std = scores.std()
        sem = stats.sem(scores) # Standard Error of Mean
        skew = scores.skew()
        kurt = scores.kurtosis()
        
        # Normality Test
        shapiro_stat, p_val = stats.shapiro(scores)
        is_normal = "✅ Yes" if p_val > 0.05 else "❌ No"
        
        # Interpretation of Skew
        skew_str = "Symmetrical"
        if skew > 1: skew_str = "High Positive Skew (Tail Right)"
        elif skew > 0.5: skew_str = "Moderate Positive Skew"
        elif skew < -1: skew_str = "High Negative Skew (Tail Left)"
        elif skew < -0.5: skew_str = "Moderate Negative Skew"

        # Add to Table
        table_rows.append(f"| **{trait}** | {mean:.2f} | {sem:.2f} | {std:.2f} | {skew:.2f} | {kurt:.2f} | {p_val:.4f} | {is_normal} |")
        
        # Collect detailed notes
        note = f"### {trait}\n"
        note += f"- **Distribution**: {is_normal} ($p={p_val:.4f}$)\n"
        note += f"- **Skewness**: {skew:.2f} ({skew_str})"
        
        # Contextual Interpretation
        if p_val > 0.05:
            note += "\n- **Implication**: Follows a normal distribution. Standard parametric tests valid."
        else:
            note += "\n- **Implication**: Deviates from normality."
            if skew < 0: note += " Scores are clustered at the high end (Negative Skew)."
            if skew > 0: note += " Scores are clustered at the low end (Positive Skew)."

        # Plot Histogram
        plt.figure(figsize=(7, 5))
        # Color based on group
        color = '#4a90e2' if trait in ['Sattva', 'Rajas', 'Tamas'] else '#e24a4a'
        
        counts, bins, patches = plt.hist(scores, bins=15, color=color, alpha=0.7, rwidth=0.85, density=True)
        
        # Add Density Line (KDE)
        try:
            density = stats.gaussian_kde(scores)
            xmin, xmax = plt.xlim()
            x = np.linspace(xmin, xmax, 100)
            plt.plot(x, density(x), 'r-', linewidth=2, label='Density Curve')
        except:
            pass # KDE might fail on constant data
            
        # Add Normal Curve for comparison
        xmin, xmax = plt.xlim()
        x_norm = np.linspace(xmin, xmax, 100)
        p_norm = stats.norm.pdf(x_norm, mean, std)
        plt.plot(x_norm, p_norm, 'k--', linewidth=1.5, alpha=0.6, label='Normal Dist.')

        plt.title(f'Distribution of {trait}\nMean={mean:.2f}, SD={std:.2f}, Skew={skew:.2f}')
        plt.xlabel('Score')
        plt.ylabel('Density')
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        image_name = f"dist_{trait.lower()}.png"
        
        # Save to IMAGES_DIR
        plt.savefig(os.path.join(IMAGES_DIR, image_name))
        plt.close()
        
        # Embed Image
        note += f"\n\n![Distribution of {trait}](../images/{image_name})\n"
        detailed_sections.append(note)

    # Append Table Rows
    report.extend(table_rows)

    # 4. Detailed Interpretation
    report.append("\n## 4. Detailed Interpretation & Implications")
    for section in detailed_sections:
        report.append(section)

    report.append("\n### Interpretation Guidelines")
    report.append("- **Sattva (Balance)** often shows a 'Negative Skew' in healthy populations (Self-Selection bias).")
    report.append("- **Tamas (Inertia)** often shows a 'Positive Skew' (most students are active/low Tamas).")
    report.append("- **Neuroticism**: High scores indicate stress/instability; usually skewed positively in healthy populations.")
    report.append("- **Conscientiousness/Agreeableness**: Often negatively skewed (most people rate themselves highly).")
    report.append("- **Methodological Note**: If normality is violated (❌), we should use **Spearman's Rank Correlation** in Phase 3 instead of Pearson's.")

    # Save Report
    report_path = os.path.join(REPORTS_DIR, "PHASE1_DETAILED_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print(f"Analysis Complete. Generated: {report_path}")
    print(f"Generated Plots in: {IMAGES_DIR}")

if __name__ == "__main__":
    analyze_phase1()
