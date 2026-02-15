import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA, FactorAnalysis
from sklearn.preprocessing import StandardScaler
import os

def analyze_phase2():
    # Load cleaned BFI-44 data
    json_path = "bfi44_cleaned.json"
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found. Run clean_and_analyze.py first.")
        return

    with open(json_path, "r") as f:
        data = json.load(f)

    # Flatten Guna Responses
    flat_data = []
    for s in data:
        row = s.get('gunaResponses', {})
        flat_data.append(row)
        
    df = pd.DataFrame(flat_data)
    
    # Filter only clean S_, R_, T_ columns
    guna_cols = [c for c in df.columns if c.startswith(('S_', 'R_', 'T_'))]
    df_guna = df[guna_cols].fillna(3) # Neutral fallback
    
    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_guna)
    
    # --- 1. PCA for Scree Plot (Eigenvalues) ---
    pca = PCA()
    pca.fit(X_scaled)
    eigenvalues = pca.explained_variance_
    
    # Plot Scree
    plt.figure(figsize=(8, 5))
    plt.plot(range(1, 11), eigenvalues[:10], marker='o', linestyle='-', color='b')
    plt.axhline(y=1, color='r', linestyle='--', label='Eigenvalue = 1')
    plt.title('Scree Plot (First 10 Factors)')
    plt.xlabel('Factor Number')
    plt.ylabel('Eigenvalue')
    plt.grid(True)
    plt.legend()
    plt.savefig('phase2_scree_plot.png')
    plt.close()

    # --- 2. Variance Explained ---
    explained_var = pca.explained_variance_ratio_ * 100
    cum_var = np.cumsum(explained_var)
    
    # Report Construction
    report = ["# Phase 2: Factor Analysis Report\n"]
    report.append(f"**Method**: PCA/EFA | **Items**: {len(guna_cols)} | **Sample**: N={len(data)}\n")
    
    report.append("## 1. Eigenvalue Analysis (The 'Elbow')")
    report.append("The Scree Plot visually demonstrates how many underlying factors (constructs) exist in the data.\n")
    report.append("![Scree Plot](file:///c:/Users/donke/Desktop/IKS_Work/Gunabased%20Survey/student-assessment/analysis/phase2_scree_plot.png)\n")
    
    report.append("| Factor | Eigenvalue | Variance Explained (%) | Cumulative (%) |")
    report.append("| :--- | :--- | :--- | :--- |")
    
    for i in range(5): # Top 5
        report.append(f"| {i+1} | {eigenvalues[i]:.3f} | {explained_var[i]:.2f}% | {cum_var[i]:.2f}% |")
        
    report.append("\n## 2. Factor Interpretability")
    report.append("Checking if the top 3 factors map roughly to Sattva, Rajas, and Tamas.\n")
    
    # --- 3. Simple Factor Loading Check (Top 3) ---
    fa = FactorAnalysis(n_components=3, rotation='varimax')
    try:
        fa.fit(X_scaled)
        loadings = fa.components_.T
        
        # for each factor, find top 3 positive loaded items
        for i in range(3):
            report.append(f"\n### Factor {i+1} Top Loadings:")
            report.append("| Item | Loading | Intended Guna |")
            report.append("| :--- | :--- | :--- |")
            
            # Get indices of sorted loadings (descending)
            loading_col = loadings[:, i]
            top_indices = np.argsort(loading_col)[::-1][:5]
            
            for idx in top_indices:
                item_id = guna_cols[idx]
                val = loading_col[idx]
                intended = "Sattva" if item_id.startswith("S_") else "Rajas" if item_id.startswith("R_") else "Tamas"
                report.append(f"| {item_id} | {val:.3f} | {intended} |")
                
    except Exception as e:
        report.append(f"\n*Note: Advanced factor rotation skipped due to dependency limitations ({str(e)}).*")

    
    with open("PHASE2_FACTOR_ANALYSIS_REPORT.md", "w") as f:
        f.write("\n".join(report))
        
    print("Phase 2 Analysis Complete. Report saved to PHASE2_FACTOR_ANALYSIS_REPORT.md")

if __name__ == "__main__":
    analyze_phase2()
