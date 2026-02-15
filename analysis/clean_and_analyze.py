import json
import pandas as pd
import os

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
# Note: This is an approximation based on standard BFI-44 traits
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
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r') as f:
        data = json.load(f)

    print(f"Total sessions loaded: {len(data)}")

    cleaned_data = []
    fake_count = 0

    for session in data:
        bf_resps = session.get('bigFiveResponses', {})
        guna_resps = session.get('gunaResponses', {})
        n_bf = len(bf_resps)
        n_guna = len(guna_resps)
        total_items = n_bf + n_guna
        
        if total_items == 0: continue

        timings = session.get('viewTimings', {})
        total_time_ms = timings.get('bigfive-likert', 0) + timings.get('guna-likert', 0)
        art = (total_time_ms / total_items) / 1000.0 if total_items > 0 else 0

        if art <= 1.5:
            fake_count += 1
            continue
            
        # Recalculate everything for consistency
        session['cohort'] = 'BFI-44' if n_bf > 20 else 'BFI-10'
        session['avg_reaction_time'] = art
        session['recalculated_guna'] = calculate_guna_scores(guna_resps)
        session['recalculated_bfi'] = calculate_bfi_scores(bf_resps, n_bf)
        cleaned_data.append(session)

    print(f"Fake sessions removed (ART <= 1.5s): {fake_count}")
    print(f"Clean sessions remaining: {len(cleaned_data)}")

    # 4. Preliminary Stats
    bfi10_data = [s for s in cleaned_data if s['cohort'] == 'BFI-10']
    bfi44_data = [s for s in cleaned_data if s['cohort'] == 'BFI-44']

    def get_prelim_stats(cohort_data, name):
        if not cohort_data: return f"\n--- No data for {name} ---"
        
        stats = [f"\n--- Preliminary Analysis: {name} ---", f"Sample Size: {len(cohort_data)}"]
        
        # Genders
        genders = pd.DataFrame([s.get('demographics', {}).get('gender', 'Unknown') for s in cohort_data])[0].value_counts().to_dict()
        stats.append(f"Genders: {genders}")
        
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
    
    with open("CLEAN_ANALYSIS_REPORT.md", "w") as f:
        f.write("# Cleaned Assessment Analysis Report\n")
        f.write(f"**Filtering Criterion**: Avg Reaction Time > 1.5 seconds per item.\n")
        f.write(report)

    # Save cleaned JSONs for psychometric analysis
    with open("bfi10_cleaned.json", "w") as f:
        json.dump(bfi10_data, f, indent=2)
    with open("bfi44_cleaned.json", "w") as f:
        json.dump(bfi44_data, f, indent=2)

if __name__ == "__main__":
    clean_and_analyze()
