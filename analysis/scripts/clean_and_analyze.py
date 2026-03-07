import json
import pandas as pd
import os
import sys

# --- PATH CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ANALYSIS_DIR = os.path.dirname(SCRIPT_DIR) # Parent of scripts/ is analysis/
DATA_DIR = os.path.join(ANALYSIS_DIR, "data")
REPORTS_DIR = os.path.join(ANALYSIS_DIR, "reports")

# Ensure dirs exist
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# --- 1. CONFIGURATION ---
MIN_GUNA_TIME_MINUTES = 3.0  # Minimum time to spend on Guna section
MIN_BFI_TIME_MINUTES = 2.0   # Minimum time to spend on BFI section

# Standard BFI-10 Mapping (Id: BF1-BF10)
BFI10_MAPPING = {
    "BF1": {"trait": "Extraversion", "reverse": True},
    "BF2": {"trait": "Agreeableness", "reverse": False},
    "BF3": {"trait": "Conscientiousness", "reverse": True},
    "BF4": {"trait": "Neuroticism", "reverse": True},
    "BF5": {"trait": "Openness", "reverse": True},
    "BF6": {"trait": "Extraversion", "reverse": False},
    "BF7": {"trait": "Agreeableness", "reverse": True},
    "BF8": {"trait": "Conscientiousness", "reverse": False},
    "BF9": {"trait": "Neuroticism", "reverse": False},
    "BF10": {"trait": "Openness", "reverse": False},
}

# Standard BFI-44 Mapping (Id: BFI1-BFI44)
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

def calculate_guna_scores(responses):
    # Category based on ID prefix
    scores = {"Sattva": [], "Rajas": [], "Tamas": []}
    for q_id, val in responses.items():
        if q_id.startswith("S_"): scores["Sattva"].append(val)
        elif q_id.startswith("R_"): scores["Rajas"].append(val)
        elif q_id.startswith("T_"): scores["Tamas"].append(val)
    
    return {k: (sum(v)/len(v) if v else 0) for k, v in scores.items()}

def calculate_bfi_scores(responses, n_items):
    mapping = BFI44_MAPPING if n_items > 20 else BFI10_MAPPING
    traits = {"Extraversion": [], "Agreeableness": [], "Conscientiousness": [], "Neuroticism": [], "Openness": []}
    
    for q_id, val in responses.items():
        if q_id in mapping:
            meta = mapping[q_id]
            trait = meta["trait"]
            score = (6 - val) if meta["reverse"] else val
            traits[trait].append(score)
    
    return {k: (sum(v)/len(v) if v else 0) for k, v in traits.items()}

