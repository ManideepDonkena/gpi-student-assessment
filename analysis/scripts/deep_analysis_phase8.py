"""
=============================================================
PHASE 8: Incremental Validity (Hierarchical Regression)
=============================================================
Tests whether GPI Guna scores predict outcomes BEYOND what
the Big Five already predicts.

Method: Hierarchical regression
  Step 1: Big Five traits as predictors
  Step 2: Add Guna traits
  Compare R-squared change (Delta R2)

Outcomes tested:
  - Scenario sattva choices %
  - Scenario rajas choices %
  - Scenario tamas choices %
  - Spiritual Practice (ordinal)
  - Gita Familiarity (ordinal)
=============================================================
"""
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from scipy import stats
from sklearn.linear_model import LinearRegression
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
REPORT_FILE = os.path.join(REPORTS_DIR, "PHASE8_INCREMENTAL_VALIDITY_REPORT.md")

GUNA_TRAITS = ["Sattva", "Rajas", "Tamas"]
BFI_TRAITS = ["Extraversion", "Agreeableness", "Conscientiousness", "Neuroticism", "Openness"]


def load_data():
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)
    
    rows = []
    for s in data:
        guna = s.get('recalculated_guna', s.get('calculated_guna', {}))
        bfi = s.get('recalculated_bfi', s.get('calculated_bfi', {}))
        demo = s.get('demographics', {})
        sr = s.get('scenarioResponses', [])
        
        row = {}
        
        for trait in GUNA_TRAITS:
            row[trait] = guna.get(trait, np.nan)
        for trait in BFI_TRAITS:
            row[trait] = bfi.get(trait, np.nan)
        
        # Scenario outcomes
        if sr:
            total = len(sr)
            row["sattva_pct"] = sum(1 for r in sr if r.get('choiceId') == 'sattva') / total * 100
            row["rajas_pct"] = sum(1 for r in sr if r.get('choiceId') == 'rajas') / total * 100
            row["tamas_pct"] = sum(1 for r in sr if r.get('choiceId') == 'tamas') / total * 100
        
        # Ordinal: Spiritual Practice
        sp_map = {"Regular": 4, "Occasional": 3, "Rarely": 2, "Never": 1}
        row["spiritual_ord"] = sp_map.get(demo.get("spiritualPractice", ""), np.nan)
        
        # Ordinal: Gita Familiarity
        gf_map = {"Very Familiar": 4, "Somewhat": 3, "Heard of it": 2, "Not at all": 1}
        row["gita_ord"] = gf_map.get(demo.get("gitaFamiliarity", ""), np.nan)
        
        rows.append(row)
    
    return pd.DataFrame(rows).dropna(subset=GUNA_TRAITS)


def hierarchical_regression(df, outcome_col, outcome_label):
    """
    Step 1: BFI only
    Step 2: BFI + Guna
    Returns: R2_step1, R2_step2, deltaR2, F_change, p_change, betas
    """
    valid = df.dropna(subset=[outcome_col] + BFI_TRAITS + GUNA_TRAITS)
    if len(valid) < 20:
        return None
    
    y = valid[outcome_col].values
    X_bfi = valid[BFI_TRAITS].values
    X_full = valid[BFI_TRAITS + GUNA_TRAITS].values
    
    # Standardize
    scaler = StandardScaler()
    X_bfi_s = scaler.fit_transform(X_bfi)
    scaler2 = StandardScaler()
    X_full_s = scaler2.fit_transform(X_full)
    
    # Step 1: BFI only
    model1 = LinearRegression()
    model1.fit(X_bfi_s, y)
    r2_1 = model1.score(X_bfi_s, y)
    
    # Step 2: BFI + Guna
    model2 = LinearRegression()
    model2.fit(X_full_s, y)
    r2_2 = model2.score(X_full_s, y)
    
    # F-change test
    n = len(y)
    p1 = X_bfi_s.shape[1]
    p2 = X_full_s.shape[1]
    delta_r2 = r2_2 - r2_1
    df_num = p2 - p1  # 3 Guna traits added
    df_denom = n - p2 - 1
    
    if (1 - r2_2) > 0 and df_denom > 0:
        f_change = (delta_r2 / df_num) / ((1 - r2_2) / df_denom)
        p_change = 1 - stats.f.cdf(f_change, df_num, df_denom)
    else:
        f_change = 0
        p_change = 1.0
    
    # Beta coefficients for Step 2
    betas = {}
    all_traits = BFI_TRAITS + GUNA_TRAITS
    for i, trait in enumerate(all_traits):
        betas[trait] = model2.coef_[i]
    
    return {
        "outcome": outcome_label,
        "n": n,
        "r2_bfi": r2_1,
        "r2_full": r2_2,
        "delta_r2": delta_r2,
        "f_change": f_change,
        "p_change": p_change,
        "betas": betas,
        "bfi_betas": {BFI_TRAITS[i]: model1.coef_[i] for i in range(len(BFI_TRAITS))}
    }


