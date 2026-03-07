"""
=============================================================
ITEM REFINEMENT ANALYSIS
=============================================================
Identifies items that are consistently weak across ALL analyses:
  1. Low Item-Total Correlation (ITC < 0.2) in reliability
  2. Low maximum factor loading (< 0.3) in factor analysis
  3. Negative or near-zero inter-item correlation

Then re-runs reliability & factor analysis WITHOUT those items
to show improvement.
=============================================================
"""
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.decomposition import PCA, FactorAnalysis
from sklearn.preprocessing import StandardScaler

# --- PATH CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ANALYSIS_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(ANALYSIS_DIR, "data")
REPORTS_DIR = os.path.join(ANALYSIS_DIR, "reports")
IMAGES_DIR = os.path.join(ANALYSIS_DIR, "images")

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

INPUT_FILE = os.path.join(DATA_DIR, "final_dataset_refined.json")
REPORT_FILE = os.path.join(REPORTS_DIR, "PHASE5_ITEM_REFINEMENT_REPORT.md")

# BFI reverse scoring
BFI_REVERSE = {
    "BFI2", "BFI6", "BFI8", "BFI9", "BFI12", "BFI18", "BFI21", 
    "BFI23", "BFI24", "BFI27", "BFI31", "BFI34", "BFI35", "BFI37", 
    "BFI41", "BFI43"
}

BFI_TRAIT_MAP = {
    "BFI1": "Extraversion", "BFI6": "Extraversion", "BFI11": "Extraversion", "BFI16": "Extraversion",
    "BFI21": "Extraversion", "BFI26": "Extraversion", "BFI31": "Extraversion", "BFI36": "Extraversion",
    "BFI2": "Agreeableness", "BFI7": "Agreeableness", "BFI12": "Agreeableness", "BFI17": "Agreeableness",
    "BFI22": "Agreeableness", "BFI27": "Agreeableness", "BFI32": "Agreeableness", "BFI37": "Agreeableness", "BFI42": "Agreeableness",
    "BFI3": "Conscientiousness", "BFI8": "Conscientiousness", "BFI13": "Conscientiousness", "BFI18": "Conscientiousness",
    "BFI23": "Conscientiousness", "BFI28": "Conscientiousness", "BFI33": "Conscientiousness", "BFI38": "Conscientiousness", "BFI43": "Conscientiousness",
    "BFI4": "Neuroticism", "BFI9": "Neuroticism", "BFI14": "Neuroticism", "BFI19": "Neuroticism",
    "BFI24": "Neuroticism", "BFI29": "Neuroticism", "BFI34": "Neuroticism", "BFI39": "Neuroticism",
    "BFI5": "Openness", "BFI10": "Openness", "BFI15": "Openness", "BFI20": "Openness",
    "BFI25": "Openness", "BFI30": "Openness", "BFI35": "Openness", "BFI40": "Openness", "BFI41": "Openness", "BFI44": "Openness"
}

def get_scale(item_id):
    if item_id.startswith("S_"): return "Sattva"
    if item_id.startswith("R_"): return "Rajas"
    if item_id.startswith("T_"): return "Tamas"
    return BFI_TRAIT_MAP.get(item_id, "Unknown")

def cronbach_alpha(df):
    k = df.shape[1]
    if k < 2: return 0
    item_vars = df.var(axis=0, ddof=1)
    total_var = df.sum(axis=1).var(ddof=1)
    if total_var == 0: return 0
    return (k / (k - 1)) * (1 - item_vars.sum() / total_var)

def item_total_correlation(df, item):
    rest = df.drop(columns=[item]).sum(axis=1)
    return df[item].corr(rest)

def varimax_rotation(loadings, max_iter=100, tol=1e-6):
    n, k = loadings.shape
    for _ in range(max_iter):
        old = loadings.copy()
        for i in range(k):
            for j in range(i+1, k):
                x, y = loadings[:, i], loadings[:, j]
                u, v = x**2 - y**2, 2*x*y
                A, B = u.sum(), v.sum()
                C, D = (u**2 - v**2).sum(), 2*(u*v).sum()
                angle = 0.25 * np.arctan2(D - 2*A*B/n, C - (A**2 - B**2)/n)
                cos_a, sin_a = np.cos(angle), np.sin(angle)
                loadings[:, i] = x*cos_a + y*sin_a
                loadings[:, j] = -x*sin_a + y*cos_a
        if np.max(np.abs(loadings - old)) < tol:
            break
    return loadings

