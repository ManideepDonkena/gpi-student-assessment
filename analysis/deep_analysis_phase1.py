import json
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
import os

def analyze_phase1():
    # Load cleaned BFI-44 data
    json_path = "bfi44_cleaned.json"
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found. Run clean_and_analyze.py first.")
        return

    with open(json_path, "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    
    # --- 1. Demographics ---
    # Normalize Gender
    if 'Gender' in df.columns:
        df['Gender'] = df['Gender'].str.title().str.strip()
    
    # Safely extract scores
    def get_score(row, category):
        return row.get('recalculated_guna', {}).get(category, None)
        
    df['Sattva'] = df.apply(lambda r: get_score(r, 'Sattva'), axis=1)
    df['Rajas'] = df.apply(lambda r: get_score(r, 'Rajas'), axis=1)
    df['Tamas'] = df.apply(lambda r: get_score(r, 'Tamas'), axis=1)

    # Report Construction
    report = ["# Phase 1: Demographics & Distributions Analysis\n"]
    report.append(f"**Cohort**: BFI-44 | **Sample Size**: N={len(df)}\n")

    # Demographics Table
    report.append("## 1. Demographic Profile\n")
    
    # Age
    if 'Age' in df.columns:
        # Convert to numeric, coerce errors
        df['Age_Num'] = pd.to_numeric(df['Age'], errors='coerce')
        age_stats = df['Age_Num'].describe()
        report.append(f"**Age**: Mean={age_stats['mean']:.1f}, Min={age_stats['min']}, Max={age_stats['max']}\n")
    
    # Gender
    if 'Gender' in df.columns:
        gender_counts = df['Gender'].value_counts()
        report.append("**Gender Distribution**:")
        report.append(gender_counts.to_markdown())
        report.append("\n")

    # Major
    if 'Major' in df.columns:
        major_counts = df['Major'].value_counts().head(5) # Top 5
        report.append("**Top 5 Majors**:")
        report.append(major_counts.to_markdown())
        report.append("\n")

    # Year
    if 'Year' in df.columns:
        year_counts = df['Year'].value_counts().sort_index()
        report.append("**Year of Study**:")
        report.append(year_counts.to_markdown())
        report.append("\n")

    # --- 2. Distributions & Normality ---
    report.append("## 2. Guna Distributions (Normality Check)\n")
    report.append("| Guna | Mean | Std Dev | Skewness | Kurtosis | Shapiro-Wilk p-value | Normality |")
    report.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    gunas = ['Sattva', 'Rajas', 'Tamas']
    
    # Create simple text histograms for the report (optional, but plots are better)
    # We will save plots to files
    
    for guna in gunas:
        scores = df[guna].dropna()
        if len(scores) < 3:
            continue
            
        mean = scores.mean()
        std = scores.std()
        skew = scores.skew()
        kurt = scores.kurtosis()
        
        # Shapiro-Wilk test
        stat, p_val = stats.shapiro(scores)
        is_normal = "Yes" if p_val > 0.05 else "No (Significant Deviation)"
        
        report.append(f"| {guna} | {mean:.2f} | {std:.2f} | {skew:.2f} | {kurt:.2f} | {p_val:.4f} | {is_normal} |")

        # Plot Histogram
        plt.figure(figsize=(6, 4))
        plt.hist(scores, bins=10, color='skyblue', edgecolor='black', alpha=0.7)
        plt.title(f'Distribution of {guna} (N={len(scores)})')
        plt.xlabel('Score')
        plt.ylabel('Frequency')
        plt.axvline(mean, color='red', linestyle='dashed', linewidth=1, label=f'Mean: {mean:.2f}')
        plt.legend()
        plt.grid(axis='y', alpha=0.5)
        plt.savefig(f"dist_{guna.lower()}.png")
        plt.close()

    report.append("\n### Interpretation")
    report.append("- **Shapiro-Wilk Test**: A p-value > 0.05 indicates the data is likely normally distributed.")
    report.append("- **Visual Inspection**: See generated `dist_*.png` files.")
    
    with open("PHASE1_DEMOGRAPHICS_REPORT.md", "w") as f:
        f.write("\n".join(report))
        
    print("Phase 1 Analysis Complete. Report saved to PHASE1_DEMOGRAPHICS_REPORT.md")

if __name__ == "__main__":
    analyze_phase1()
