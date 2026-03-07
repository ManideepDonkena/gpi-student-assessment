import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os

# Refined Exclusion List (Matching Phase 5 Report - 9 items)
EXCLUDE_ITEMS = [
    "BFI35", "BFI41", "BFI44", # Openness
    "R_AV", "R_BX", "R_DP",    # Rajas
    "S_AT", "S_DR",            # Sattva
    "T_AN"                     # Tamas
]

# Copying BFI Mapping from analyze_cronbach.py for consistency
BFI44_MAPPING = {
    f"BFI{i}": {"trait": trait, "reverse": reverse} 
    for i, (trait, reverse) in enumerate([
        ("Extraversion", False), ("Agreeableness", True), ("Conscientiousness", False), ("Neuroticism", False), ("Openness", False),
        ("Extraversion", True), ("Agreeableness", False), ("Conscientiousness", True), ("Neuroticism", True), ("Openness", False),
        ("Extraversion", False), ("Agreeableness", True), ("Conscientiousness", False), ("Neuroticism", False), ("Openness", False),
        ("Extraversion", False), ("Agreeableness", False), ("Conscientiousness", True), ("Neuroticism", False), ("Openness", False),
        ("Extraversion", True), ("Agreeableness", False), ("Conscientiousness", True), ("Neuroticism", True), ("Openness", False),
        ("Extraversion", False), ("Agreeableness", True), ("Conscientiousness", False), ("Neuroticism", False), ("Openness", False),
        ("Extraversion", True), ("Agreeableness", False), ("Conscientiousness", False), ("Neuroticism", True), ("Openness", True),
        ("Extraversion", False), ("Agreeableness", True), ("Conscientiousness", False), ("Neuroticism", False), ("Openness", False),
        ("Openness", True), ("Agreeableness", False), ("Conscientiousness", True), ("Openness", False)
    ], 1)
}

