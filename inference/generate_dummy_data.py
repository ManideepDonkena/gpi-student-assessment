
import json
import random
import os
import argparse
import pandas as pd
from datetime import datetime
import numpy as np

# Configuration
NUM_RESPONDENTS = 200
OUTPUT_DIR = "dummy_data"
SCENARIOS_PATH = os.path.join(os.path.dirname(__file__), "../src/scenarios.json")

def load_scenarios():
    with open(SCENARIOS_PATH, 'r') as f:
        return json.load(f)

def generate_respondent(scenarios, archetype):
    """
    Generate a single respondent's session data based on an archetype.
    Archetypes: 'sattva', 'rajas', 'tamas', 'mixed'
    """
    respondent_id = f"resp_{random.randint(10000, 99999)}"
    
    # Biases based on archetype (probability of choosing that guna's option)
    if archetype == 'sattva':
        weights = {'sattva': 0.7, 'rajas': 0.2, 'tamas': 0.1}
        # Sattva types take moderate time (deliberate)
        base_time_ms = 5000 
    elif archetype == 'rajas':
        weights = {'sattva': 0.2, 'rajas': 0.7, 'tamas': 0.1}
        # Rajas types are fast
        base_time_ms = 2500
    elif archetype == 'tamas':
        weights = {'sattva': 0.1, 'rajas': 0.2, 'tamas': 0.7}
        # Tamas types are slow or very variable
        base_time_ms = 8000
    else: # mixed
        weights = {'sattva': 0.33, 'rajas': 0.33, 'tamas': 0.33}
        base_time_ms = 4000
    
    session_data = {
        "sessionId": respondent_id,
        "timestamp": datetime.now().isoformat(),
        "demographics": {
            "age": random.randint(18, 65),
            "gender": random.choice(["Male", "Female", "Other"]),
            "occupation": random.choice(["Student", "Professional", "Self-employed", "Unemployed"]),
            "archetype_label": archetype # Ground truth for validation
        },
        "responses": []
    }
    
    for scenario in scenarios:
        # Determine choice based on weights
        # We need to map options to their dominant weight to pick one
        options = scenario['choices']
        option_weights = []
        
        for opt in options:
            # Simple heuristic: which guna is dominant in this option?
            dom_guna = max(opt['weights'], key=opt['weights'].get)
            option_weights.append(weights[dom_guna])
        
        # Normalize weights to probabilities
        total_w = sum(option_weights)
        probs = [w / total_w for w in option_weights]
        
        chosen_idx = np.random.choice(range(len(options)), p=probs)
        chosen_option = options[chosen_idx]
        
        # Simulate timing
        # Log-normal distribution for reaction times
        time_taken = int(np.random.lognormal(mean=np.log(base_time_ms), sigma=0.4))
        
        response = {
            "scenarioId": scenario['id'],
            "choiceId": chosen_option['id'],
            "timeToSelectMs": time_taken,
            "hoverCount": random.randint(0, 3)
        }
        session_data['responses'].append(response)
        
    return session_data

def main():
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    scenarios = load_scenarios()
    
    print(f"Generating {NUM_RESPONDENTS} dummy respondents...")
    
    archetypes = ['sattva'] * 50 + ['rajas'] * 50 + ['tamas'] * 50 + ['mixed'] * 50
    random.shuffle(archetypes)
    
    summary_data = []
    
    for i, arch in enumerate(archetypes):
        data = generate_respondent(scenarios, arch)
        
        # Save JSON
        filename = f"{OUTPUT_DIR}/{data['sessionId']}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
            
        summary_data.append({
            "id": data['sessionId'],
            "archetype": arch,
            "file": filename
        })
        
    # Save summary CSV
    df = pd.DataFrame(summary_data)
    df.to_csv("dummy_data_summary.csv", index=False)
    print(f"Done. Saved {NUM_RESPONDENTS} files to {OUTPUT_DIR}/ and summary to dummy_data_summary.csv")

if __name__ == "__main__":
    main()