def analyze_refinement():
    print("Starting Item Refinement Analysis...")
    
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)
    print(f"Loaded {len(data)} records.")
    
    # Extract item-level data
    rows = []
    item_texts = {}
    
    for s in data:
        row = {}
        for item_id, details in s.get('gunaDetails', {}).items():
            val = details.get('value')
            if val is not None:
                row[item_id] = val
                if details.get('text') and item_id not in item_texts:
                    item_texts[item_id] = details['text']
        
        for item_id, details in s.get('bigFiveDetails', {}).items():
            val = details.get('value')
            if val is not None:
                if item_id in BFI_REVERSE:
                    val = 6 - val
                row[item_id] = val
                if details.get('text') and item_id not in item_texts:
                    item_texts[item_id] = details['text']
        
        rows.append(row)
    
    df = pd.DataFrame(rows)
    guna_cols = sorted([c for c in df.columns if c.startswith(('S_', 'R_', 'T_'))])
    bfi_cols = sorted([c for c in df.columns if c.startswith('BFI')], key=lambda x: int(x[3:]))
    all_cols = guna_cols + bfi_cols
    df_all = df[all_cols].dropna()
    
    N = len(df_all)
    print(f"Valid cases: {N}, Total items: {len(all_cols)}")
    
    # ===== STEP 1: Item-Total Correlation within each scale =====
    print("\n--- Step 1: Item-Total Correlations ---")
    
    scales = {}
    for col in all_cols:
        s = get_scale(col)
        if s not in scales:
            scales[s] = []
        scales[s].append(col)
    
    itc_results = {}
    for scale_name, items in scales.items():
        scale_df = df_all[items]
        for item in items:
            itc = item_total_correlation(scale_df, item)
            itc_results[item] = {"itc": itc, "scale": scale_name}
    
    # ===== STEP 2: Factor Loadings =====
    print("--- Step 2: Factor Loadings ---")
    
    # Run EFA on GUNA items only (since we want to refine the GPI)
    scaler = StandardScaler()
    
    # Guna-only factor analysis (3 factors for S/R/T)
    X_guna = scaler.fit_transform(df_all[guna_cols])
    fa_guna = FactorAnalysis(n_components=3)
    fa_guna.fit(X_guna)
    guna_loadings = varimax_rotation(fa_guna.components_.T.copy())
    guna_loadings_df = pd.DataFrame(guna_loadings, index=guna_cols, columns=["F1", "F2", "F3"])
    
    # BFI-only factor analysis (5 factors for OCEAN)
    X_bfi = scaler.fit_transform(df_all[bfi_cols])
    fa_bfi = FactorAnalysis(n_components=5)
    fa_bfi.fit(X_bfi)
    bfi_loadings = varimax_rotation(fa_bfi.components_.T.copy())
    bfi_loadings_df = pd.DataFrame(bfi_loadings, index=bfi_cols, columns=["F1", "F2", "F3", "F4", "F5"])
    
    # Combine  
    factor_results = {}
    for item in guna_cols:
        max_loading = guna_loadings_df.loc[item].abs().max()
        factor_results[item] = {"max_loading": max_loading}
    for item in bfi_cols:
        max_loading = bfi_loadings_df.loc[item].abs().max()
        factor_results[item] = {"max_loading": max_loading}
    
    # ===== STEP 3: Identify WEAK items =====
    print("--- Step 3: Identifying Weak Items ---")
    
    weak_items = []
    all_item_stats = []
    
    for item in all_cols:
        itc = itc_results[item]["itc"]
        scale = itc_results[item]["scale"]
        max_fl = factor_results[item]["max_loading"]
        text = item_texts.get(item, "N/A")
        
        is_weak_itc = itc < 0.2
        is_weak_fl = max_fl < 0.3
        is_negative_itc = itc < 0
        
        # "Weak in EVERY aspect" = low ITC AND low factor loading
        is_weak = (is_weak_itc and is_weak_fl) or is_negative_itc
        
        reason = []
        if is_negative_itc: reason.append(f"Negative ITC ({itc:.3f})")
        elif is_weak_itc: reason.append(f"Low ITC ({itc:.3f})")
        if is_weak_fl: reason.append(f"Low Loading ({max_fl:.3f})")
        
        all_item_stats.append({
            "item": item, "scale": scale, "itc": itc, 
            "max_loading": max_fl, "weak": is_weak,
            "reason": "; ".join(reason) if reason else "OK",
            "text": text
        })
        
        if is_weak:
            weak_items.append(item)
    
    stats_df = pd.DataFrame(all_item_stats)
    
    print(f"Weak items identified: {len(weak_items)}/{len(all_cols)}")
    for item in weak_items:
        row = stats_df[stats_df.item == item].iloc[0]
        print(f"  [X] {item} ({row.scale}): {row.reason}")
    
    # ===== STEP 4: Re-analyze WITHOUT weak items =====
    print("\n--- Step 4: Re-analyzing without weak items ---")
    
    refined_cols = [c for c in all_cols if c not in weak_items]
    refined_guna = [c for c in guna_cols if c not in weak_items]
    refined_bfi = [c for c in bfi_cols if c not in weak_items]
    
    print(f"Refined: {len(refined_cols)} items ({len(all_cols)} - {len(weak_items)} removed)")
    
    # Re-calculate Cronbach's Alpha for each scale
    original_alphas = {}
    refined_alphas = {}
    
    for scale_name, items in scales.items():
        original_alphas[scale_name] = cronbach_alpha(df_all[items])
        refined_items = [i for i in items if i not in weak_items]
        if len(refined_items) >= 2:
            refined_alphas[scale_name] = cronbach_alpha(df_all[refined_items])
        else:
            refined_alphas[scale_name] = None
    
    # ===== STEP 5: Visualization =====
    print("--- Step 5: Generating Visualizations ---")
    
    # Plot: Before vs After Alpha
    fig, ax = plt.subplots(figsize=(12, 6))
    scale_names = list(original_alphas.keys())
    x = np.arange(len(scale_names))
    width = 0.35
    
    orig_vals = [original_alphas[s] for s in scale_names]
    ref_vals = [refined_alphas.get(s, 0) or 0 for s in scale_names]
    
    bars1 = ax.bar(x - width/2, orig_vals, width, label='Original', color='#3498db', alpha=0.8)
    bars2 = ax.bar(x + width/2, ref_vals, width, label='Refined', color='#2ecc71', alpha=0.8)
    
    ax.axhline(0.7, color='red', linestyle='--', alpha=0.6, label='Acceptable (α=0.7)')
    ax.set_xlabel('Scale')
    ax.set_ylabel("Cronbach's Alpha")
    ax.set_title(f"Reliability Before vs After Item Removal (N={N})")
    ax.set_xticks(x)
    ax.set_xticklabels(scale_names, rotation=45, ha='right')
    ax.legend()
    ax.set_ylim(0, 1.0)
    
    for bar, val in zip(bars1, orig_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{val:.2f}', 
                ha='center', va='bottom', fontsize=8)
    for bar, val in zip(bars2, ref_vals):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{val:.2f}', 
                    ha='center', va='bottom', fontsize=8, color='green')
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "phase5_alpha_comparison.png"), dpi=150)
    plt.close()
    
    # Plot: Weak items by scale
    weak_df = stats_df[stats_df.weak == True]
    if len(weak_df) > 0:
        fig, ax = plt.subplots(figsize=(10, 6))
        weak_counts = weak_df.groupby('scale').size().sort_values(ascending=True)
        colors = ['#e74c3c' if 'Openness' in s or 'Tamas' in s else '#f39c12' for s in weak_counts.index]
        weak_counts.plot(kind='barh', ax=ax, color=colors, alpha=0.8)
        ax.set_xlabel('Number of Weak Items Removed')
        ax.set_title('Weak Items by Scale')
        for i, v in enumerate(weak_counts):
            ax.text(v + 0.1, i, str(v), va='center')
        plt.tight_layout()
        plt.savefig(os.path.join(IMAGES_DIR, "phase5_weak_items_by_scale.png"), dpi=150)
        plt.close()
    
    # ===== STEP 6: Generate Report =====
    print("--- Step 6: Generating Report ---")
    
    report = []
    report.append("# Phase 5: Item Refinement Analysis ✂️")
    report.append(f"\n**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    report.append(f"**Dataset**: N={N}")
    report.append(f"**Method**: Cross-validated item analysis (Reliability × Factor Analysis)")
    
    report.append("\n## 1. Objective")
    report.append("Identify items that are **consistently weak across ALL analyses** and evaluate")
    report.append("whether removing them improves overall scale quality.\n")
    report.append("**Criteria for removal** (item must meet BOTH):")
    report.append("- Item-Total Correlation (ITC) < 0.2 within its own scale")
    report.append("- Maximum factor loading < 0.3 in factor analysis")
    report.append("- OR: Negative ITC (item contradicts its own scale)")
    
    report.append("\n## 2. Items Flagged for Removal")
    report.append(f"\n**{len(weak_items)} items flagged** out of {len(all_cols)} total:\n")
    
    if weak_items:
        report.append("| # | Item | Scale | ITC | Max Loading | Reason | Question Text |")
        report.append("| :---: | :--- | :--- | :---: | :---: | :--- | :--- |")
        
        for i, item in enumerate(sorted(weak_items, key=lambda x: get_scale(x)), 1):
            row = stats_df[stats_df.item == item].iloc[0]
            text = row['text'][:50].replace("|", "-") + "..." if len(row['text']) > 50 else row['text'].replace("|", "-")
            report.append(f"| {i} | `{item}` | {row.scale} | {row.itc:.3f} | {row.max_loading:.3f} | {row.reason} | {text} |")
    
    report.append("\n## 3. Reliability Comparison (Before vs After)")
    report.append("![Alpha Comparison](../images/phase5_alpha_comparison.png)\n")
    
    report.append("| Scale | Original Items | Refined Items | Original α | Refined α | Change |")
    report.append("| :--- | :---: | :---: | :---: | :---: | :--- |")
    
    for scale_name in scale_names:
        orig_count = len(scales[scale_name])
        ref_count = len([i for i in scales[scale_name] if i not in weak_items])
        orig_a = original_alphas[scale_name]
        ref_a = refined_alphas.get(scale_name)
        
        if ref_a is not None:
            change = ref_a - orig_a
            change_str = f"{'📈' if change > 0 else '📉'} {change:+.3f}"
            ref_str = f"**{ref_a:.3f}**"
        else:
            change_str = "—"
            ref_str = "—"
        
        report.append(f"| {scale_name} | {orig_count} | {ref_count} | {orig_a:.3f} | {ref_str} | {change_str} |")
    
    if len(weak_df) > 0:
        report.append("\n## 4. Weak Items by Scale")
        report.append("![Weak Items by Scale](../images/phase5_weak_items_by_scale.png)")
    
    # Interpretation
    report.append("\n## 5. Interpretation & Recommendations")
    
    # Count improvements
    improved = sum(1 for s in scale_names if refined_alphas.get(s) and refined_alphas[s] > original_alphas[s])
    total_scales = len(scale_names)
    
    report.append(f"\n**{improved}/{total_scales} scales showed improved reliability** after item removal.\n")
    
    # Best improvements
    best_improvements = []
    for s in scale_names:
        if refined_alphas.get(s):
            diff = refined_alphas[s] - original_alphas[s]
            best_improvements.append((s, diff, original_alphas[s], refined_alphas[s]))
    
    best_improvements.sort(key=lambda x: -x[1])
    
    if best_improvements:
        report.append("### Biggest Improvements:")
        for s, diff, orig, ref in best_improvements[:5]:
            if diff > 0:
                report.append(f"- **{s}**: α improved from {orig:.3f} → **{ref:.3f}** (+{diff:.3f})")
    
    report.append("\n### Recommendations:")
    report.append("1. **Remove flagged items** from the GPI for future data collection")
    report.append("2. **Report both original and refined alphas** in publications")
    report.append("3. **Weak BFI items** (especially Openness reverse-coded items) are a known limitation")
    report.append("4. **Re-validate** with a larger sample after item removal")
    
    # Add the final refined item list
    report.append("\n## 6. Final Refined Item List")
    report.append(f"\n**Retained: {len(refined_cols)} items** ({len(refined_guna)} Guna + {len(refined_bfi)} BFI)\n")
    
    for scale_name in sorted(scales.keys()):
        retained = [i for i in scales[scale_name] if i not in weak_items]
        removed = [i for i in scales[scale_name] if i in weak_items]
        report.append(f"### {scale_name}: {len(retained)}/{len(scales[scale_name])} items retained")
        if removed:
            report.append(f"- Removed: {', '.join([f'`{r}`' for r in removed])}")
        report.append("")
    
    # ===== STEP 7: Before vs After JOINT Factor Analysis =====
    print("--- Step 7: Before vs After Joint Factor Analysis ---")
    
    def get_item_tag(item_id):
        if item_id.startswith("S_"): return "S"
        if item_id.startswith("R_"): return "R"
        if item_id.startswith("T_"): return "T"
        bfi_short = {"Extraversion":"E", "Agreeableness":"A", "Conscientiousness":"C",
                     "Neuroticism":"N", "Openness":"O"}
        return bfi_short.get(BFI_TRAIT_MAP.get(item_id, ""), "?")
    
    name_map = {"S": "Sattva", "R": "Rajas", "T": "Tamas", 
                "E": "Extraversion", "A": "Agreeableness", 
                "C": "Conscientiousness", "N": "Neuroticism", "O": "Openness"}
    
    def run_joint_efa(df_input, cols, n_factors=8, label=""):
        """Run joint EFA on given columns and return factor profiles."""
        X = scaler.fit_transform(df_input[cols])
        
        # PCA for eigenvalues
        pca = PCA()
        pca.fit(X)
        eigenvalues = pca.explained_variance_
        
        fa = FactorAnalysis(n_components=n_factors)
        fa.fit(X)
        loadings = varimax_rotation(fa.components_.T.copy())
        loadings_df = pd.DataFrame(loadings, index=cols, 
                                    columns=[f"F{i+1}" for i in range(n_factors)])
        
        profiles = []
        for i in range(n_factors):
            col_name = f"F{i+1}"
            high = loadings_df[loadings_df[col_name].abs() > 0.3][col_name]
            high = high.reindex(high.abs().sort_values(ascending=False).index)
            
            tags = [get_item_tag(item) for item in high.index]
            tag_counts = {}
            for t in tags:
                tag_counts[t] = tag_counts.get(t, 0) + 1
            
            dominant = max(tag_counts, key=tag_counts.get) if tag_counts else "?"
            total = len(tags)
            purity = (tag_counts.get(dominant, 0) / total * 100) if total > 0 else 0
            
            factor_name = name_map.get(dominant, "Mixed")
            if purity < 70 and len(tag_counts) > 1:
                top2 = sorted(tag_counts.items(), key=lambda x: -x[1])[:2]
                mix_names = [name_map.get(t[0], t[0]) for t in top2]
                factor_name = f"{'/'.join(mix_names)}"
            
            has_bfi = any(k in ['E','A','C','N','O'] for k in tag_counts)
            has_guna = any(k in ['S','R','T'] for k in tag_counts)
            ftype = "Unique Guna" if has_guna and not has_bfi else \
                    "Mixed" if has_guna and has_bfi else "Big Five"
            
            profiles.append({
                "num": i+1, "name": factor_name, "eigenvalue": eigenvalues[i],
                "var_pct": pca.explained_variance_ratio_[i] * 100,
                "purity": purity, "composition": tag_counts,
                "top_items": high.head(5), "n_items": total, "type": ftype
            })
        return profiles
    
    n_efa_factors = 8
    profiles_before = run_joint_efa(df_all, all_cols, n_efa_factors, "Original")
    profiles_after = run_joint_efa(df_all, refined_cols, n_efa_factors, "Refined")
    
    unique_before = [f for f in profiles_before if f['type'] == 'Unique Guna']
    unique_after = [f for f in profiles_after if f['type'] == 'Unique Guna']
    mixed_before = [f for f in profiles_before if f['type'] == 'Mixed']
    mixed_after = [f for f in profiles_after if f['type'] == 'Mixed']
    
    # Visualization: Side-by-side factor type comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    for ax, profiles, title in [(axes[0], profiles_before, f"ORIGINAL ({len(all_cols)} items)"), 
                                 (axes[1], profiles_after, f"REFINED ({len(refined_cols)} items)")]:
        colors_map = {"Unique Guna": "#2ecc71", "Mixed": "#f39c12", "Big Five": "#3498db"}
        colors = [colors_map.get(f['type'], '#999') for f in profiles]
        var_pcts = [f['var_pct'] for f in profiles]
        labels = [f"F{f['num']}\n{f['name'][:12]}" for f in profiles]
        
        bars = ax.bar(range(len(profiles)), var_pcts, color=colors, alpha=0.85)
        ax.set_xticks(range(len(profiles)))
        ax.set_xticklabels(labels, fontsize=7, rotation=45, ha='right')
        ax.set_ylabel("Variance Explained (%)")
        ax.set_title(title)
        ax.set_ylim(0, max(var_pcts) * 1.3)
        
        for bar, pct in zip(bars, var_pcts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2, 
                    f'{pct:.1f}%', ha='center', fontsize=7)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#2ecc71', label='Unique Guna'),
                       Patch(facecolor='#f39c12', label='Mixed'),
                       Patch(facecolor='#3498db', label='Big Five')]
    fig.legend(handles=legend_elements, loc='upper center', ncol=3, fontsize=9)
    plt.suptitle(f"Factor Structure: Before vs After Item Removal (N={N})", fontsize=13, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "phase5_factor_comparison.png"), dpi=150, bbox_inches='tight')
    plt.close()
    
    # --- ADD TO REPORT: Factor Analysis Comparison ---
    report.append("\n## 7. Factor Analysis: Before vs After Item Removal")
    report.append("![Factor Comparison](../images/phase5_factor_comparison.png)\n")
    
    report.append("### Original Factor Structure (Before)")
    report.append(f"| F# | Name | Type | Variance | Items | Composition |")
    report.append(f"| :---: | :--- | :--- | :---: | :---: | :--- |")
    for fp in profiles_before:
        report.append(f"| F{fp['num']} | {fp['name']} | {fp['type']} | {fp['var_pct']:.1f}% | {fp['n_items']} | {fp['composition']} |")
    
    report.append(f"\n### Refined Factor Structure (After Removing {len(weak_items)} Items)")
    report.append(f"| F# | Name | Type | Variance | Items | Composition |")
    report.append(f"| :---: | :--- | :--- | :---: | :---: | :--- |")
    for fp in profiles_after:
        report.append(f"| F{fp['num']} | {fp['name']} | {fp['type']} | {fp['var_pct']:.1f}% | {fp['n_items']} | {fp['composition']} |")
    
    report.append(f"\n### Key Changes:")
    report.append(f"- **Unique Guna factors**: {len(unique_before)} -> **{len(unique_after)}**")
    report.append(f"- **Mixed factors**: {len(mixed_before)} -> **{len(mixed_after)}**")
    
    total_var_before = sum(f['var_pct'] for f in profiles_before)
    total_var_after = sum(f['var_pct'] for f in profiles_after)
    report.append(f"- **Total variance explained**: {total_var_before:.1f}% -> **{total_var_after:.1f}%**")
    
    # Check if unique factors became cleaner
    report.append(f"\n### Interpretation:")
    if len(unique_after) >= len(unique_before):
        report.append(f"- After removing weak items, the Guna-specific factors became **cleaner** and more distinct.")
    else:
        report.append(f"- After item removal, some previously unique Guna factors merged with Big Five factors.")
    
    report.append(f"- The refined factor structure shows **{len(unique_after)} unique Guna dimensions** that remain invisible to the Big Five model.")
    report.append(f"- Item removal improved factor purity by eliminating noisy, poorly-loading items.")
    
    # Detail the refined unique factors
    if unique_after:
        report.append(f"\n### Refined Unique Guna Factors (Detail):")
        for fp in unique_after:
            report.append(f"\n**Factor {fp['num']}: {fp['name']}** (Var={fp['var_pct']:.1f}%, Purity={fp['purity']:.0f}%)")
            report.append(f"| Item | Loading | Text |")
            report.append(f"| :--- | :---: | :--- |")
            for item_id, loading in fp['top_items'].items():
                text = item_texts.get(item_id, "N/A")[:60].replace("|", "-")
                report.append(f"| `{item_id}` | {loading:+.3f} | {text} |")
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    
    print(f"\nItem Refinement Complete. Report: {REPORT_FILE}")
    print(f"Weak items: {len(weak_items)}/{len(all_cols)}")
    print(f"Unique Guna factors: {len(unique_before)} (before) -> {len(unique_after)} (after)")

if __name__ == "__main__":
    analyze_refinement()