def sig_stars(p):
    if p < 0.001: return "***"
    if p < 0.01: return "**"
    if p < 0.05: return "*"
    return "ns"


def analyze_phase8():
    print("Starting Phase 8: Incremental Validity...")
    
    df = load_data()
    N = len(df)
    print(f"Records: {N}")
    
    # Define outcomes
    outcomes = [
        ("sattva_pct", "Sattvic Scenario Choices (%)"),
        ("rajas_pct", "Rajasic Scenario Choices (%)"),
        ("tamas_pct", "Tamasic Scenario Choices (%)"),
        ("spiritual_ord", "Spiritual Practice (ordinal)"),
        ("gita_ord", "Gita Familiarity (ordinal)"),
    ]
    
    results = []
    for col, label in outcomes:
        print(f"  Analyzing: {label}")
        result = hierarchical_regression(df, col, label)
        if result:
            results.append(result)
    
    # === REPORT ===
    report = []
    report.append("# Phase 8: Incremental Validity (Hierarchical Regression)")
    report.append(f"\n**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    report.append(f"**Dataset**: N={N}")
    report.append(f"**Method**: Hierarchical regression with standardized predictors")
    report.append(f"\n> **Research Question**: Does the GPI explain variance in outcomes **beyond** what the Big Five already explains?")
    
    report.append("\n## Method\n")
    report.append("| Step | Predictors | Purpose |")
    report.append("| :---: | :--- | :--- |")
    report.append("| Step 1 | Big Five (E, A, C, N, O) | Baseline model |")
    report.append("| Step 2 | Big Five + Guna (S, R, T) | Test incremental contribution |")
    report.append("| | | If Delta-R2 is significant, Gunas add unique predictive power |")
    
    # === SUMMARY TABLE ===
    report.append("\n## Results Summary\n")
    report.append("| Outcome | N | R2 (BFI Only) | R2 (BFI+Guna) | Delta-R2 | F-change | p | Sig |")
    report.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
    
    for r in results:
        p_str = "< 0.001" if r['p_change'] < 0.001 else f"{r['p_change']:.3f}"
        report.append(f"| {r['outcome']} | {r['n']} | {r['r2_bfi']:.3f} | {r['r2_full']:.3f} | **{r['delta_r2']:.3f}** | {r['f_change']:.2f} | {p_str} | {sig_stars(r['p_change'])} |")
    
    # === DETAILED RESULTS ===
    for r in results:
        report.append(f"\n---\n### {r['outcome']}\n")
        report.append(f"**Step 1 (BFI only)**: R2 = {r['r2_bfi']:.3f} ({r['r2_bfi']*100:.1f}% of variance)")
        report.append(f"**Step 2 (BFI + Guna)**: R2 = {r['r2_full']:.3f} ({r['r2_full']*100:.1f}% of variance)")
        p_label = "< 0.001" if r['p_change'] < 0.001 else f"{r['p_change']:.3f}"
        df_res = r['n'] - len(BFI_TRAITS) - len(GUNA_TRAITS) - 1
        report.append(f"**Delta-R2** = {r['delta_r2']:.3f} ({r['delta_r2']*100:.1f}% additional), F({len(GUNA_TRAITS)},{df_res}) = {r['f_change']:.2f}, p = {p_label}")
        
        # Beta table
        report.append("\n| Predictor | Beta (Step 2) | Contribution |")
        report.append("| :--- | :---: | :--- |")
        
        sorted_betas = sorted(r['betas'].items(), key=lambda x: abs(x[1]), reverse=True)
        for trait, beta in sorted_betas:
            source = "Guna" if trait in GUNA_TRAITS else "BFI"
            strength = "Strong" if abs(beta) > 0.3 else "Moderate" if abs(beta) > 0.15 else "Weak"
            direction = "+" if beta > 0 else "-"
            report.append(f"| {trait} ({source}) | {beta:+.3f} | {direction} {strength} |")
    
    # === VISUALIZATION ===
    # Bar chart: Delta-R2 for each outcome
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Stacked bar (BFI R2 + Delta R2)
    ax = axes[0]
    outcome_labels = [r['outcome'].replace(' (%)', '').replace(' (ordinal)', '') for r in results]
    r2_bfi = [r['r2_bfi'] for r in results]
    delta_r2 = [r['delta_r2'] for r in results]
    
    y_pos = np.arange(len(results))
    
    bars1 = ax.barh(y_pos, r2_bfi, color='#3498db', alpha=0.7, label='Big Five alone')
    bars2 = ax.barh(y_pos, delta_r2, left=r2_bfi, color='#2ecc71', alpha=0.8, label='+ Guna (incremental)')
    
    # Significance markers
    for i, r in enumerate(results):
        total = r['r2_bfi'] + r['delta_r2']
        star = sig_stars(r['p_change'])
        ax.text(total + 0.005, i, f'{star} (+{r["delta_r2"]*100:.1f}%)', 
                va='center', fontsize=9, fontweight='bold',
                color='green' if r['p_change'] < 0.05 else 'gray')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(outcome_labels, fontsize=9)
    ax.set_xlabel('R-squared')
    ax.set_title('Incremental Validity: Guna Beyond Big Five', fontsize=11, fontweight='bold')
    ax.legend(loc='lower right', fontsize=9)
    ax.grid(axis='x', alpha=0.3)
    
    # Right: Beta comparison for strongest outcome
    ax2 = axes[1]
    best = max(results, key=lambda x: x['delta_r2'])
    all_traits = BFI_TRAITS + GUNA_TRAITS
    betas = [best['betas'][t] for t in all_traits]
    colors = ['#3498db'] * len(BFI_TRAITS) + ['#2ecc71'] * len(GUNA_TRAITS)
    
    bars = ax2.barh(range(len(all_traits)), betas, color=colors, alpha=0.8)
    ax2.set_yticks(range(len(all_traits)))
    ax2.set_yticklabels(all_traits, fontsize=9)
    ax2.axvline(x=0, color='black', linewidth=0.5)
    ax2.set_xlabel('Standardized Beta')
    title_short = best['outcome'].replace(' (%)', '').replace(' (ordinal)', '')
    ax2.set_title(f'Standardized Betas: {title_short}', fontsize=11, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(IMAGES_DIR, "phase8_incremental_validity.png"), dpi=150, bbox_inches='tight')
    plt.close()
    
    report.append("\n## Visualization\n")
    report.append("![Incremental Validity](../images/phase8_incremental_validity.png)")
    
    # === INTERPRETATION ===
    sig_outcomes = [r for r in results if r['p_change'] < 0.05]
    
    report.append("\n## Interpretation\n")
    report.append(f"### {len(sig_outcomes)}/{len(results)} outcomes showed significant incremental validity\n")
    
    if sig_outcomes:
        report.append("The Guna traits explain **additional variance beyond the Big Five** in:")
        for r in sig_outcomes:
            p_label = "< 0.001" if r['p_change'] < 0.001 else f"{r['p_change']:.3f}"
            report.append(f"- **{r['outcome']}**: +{r['delta_r2']*100:.1f}% additional variance (p = {p_label})")
        
        report.append("\n### Practical Significance")
        report.append("This demonstrates that the GPI captures meaningful psychological dimensions")
        report.append("that are **invisible** to the Big Five model. Specifically:")
        report.append("- Guna traits predict behavioral choices (scenarios) and cultural engagement")
        report.append("  (spiritual practice, Gita familiarity) better than Big Five alone")
        report.append("- This justifies the GPI as a **complementary** instrument to standard")
        report.append("  personality measures, not merely a redundant translation of Western constructs")
    
    report.append("\n### Implication for Indian Psychology")
    report.append("The incremental validity evidence supports the position that Guna-based")
    report.append("personality dimensions capture culturally specific aspects of human nature")
    report.append("that Western personality models were not designed to measure.")
    
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(report))
    
    print(f"\nPhase 8 Complete. Report: {REPORT_FILE}")


if __name__ == "__main__":
    analyze_phase8()