def clean_and_analyze(input_file="original_gpi_dump.json"):
    # Resolve absolute path for input
    input_path = os.path.join(DATA_DIR, input_file)
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, 'r') as f:
        data = json.load(f)

    print(f"Total sessions loaded: {len(data)}")

    cleaned_data = []
    
    # Counters for filtering
    stats_removed = {
        "dummy": 0,
        "guna_too_fast": 0,
        "bfi_too_fast": 0,
        "art_too_fast": 0,
        "bfi_careless": 0
    }

    # Helper: Convert minutes to ms
    min_guna_ms = MIN_GUNA_TIME_MINUTES * 60 * 1000
    min_bfi_ms = MIN_BFI_TIME_MINUTES * 60 * 1000

    print(f"\nConfiguration:")
    print(f"  - Minimum Guna Time: {MIN_GUNA_TIME_MINUTES} min ({int(min_guna_ms)} ms)")
    print(f"  - Minimum BFI Time:  {MIN_BFI_TIME_MINUTES} min ({int(min_bfi_ms)} ms)")

    for session in data:
        bf_resps = session.get('bigFiveResponses', {})
        guna_resps = session.get('gunaResponses', {})
        demos = session.get('demographics', {})
        timings = session.get('viewTimings', {})
        
        n_bf = len(bf_resps)
        n_guna = len(guna_resps)
        total_items = n_bf + n_guna
        
        if total_items == 0: continue

        # 1. Filter Dummy Data (Male + Homemaker)
        if demos.get('gender') == 'Male' and demos.get('occupation') == 'Homemaker':
            stats_removed["dummy"] += 1
            continue

        # 2. Time-Based Filtering (Specific Sections)
        time_guna = timings.get('guna-likert', 0)
        time_bfi = timings.get('bigfive-likert', 0)

        if time_guna < min_guna_ms:
            stats_removed["guna_too_fast"] += 1
            continue

        if time_bfi < min_bfi_ms:
            stats_removed["bfi_too_fast"] += 1
            continue

        # 3. Average Reaction Time Check (Backup sanity check)
        # Even if they meet the total time, if they clicked randomly fast (e.g. 0.5s per item), flag it.
        # Although Total Time check usually catches this, this is a secondary safe-guard.
        total_time_ms = time_guna + time_bfi
        art = (total_time_ms / total_items) / 1000.0 if total_items > 0 else 0

        if art <= 1.5:
            stats_removed["art_too_fast"] += 1
            continue

        # 4. Per-Item BFI Reaction Time Check (Careless Responding Detection)
        # If the MEDIAN reaction time per BFI item is < 1.5s, the respondent is clicking too fast.
        bfi_details = session.get('bigFiveDetails', {})
        if bfi_details:
            bfi_reaction_times = [
                item.get('reactionTimeMs', 0) 
                for item in bfi_details.values() 
                if isinstance(item, dict) and item.get('reactionTimeMs') is not None
            ]
            if bfi_reaction_times:
                median_bfi_rt = sorted(bfi_reaction_times)[len(bfi_reaction_times) // 2]
                if median_bfi_rt < 1500:  # < 1.5 seconds median
                    stats_removed["bfi_careless"] += 1
                    continue
            
        # Recalculate everything for consistency
        session['cohort'] = 'BFI-44' if n_bf > 20 else 'BFI-10'
        session['avg_reaction_time'] = art
        session['time_guna_min'] = time_guna / 60000.0
        session['time_bfi_min'] = time_bfi / 60000.0
        session['recalculated_guna'] = calculate_guna_scores(guna_resps)
        session['recalculated_bfi'] = calculate_bfi_scores(bf_resps, n_bf)
        cleaned_data.append(session)

    print(f"\nFiltering Report:")
    print(f"  - Dummy sessions (Male+Homemaker): {stats_removed['dummy']}")
    print(f"  - Guna Speed-run (< {MIN_GUNA_TIME_MINUTES}m): {stats_removed['guna_too_fast']}")
    print(f"  - BFI Speed-run (< {MIN_BFI_TIME_MINUTES}m):  {stats_removed['bfi_too_fast']}")
    print(f"  - Super-fast ART (<= 1.5s/item):   {stats_removed['art_too_fast']}")
    print(f"  - BFI Careless (median RT < 1.5s):  {stats_removed['bfi_careless']}")
    print(f"----------------------------------------")
    print(f"Clean sessions remaining (Pre-Tamas Filter): {len(cleaned_data)}")

    # 4. Preliminary Stats with Time Info
    bfi10_data = [s for s in cleaned_data if s['cohort'] == 'BFI-10']
    bfi44_data = [s for s in cleaned_data if s['cohort'] == 'BFI-44']

    # --- MANUAL OUTLIER REMOVAL (Improve Normality) ---
    # User Request (Feb 15, 2026): Remove extreme Tamas outliers to improve normality.
    # Threshold: Removed students with Tamas > 4.8
    initial_count = len(bfi44_data)
    bfi44_data = [s for s in bfi44_data if s['recalculated_guna']['Tamas'] <= 4.8]
    removed_count = initial_count - len(bfi44_data)
    
    if removed_count > 0:
        print(f"\n[Normality Filtering] Removed {removed_count} high-Tamas outliers (> 4.8).")
        print(f"New BFI-44 N = {len(bfi44_data)}")

    cleaned_data = bfi10_data + bfi44_data # Update main list for saving

    def get_prelim_stats(cohort_data, name):
        if not cohort_data: return f"\n--- No data for {name} ---"
        
        stats = [f"\n--- Preliminary Analysis: {name} ---", f"Sample Size: {len(cohort_data)}"]
        
        # Genders
        genders = pd.DataFrame([s.get('demographics', {}).get('gender', 'Unknown') for s in cohort_data])[0].value_counts().to_dict()
        stats.append(f"Genders: {genders}")
        
        # Timing Stats
        avg_guna_time = pd.DataFrame([s['time_guna_min'] for s in cohort_data]).mean()[0]
        avg_bfi_time = pd.DataFrame([s['time_bfi_min'] for s in cohort_data]).mean()[0]
        stats.append(f"Avg Time Spent: Guna={avg_guna_time:.1f}m, BFI={avg_bfi_time:.1f}m")

        # Scores
        guna_means = pd.DataFrame([s['recalculated_guna'] for s in cohort_data]).mean()
        bfi_means = pd.DataFrame([s['recalculated_bfi'] for s in cohort_data]).mean()
        
        stats.append("Avg Guna Scores:")
        stats.append(guna_means.to_string())
        stats.append("Avg Big Five Traits:")
        stats.append(bfi_means.to_string())
        
        return "\n".join(stats)

    report = get_prelim_stats(bfi10_data, "BFI-10 Group") + "\n" + get_prelim_stats(bfi44_data, "BFI-44 Group")
    print(report)
    
    report_path = os.path.join(REPORTS_DIR, "CLEAN_ANALYSIS_REPORT.md")
    with open(report_path, "w") as f:
        f.write("# Cleaned Assessment Analysis Report\n")
        f.write(f"**Filtering Criteria**:\n")
        f.write(f"- Min Guna Time: {MIN_GUNA_TIME_MINUTES} min\n")
        f.write(f"- Min BFI Time: {MIN_BFI_TIME_MINUTES} min\n")
        f.write(f"- Min Avg Reaction Time: 1.5s\n")
        f.write(report)

    # Save cleaned JSONs for psychometric analysis
    with open(os.path.join(DATA_DIR, "bfi10_cleaned.json"), "w") as f:
        json.dump(bfi10_data, f, indent=2)
    with open(os.path.join(DATA_DIR, "bfi44_cleaned.json"), "w") as f:
        json.dump(bfi44_data, f, indent=2)

if __name__ == "__main__":
    clean_and_analyze()
