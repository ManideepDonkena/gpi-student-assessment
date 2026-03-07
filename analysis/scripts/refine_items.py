import json
import pandas as pd
import os

# --- PATH CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ANALYSIS_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(ANALYSIS_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Items to Drop (Based on Phase 2 Reliability Analysis)
ITEMS_TO_DROP = [
    "BFI41", "BFI35", # Openness Fix
    "R_AV", "R_BX"    # Rajas Optimization
]

def refine_dataset():
    input_file = os.path.join(DATA_DIR, "bfi44_cleaned.json")
    output_file = os.path.join(DATA_DIR, "final_dataset_refined.json")
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Run clean_and_analyze.py first.")
        return

    with open(input_file, 'r') as f:
        data = json.load(f)
        
    print(f"Loading {len(data)} sessions from {input_file}...")
    print(f"Dropping Items: {ITEMS_TO_DROP}")
    
    refined_data = []
    
    for session in data:
        # Create copies of response dicts
        guna = session.get('gunaResponses', {}).copy()
        bfi = session.get('bigFiveResponses', {}).copy()
        
        # Remove items
        for item in ITEMS_TO_DROP:
            if item in guna: del guna[item]
            if item in bfi: del bfi[item]
            
        # Update session with cleaned responses
        session['gunaResponses'] = guna
        session['bigFiveResponses'] = bfi
        
        # Note: Recalculated scores in the session dict (e.g. 'recalculated_guna')
        # might need updating if they were heavily dependent on these items.
        # For valid analysis, we should re-calculate scores downstream or here.
        # Let's mark this session as 'refined'.
        session['is_refined'] = True
        
        refined_data.append(session)
        
    with open(output_file, 'w') as f:
        json.dump(refined_data, f, indent=2)
        
    print(f"✅ Saved refined dataset to {output_file} (N={len(refined_data)})")
    print("Ready for Phase 3 (Factor Analysis).")

if __name__ == "__main__":
    refine_dataset()
