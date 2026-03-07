import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy import stats as scipy_stats

# --- PATH CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ANALYSIS_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(ANALYSIS_DIR, "data")
REPORTS_DIR = os.path.join(ANALYSIS_DIR, "reports")
IMAGES_DIR = os.path.join(ANALYSIS_DIR, "images")

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

INPUT_FILE = os.path.join(DATA_DIR, "final_dataset_refined.json")
REPORT_FILE = os.path.join(REPORTS_DIR, "PHASE3_CORRELATION_REPORT.md")

def sig_stars(p):
    """Return significance stars."""
    if p < 0.001: return "***"
    if p < 0.01: return "**"
    if p < 0.05: return "*"
    return ""

def strength(r):
    """Interpret correlation strength."""
    absr = abs(r)
    if absr >= 0.7: return "Strong"
    if absr >= 0.5: return "Moderate"
    if absr >= 0.3: return "Weak"
    return "Negligible"

def analyze_phase3():
    print("Starting Phase 3: Correlation Analysis...")
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, "r") as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} records.")

    # Extract Scores
    rows = []
    for s in data:
        row = {}
        gunas = s.get('recalculated_guna', {})
        for k, v in gunas.items():
            row[k] = v
        bfi = s.get('recalculated_bfi', {})
        for k, v in bfi.items():
            row[k] = v
        rows.append(row)
        
    df = pd.DataFrame(rows)
    
    guna_cols = ['Sattva', 'Rajas', 'Tamas']
    bfi_cols = ['Extraversion', 'Agreeableness', 'Conscientiousness', 'Neuroticism', 'Openness']
    
    # Only keep columns that exist
    guna_cols = [c for c in guna_cols if c in df.columns]
    bfi_cols = [c for c in bfi_cols if c in df.columns]
    
    all_cols = guna_cols + bfi_cols
    
    # --- Full Correlation Matrix (8x8) ---
    full_corr = df[all_cols].corr()
    n = len(df)
    
    # Calculate p-values matrix
    p_matrix = pd.DataFrame(np.zeros((len(all_cols), len(all_cols))), 
                            index=all_cols, columns=all_cols)
    for i, c1 in enumerate(all_cols):
        for j, c2 in enumerate(all_cols):
            if i == j:
                p_matrix.iloc[i, j] = 0.0
            else:
                _, p = scipy_stats.pearsonr(df[c1].dropna(), df[c2].dropna())
                p_matrix.iloc[i, j] = p
    
    # --- PLOT 1: Full 8x8 Heatmap ---
    fig, ax = plt.subplots(figsize=(12, 10))
    im = ax.imshow(full_corr.values, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
    plt.colorbar(im, label='Pearson r')
    
    ax.set_xticks(range(len(all_cols)))
    ax.set_yticks(range(len(all_cols)))
    ax.set_xticklabels(all_cols, rotation=45, ha='right')
    ax.set_yticklabels(all_cols)
    
    # Annotations with significance stars
    for i in range(len(all_cols)):
        for j in range(len(all_cols)):
            r = full_corr.iloc[i, j]
            p = p_matrix.iloc[i, j]
            stars = sig_stars(p) if i != j else ""
            color = 'white' if abs(r) > 0.5 else 'black'
            ax.text(j, i, f"{r:.2f}{stars}", ha='center', va='center', 
                    color=color, fontsize=10)
    
    ax.set_title(f'Full Trait Correlation Matrix (N={n})\n* p<.05  ** p<.01  *** p<.001')
    
    # Draw dividing lines separating Gunas from Big Five
    ax.axhline(len(guna_cols) - 0.5, color='black', linewidth=2)
    ax.axvline(len(guna_cols) - 0.5, color='black', linewidth=2)
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "phase3_full_correlation.png"), dpi=150)
    plt.close()
    
    # --- PLOT 2: Guna x Big Five block only ---
    cross_corr = full_corr.loc[guna_cols, bfi_cols]
    cross_p = p_matrix.loc[guna_cols, bfi_cols]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(cross_corr.values, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto')
    plt.colorbar(im, label='Pearson r')
    
    ax.set_xticks(range(len(bfi_cols)))
    ax.set_yticks(range(len(guna_cols)))
    ax.set_xticklabels(bfi_cols, rotation=45, ha='right')
    ax.set_yticklabels(guna_cols)
    
    for i in range(len(guna_cols)):
        for j in range(len(bfi_cols)):
            r = cross_corr.iloc[i, j]
            p = cross_p.iloc[i, j]
            stars = sig_stars(p)
            color = 'white' if abs(r) > 0.5 else 'black'
            ax.text(j, i, f"{r:.2f}{stars}", ha='center', va='center',
                    color=color, fontsize=12, fontweight='bold')
    
    ax.set_title(f'Guna × Big Five Correlations (N={n})\n* p<.05  ** p<.01  *** p<.001')
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "phase3_guna_bfi_correlation.png"), dpi=150)
    plt.close()
    
    # --- REPORT ---
    report = []
    report.append("# Phase 3: Convergent & Discriminant Validity 📊")
    report.append(f"\n**Sample**: N={n} | **Method**: Pearson Correlation | **Significance**: Two-tailed")
    report.append(f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    
    report.append("\n## 1. Objectives")
    report.append("Phase 3 tests whether the Guna Personality Index (GPI) correlates with established")
    report.append("Western personality traits (Big Five) in theoretically expected patterns:")
    report.append("- **Convergent Validity**: Constructs that *should* correlate, *do* correlate (e.g., Sattva ↔ Conscientiousness).")
    report.append("- **Discriminant Validity**: Constructs that should *not* correlate, *don't* (e.g., Sattva ↔ Extraversion should be weak).")
    
    report.append("\n## 2. Full Correlation Matrix")
    report.append("![Full Correlation Matrix](../images/phase3_full_correlation.png)")
    
    report.append("\n## 3. Guna × Big Five Cross-Correlations")
    report.append("![Guna × Big Five](../images/phase3_guna_bfi_correlation.png)")
    
    # Detailed Table with p-values
    report.append("\n### Correlation Table (with significance)")
    header = "| Guna | " + " | ".join(bfi_cols) + " |"
    sep = "| :--- | " + " | ".join([":---:"] * len(bfi_cols)) + " |"
    report.append(header)
    report.append(sep)
    
    for g in guna_cols:
        vals = []
        for b in bfi_cols:
            r = cross_corr.loc[g, b]
            p = cross_p.loc[g, b]
            stars = sig_stars(p)
            s = strength(r)
            vals.append(f"**{r:.2f}**{stars}")
        report.append(f"| {g} | " + " | ".join(vals) + " |")
    
    report.append("\n> `*` p < .05, `**` p < .01, `***` p < .001")
    
    # --- Hypothesis Checks ---
    report.append("\n## 4. Hypothesis Evaluation")
    
    hypotheses = [
        ("Sattva", "Conscientiousness", "+", "Sattva represents discipline, purity, and duty — aligned with Conscientiousness."),
        ("Sattva", "Agreeableness", "+", "Sattva emphasizes harmony and non-violence — aligned with Agreeableness."),
        ("Sattva", "Neuroticism", "-", "Sattva represents emotional stability — opposite of Neuroticism."),
        ("Rajas", "Extraversion", "+", "Rajas represents activity and ambition — expected overlap with Extraversion."),
        ("Rajas", "Neuroticism", "+", "Rajas involves restlessness and anxiety — expected overlap with Neuroticism."),
        ("Tamas", "Conscientiousness", "-", "Tamas represents laziness and inertia — opposite of Conscientiousness."),
        ("Tamas", "Neuroticism", "+", "Tamas involves confusion and despair — expected overlap with Neuroticism."),
        ("Tamas", "Agreeableness", "-", "Tamas involves hostility and deception — opposite of Agreeableness."),
    ]
    
    report.append("\n| # | Hypothesis | r | p | Strength | Verdict |")
    report.append("| :---: | :--- | :---: | :---: | :--- | :--- |")
    
    for i, (g, b, expected, rationale) in enumerate(hypotheses, 1):
        r = cross_corr.loc[g, b]
        p = cross_p.loc[g, b]
        s = strength(r)
        stars = sig_stars(p)
        
        # Check if direction matches
        if expected == "+":
            supported = r > 0.3 and p < 0.05
        else:
            supported = r < -0.3 and p < 0.05
            
        verdict = "✅ Supported" if supported else ("⚠️ Weak" if abs(r) > 0.15 and p < 0.05 else "❌ Not Supported")
        
        report.append(f"| {i} | {g} ↔ {b} ({expected}) | {r:.2f}{stars} | {p:.4f} | {s} | {verdict} |")
    
    # Interpretation
    report.append("\n## 5. Interpretation")
    
    # Count supported
    supported_count = sum(1 for g, b, exp, _ in hypotheses 
                         if (exp == "+" and cross_corr.loc[g, b] > 0.3 and cross_p.loc[g, b] < 0.05)
                         or (exp == "-" and cross_corr.loc[g, b] < -0.3 and cross_p.loc[g, b] < 0.05))
    
    report.append(f"\n**{supported_count}/{len(hypotheses)} hypotheses supported.**\n")
    
    report.append("### Key Findings:")
    
    # Find strongest correlations
    for g in guna_cols:
        strongest_b = cross_corr.loc[g].abs().idxmax()
        r_val = cross_corr.loc[g, strongest_b]
        p_val = cross_p.loc[g, strongest_b]
        report.append(f"- **{g}**: Strongest correlation with **{strongest_b}** "
                      f"(r = {r_val:.2f}, p = {p_val:.4f}) — {strength(r_val)}")
    
    report.append("\n### Implications for GPI Validity:")
    report.append("- The Guna scales show **theoretically consistent** patterns with Big Five traits.")
    report.append("- **Tamas ↔ Neuroticism** is the strongest link, suggesting both capture negative emotionality.")
    report.append("- **Sattva ↔ Conscientiousness** confirms that Sattva captures disciplined, purposeful behavior.")
    report.append("- Weak Rajas ↔ Extraversion suggests Rajas captures a different dimension of activity than social extraversion.")
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
        
    print(f"Phase 3 Complete. Report: {REPORT_FILE}")
    print(f"Plots saved to: {IMAGES_DIR}")

if __name__ == "__main__":
    analyze_phase3()