def analyze_clusters():
    # Use the refined N=181 dataset
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "final_dataset_refined.json")
    if not os.path.exists(json_path):
        print("Error: Data file not found.")
        return

    with open(json_path, "r") as f:
        data = json.load(f)

    # 1. Prepare Data
    processed_rows = []
    
    for session in data:
        guna = session.get('gunaResponses', {})
        bfi = session.get('bigFiveResponses', {})
        
        # Guna Scores (Refined)
        s_vals = [v for k,v in guna.items() if k.startswith('S_') and k not in EXCLUDE_ITEMS]
        r_vals = [v for k,v in guna.items() if k.startswith('R_') and k not in EXCLUDE_ITEMS]
        t_vals = [v for k,v in guna.items() if k.startswith('T_') and k not in EXCLUDE_ITEMS]
        
        # BFI Scores (Refined)
        bfi_scores = {t: [] for t in ["Extraversion", "Agreeableness", "Conscientiousness", "Neuroticism", "Openness"]}
        
        for q_id, val in bfi.items():
            if q_id in EXCLUDE_ITEMS: continue
            if q_id not in BFI44_MAPPING: continue
            
            meta = BFI44_MAPPING[q_id]
            score = (6 - val) if meta['reverse'] else val
            bfi_scores[meta['trait']].append(score)
            
        row = {
            "Sattva": np.mean(s_vals) if s_vals else 0,
            "Rajas": np.mean(r_vals) if r_vals else 0,
            "Tamas": np.mean(t_vals) if t_vals else 0,
            "Extraversion": np.mean(bfi_scores["Extraversion"]) if bfi_scores["Extraversion"] else 0,
            "Agreeableness": np.mean(bfi_scores["Agreeableness"]) if bfi_scores["Agreeableness"] else 0,
            "Conscientiousness": np.mean(bfi_scores["Conscientiousness"]) if bfi_scores["Conscientiousness"] else 0,
            "Neuroticism": np.mean(bfi_scores["Neuroticism"]) if bfi_scores["Neuroticism"] else 0,
            "Openness": np.mean(bfi_scores["Openness"]) if bfi_scores["Openness"] else 0,
        }
        processed_rows.append(row)

    df = pd.DataFrame(processed_rows)
    
    # 2. Standardization (Z-Score)
    # User Request: Scale based on MEAN (Relative to population)
    # This is "StandardScaler" (Mean=0, Std=1)
    
    scaler = StandardScaler()
    feature_cols = df.columns # All numeric cols
    X_scaled = scaler.fit_transform(df[feature_cols])
    
    # Create Z-score DataFrame
    df_z = pd.DataFrame(X_scaled, columns=feature_cols)
    
    # 3. Clustering (K=3)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    df['Cluster'] = clusters
    df_z['Cluster'] = clusters
    
    # 4. Profile Analysis
    # Get Z-score centers (for interpretation relative to average)
    cluster_centers_z = df_z.groupby('Cluster').mean()
    
    # Get Raw centers (for "Real world" values)
    raw_means = df.groupby('Cluster').mean()
    
    # Generate Report
    report = ["# Student Archetype Analysis (Cluster Analysis) 👥\n"]
    report.append(f"**Sample**: N={len(df)} | **Method**: K-Means on Z-Scores (Standardized)\n")
    report.append("**Correction**: Data standardized (Mean=0, SD=1). Group characteristics are defined *relative to the campus average*.\n")
    
    report.append("## 1. The 3 Student Archetypes")
    report.append("We identified 3 distinct groups of students.\n")
    
    for i in range(3):
        profile_raw = raw_means.iloc[i]
        profile_z = cluster_centers_z.iloc[i]
        size = len(df[df['Cluster'] == i])
        perc = (size / len(df)) * 100
        
        # Heuristics based on Z-Scores (easier to define "High" vs "Low")
        s_z, r_z, t_z = profile_z['Sattva'], profile_z['Rajas'], profile_z['Tamas']
        
        label = f"Cluster {i+1}"
        desc = ""
        
        if s_z > 0.5 and t_z < -0.5:
            label = "The Sattvic Ideal (Balanced/Yogi)"
            desc = "Above average Purity, Below average Distress."
        elif t_z > 0.5 and r_z > 0.0:
            label = "The Distressed/Anxious (High Rajas/Tamas)"
            desc = "Significantly higher distress/inertia than peers."
        elif r_z > 0.5 and s_z > 0.0:
            label = "The High-Flyer (Type-A)"
            desc = "High Ambition, Average Distress."
        else:
             # Fallback
            if max(s_z, r_z, t_z) == s_z: label = "Sattva-Dominant"
            elif max(s_z, r_z, t_z) == r_z: label = "Rajas-Dominant"
            else: label = "Tamas-Dominant"

        report.append(f"### {label} ({size} students, {perc:.1f}%)")
        if desc: report.append(f"*{desc}*")
        
        report.append("| Trait | Raw Score | T-Score (Avg=50) | Status |")
        report.append("|---|---|---|---|")
        
        for col in df.columns[:-1]:
            val_raw = profile_raw[col]
            val_z = profile_z[col]
            
            # Convert Z to T-Score (Mean 50, SD 10) for easier reading
            t_score = 50 + (val_z * 10)
            
            indicator = "⬆️ High" if val_z > 0.5 else "⬇️ Low" if val_z < -0.5 else "Avg"
            scale_max = 7 if col in ["Sattva", "Rajas", "Tamas"] else 5
            
            report.append(f"| {col} | {val_raw:.2f}/{scale_max} | **{t_score:.0f}** | {indicator} |")
        report.append("\n")

    report.append("\n## 2. Visualizations")
    report.append("### 3D Cluster Visualization (Z-Space)")
    report.append("![3D Clusters](file:///c:/Users/donke/Desktop/IKS_Work/Gunabased%20Survey/student-assessment/analysis/clusters_3d.png)\n")
    report.append("### Archetype Radar Chart (T-Scores)")
    report.append("![radar](file:///c:/Users/donke/Desktop/IKS_Work/Gunabased%20Survey/student-assessment/analysis/clusters_radar.png)\n")
    report.append("*Note: Radar Chart uses T-Scores (50 is Average). Spikes show deviation from the norm.*")

    with open("STUDENT_CLUSTERS_REPORT.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print("Cluster Analysis Report saved.")
    
    # --- 5. VISUALIZATIONS ---
    print("Generating plots...")
    
    # A. 3D Scatter Plot (Using Z-Scores)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    colors = ['green', 'red', 'blue']
    
    for i in range(3):
        subset = df_z[df_z['Cluster'] == i]
        ax.scatter(subset['Sattva'], subset['Rajas'], subset['Tamas'], c=colors[i], label=f'Cluster {i}', s=50, alpha=0.6)
        
    ax.set_xlabel('Sattva (Z)')
    ax.set_ylabel('Rajas (Z)')
    ax.set_zlabel('Tamas (Z)')
    ax.set_title('Student Clusters in Guna Space (Standardized)')
    ax.legend()
    plt.savefig('clusters_3d.png')
    plt.close()
    
    # B. Radar Chart (Comparison using T-Scores)
    # T-Score = 50 + 10*Z
    # This transforms Z (-2 to +2) to T (30 to 70), ensuring positive values for Radar
    
    feature_names = df.columns[:-1]
    clusters_t = cluster_centers_z.copy()
    for col in feature_names:
        clusters_t[col] = 50 + (clusters_t[col] * 10)
        
    # Angles
    num_vars = len(feature_names)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1] 
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    # Reference Circle (Average = 50)
    ax.plot(angles, [50]*(num_vars+1), color='grey', linestyle='--', linewidth=1, label='Campus Avg (50)')
    
    for i in range(3):
        values = clusters_t.iloc[i].tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=2, label=f'Cluster {i}')
        ax.fill(angles, values, alpha=0.1)
        
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(feature_names)
    ax.set_ylim(30, 70) # T-Scores usually fall in this range
    ax.set_title('Personality Deviation from Average (T-Scores)')
    ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    
    plt.savefig('clusters_radar.png')
    plt.close()
    
    print("Plots saved: clusters_3d.png, clusters_radar.png")

if __name__ == "__main__":
    analyze_clusters()
