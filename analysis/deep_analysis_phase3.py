import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

def analyze_phase3():
    # Load cleaned BFI-44 data
    json_path = "bfi44_cleaned.json"
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    with open(json_path, "r") as f:
        data = json.load(f)

    # Extract Scores
    rows = []
    for s in data:
        row = {}
        # Guna Scores
        gunas = s.get('recalculated_guna', {})
        for k, v in gunas.items():
            row[k] = v
            
        # Big Five Scores
        bfi = s.get('recalculated_bfi', {})
        for k, v in bfi.items():
            row[f"BFI_{k}"] = v
            
        rows.append(row)
        
    df = pd.DataFrame(rows)
    
    # Select Columns for Correlation
    guna_cols = ['Sattva', 'Rajas', 'Tamas']
    bfi_cols = [c for c in df.columns if c.startswith("BFI_")]
    
    # Calculate Correlation Matrix
    corr_matrix = df[guna_cols + bfi_cols].corr()
    
    # Extract just the Guna x BigFive block
    final_corr = corr_matrix.loc[guna_cols, bfi_cols]
    
    # Rename columns for display
    final_corr.columns = [c.replace("BFI_", "") for c in final_corr.columns]
    
    # Plot Heatmap using Matplotlib
    plt.figure(figsize=(12, 7))
    plt.imshow(final_corr, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
    plt.colorbar(label='Pearson Correlation')
    
    # Ticks
    plt.xticks(range(len(final_corr.columns)), final_corr.columns, rotation=45, ha='right')
    plt.yticks(range(len(final_corr.index)), final_corr.index)
    plt.title(f'Gunas vs. Big Five Correlations (N={len(data)})')
    
    # Annotations
    for i in range(len(final_corr.index)):
        for j in range(len(final_corr.columns)):
            val = final_corr.iloc[i, j]
            color = 'white' if abs(val) > 0.5 else 'black'
            plt.text(j, i, f"{val:.2f}", ha='center', va='center', color=color)
            
    plt.tight_layout()
    plt.savefig('phase3_correlation_heatmap.png')
    plt.close()

    # Report Construction
    report = ["# Phase 3: Convergent Validity (Correlations)\n"]
    report.append(f"**Sample**: N={len(data)} | **Method**: Pearson Correlation\n")
    
    report.append("## 1. Correlation Matrix Heatmap")
    report.append("Visualizing the relationships between Vedic Gunas and Western Personality Traits.\n")
    report.append("![Correlation Heatmap](file:///c:/Users/donke/Desktop/IKS_Work/Gunabased%20Survey/student-assessment/analysis/phase3_correlation_heatmap.png)\n")
    
    report.append("## 2. Key Hypothesis Checks")
    
    def check_hyp(g, b, expected_sign):
        try:
            val = final_corr.loc[g, b]
            sign = "+" if val >= 0 else "-"
            # Threshold 0.3 for weak support
            supported = (expected_sign == "+" and val > 0.3) or (expected_sign == "-" and val < -0.3)
            match = "SUPPORTED" if supported else "WEAK/MIXED"
            return f"- **{g} vs {b}**: r = {val:.2f} (Expected: {expected_sign}) -> **{match}**"
        except KeyError:
             return f"- **{g} vs {b}**: Data Missing"

    report.append(check_hyp("Sattva", "Conscientiousness", "+"))
    report.append(check_hyp("Sattva", "Agreeableness", "+"))
    report.append(check_hyp("Rajas", "Extraversion", "+"))
    report.append(check_hyp("Rajas", "Neuroticism", "+"))
    report.append(check_hyp("Tamas", "Conscientiousness", "-"))
    report.append(check_hyp("Tamas", "Neuroticism", "+"))

    report.append("\n## 3. Full Correlation Table")
    
    # Manual Markdown Table Construction
    cols = final_corr.columns.tolist()
    header = "| Guna | " + " | ".join(cols) + " |"
    separator = "| :--- | " + " | ".join([":---"] * len(cols)) + " |"
    
    report.append(header)
    report.append(separator)
    
    for idx, row in final_corr.iterrows():
        vals = [f"{x:.2f}" for x in row]
        line = f"| {idx} | " + " | ".join(vals) + " |"
        report.append(line)

    with open("PHASE3_CORRELATION_REPORT.md", "w") as f:
        f.write("\n".join(report))
        
    print("Phase 3 Analysis Complete. Report saved to PHASE3_CORRELATION_REPORT.md")

if __name__ == "__main__":
    analyze_phase3()
