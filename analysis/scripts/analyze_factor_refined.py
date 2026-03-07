import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import FactorAnalysis, PCA
from sklearn.preprocessing import StandardScaler
import os

# Items identified for removal in Reliability Analysis
REMOVAL_LIST = [
    "S_J", "S_BF",          # Sattva Weak
    "R_AV", "R_BX", "R_AL", "R_EX", # Rajas Weak/Negative
    "T_DH"                  # Tamas Weak
]

def analyze_factor_refined():
    json_path = "bfi44_cleaned.json"
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    with open(json_path, "r") as f:
        data = json.load(f)

    # Flatten Guna Responses
    flat_data = []
    for s in data:
        row = s.get('gunaResponses', {})
        flat_data.append(row)
        
    df = pd.DataFrame(flat_data)
    
    # 1. Original Set
    guna_cols_orig = [c for c in df.columns if c.startswith(('S_', 'R_', 'T_'))]
    df_orig = df[guna_cols_orig].apply(pd.to_numeric, errors='coerce').fillna(3)
    
    # 2. Refined Set
    guna_cols_ref = [c for c in guna_cols_orig if c not in REMOVAL_LIST]
    df_ref = df[guna_cols_ref].apply(pd.to_numeric, errors='coerce').fillna(3)
    
    print(f"Original Items: {len(guna_cols_orig)}")
    print(f"Refined Items: {len(guna_cols_ref)}")
    
    # Analyze Both
    results = {}
    
    for name, dataset, cols in [("Original", df_orig, guna_cols_orig), ("Refined", df_ref, guna_cols_ref)]:
        print(f"\nRunning Analysis for: {name}")
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(dataset)
        
        # PCA for Variance
        pca = PCA()
        pca.fit(X_scaled)
        eigenvalues = pca.explained_variance_
        var_explained = pca.explained_variance_ratio_ * 100
        cum_var = np.cumsum(var_explained)
        
        # Determine N factors (Eigenvalue > 1)
        n_factors = sum(e > 1 for e in eigenvalues)
        print(f"  > Retaining {n_factors} factors (Eigenvalue > 1)")
        
        # Factor Analysis (Dynamic N)
        fa = FactorAnalysis(n_components=n_factors, rotation='varimax')
        fa.fit(X_scaled)
        loadings = fa.components_.T
        
        # Top Loading Items per Factor
        factor_map = []
        for i in range(n_factors):
            # Sort loadings
            loading_col = loadings[:, i]
            # Get indices of top 5 absolute loadings
            idx_sorted = np.argsort(np.abs(loading_col))[::-1][:5]
            
            top_items = []
            for idx in idx_sorted:
                item_name = cols[idx]
                val = loading_col[idx]
                tag = item_name.split('_')[0] # S, R, T
                top_items.append(f"{item_name}({tag}:{val:.2f})")
            
            # Simple heuristic for Factor Identity
            # Count tags in top 10 loadings to guess identity
            idx_top10 = np.argsort(np.abs(loading_col))[::-1][:10]
            tags = [cols[x].split('_')[0] for x in idx_top10]
            identity = max(set(tags), key=tags.count)
            
            factor_map.append({
                "factor_num": i+1,
                "identity": identity,
                "top_items": ", ".join(top_items),
                "eigenvalue": eigenvalues[i],
                "var_explained": var_explained[i]
            })
            
        results[name] = {
            "eigenvalues": eigenvalues,
            "cum_var": cum_var[n_factors-1], 
            "factors": factor_map,
            "n_retained": n_factors
        }

    # Generate Comparative Report
    report = ["# Refined Factor Analysis Report (Kaiser Criterion > 1)\n"]
    report.append(f"**Sample**: N={len(df)} | **Impact of Item Removal**\n")
    
    report.append("## 1. Variance Explained")
    
    r_orig = results['Original']
    r_ref = results['Refined']
    
    report.append(f"| Metric | Original (80 items) | Refined ({len(guna_cols_ref)} items) |")
    report.append("| :--- | :--- | :--- |")
    report.append(f"| **Factors Retained (Eig > 1)** | {r_orig['n_retained']} | **{r_ref['n_retained']}** |")
    report.append(f"| **Total Variance Explained** | {r_orig['cum_var']:.2f}% | **{r_ref['cum_var']:.2f}%** |")
    
    report.append("\n## 2. Refined Factor Structure (Detailed)")
    report.append("Below are the significant factors found in the **Refined** dataset:\n")
    
    for f in r_ref['factors']:
        report.append(f"### Factor {f['factor_num']}: {f['identity']} Core (Eig={f['eigenvalue']:.2f}, Var={f['var_explained']:.1f}%)")
        report.append(f"- **Top Loadings**: {f['top_items']}")
        report.append("\n")

    with open("REFINED_FACTOR_ANALYSIS_REPORT.md", "w") as f:
        f.write("\n".join(report))
        
    print("Analysis Complete. Saved to REFINED_FACTOR_ANALYSIS_REPORT.md")

if __name__ == "__main__":
    analyze_factor_refined()
