import json
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
import os

def analyze_phase4():
    # Load cleaned BFI-44 data
    json_path = "bfi44_cleaned.json"
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    with open(json_path, "r") as f:
        data = json.load(f)

    # Extract Data
    rows = []
    for s in data:
        row = {}
        # Guna Scores
        gunas = s.get('recalculated_guna', {})
        for k, v in gunas.items():
            row[k] = v
            
        # Demographics
        demo = s.get('demographics', {})
        row['Gender'] = demo.get('gender', 'Unknown').strip().title()
        row['Year'] = demo.get('year', 'Unknown')
        
        rows.append(row)
        
    df = pd.DataFrame(rows)
    
    report = ["# Phase 4: Hypothesis Testing (Group Differences)\n"]
    report.append(f"**Sample**: N={len(data)} | **Tests**: T-test (Gender), ANOVA (Year)\n")
    
    # --- 1. Gender Differences (T-Test) ---
    report.append("## 1. Gender Analysis (Male vs. Female)")
    
    males = df[df['Gender'] == 'Male']
    females = df[df['Gender'] == 'Female']
    
    if len(males) > 1 and len(females) > 1:
        report.append(f"**Comparison**: Male (N={len(males)}) vs. Female (N={len(females)})\n")
        
        header = "| Guna | Male Mean | Female Mean | T-Statistic | p-value | Significance |"
        sep = "| :--- | :--- | :--- | :--- | :--- | :--- |"
        report.append(header)
        report.append(sep)
        
        for guna in ['Sattva', 'Rajas', 'Tamas']:
            m_scores = males[guna]
            f_scores = females[guna]
            
            t_stat, p_val = stats.ttest_ind(m_scores, f_scores, equal_var=False)
            sig = "**SIGNIFICANT**" if p_val < 0.05 else "ns"
            
            report.append(f"| {guna} | {m_scores.mean():.2f} | {f_scores.mean():.2f} | {t_stat:.2f} | {p_val:.4f} | {sig} |")
            
            # Plot Boxplot if significant or close
            if p_val < 0.10: # Generous threshold for visibility
                plt.figure(figsize=(6, 5))
                plt.boxplot([m_scores, f_scores], labels=['Male', 'Female'])
                plt.title(f'{guna} by Gender (p={p_val:.3f})')
                plt.ylabel('Score')
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.savefig(f'phase4_gender_{guna.lower()}.png')
                plt.close()
                report.append(f"\n![{guna} Gender Differences](file:///c:/Users/donke/Desktop/IKS_Work/Gunabased%20Survey/student-assessment/analysis/phase4_gender_{guna.lower()}.png)\n")

    else:
        report.append("\n*Insufficient data for gender comparison (need at least 2 per group).*\n")
        
    # --- 2. Year of Study (ANOVA) ---
    report.append("\n## 2. Year of Study Analysis")
    
    # Clean Year Data (Assuming strings like "1st Year", "2", etc.)
    # Simple heuristic: extract first digit
    def parse_year(y):
        y = str(y)
        if '1' in y: return 1
        if '2' in y: return 2
        if '3' in y: return 3
        if '4' in y: return 4
        return None
        
    df['Year_Num'] = df['Year'].apply(parse_year)
    valid_years = df.dropna(subset=['Year_Num'])
    
    year_groups = valid_years.groupby('Year_Num')
    counts = year_groups.size()
    
    report.append(f"**Distribution**: {counts.to_dict()}\n")
    
    # Needs at least 2 groups with data
    if len(counts) >= 2:
        header = "| Guna | F-Statistic | p-value | Trend |"
        sep = "| :--- | :--- | :--- | :--- |"
        report.append(header)
        report.append(sep)
        
        for guna in ['Sattva', 'Rajas', 'Tamas']:
            groups = [group[guna].values for name, group in year_groups]
            
            if len(groups) < 2: continue
            
            f_stat, p_val = stats.f_oneway(*groups)
            sig = "**SIGNIFICANT**" if p_val < 0.05 else "ns"
            
            report.append(f"| {guna} | {f_stat:.2f} | {p_val:.4f} | {sig} |")
            
            # Plot Trend (Always plot for visibility as per user request)
            if True:
                plt.figure(figsize=(6, 5))
                # Boxplot per year
                plt.boxplot(groups, labels=sorted(valid_years['Year_Num'].unique()))
                plt.title(f'{guna} by Year of Study (p={p_val:.3f})')
                plt.xlabel('Year')
                plt.ylabel('Score')
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.savefig(f'phase4_year_{guna.lower()}.png')
                plt.close()
                report.append(f"\n![{guna} Year Trend](file:///c:/Users/donke/Desktop/IKS_Work/Gunabased%20Survey/student-assessment/analysis/phase4_year_{guna.lower()}.png)\n")
    else:
        report.append("\n*Insufficient year variance for ANOVA.*\n")

    with open("PHASE4_HYPOTHESIS_REPORT.md", "w") as f:
        f.write("\n".join(report))
        
    print("Phase 4 Analysis Complete. Report saved to PHASE4_HYPOTHESIS_REPORT.md")

if __name__ == "__main__":
    analyze_phase4()
