
import os
import json
import glob
import pandas as pd
import argparse
import matplotlib.pyplot as plt
from score_session import calculate_weighted_scores
from bayesian_estimation import estimate_guna_profile

# Configuration
SCENARIOS_PATH = os.path.join(os.path.dirname(__file__), "../src/scenarios.json")

def load_scenarios():
    with open(SCENARIOS_PATH, 'r') as f:
        return json.load(f)

def analyze_sessions(input_dir, output_file="analysis_results.csv"):
    scenarios = load_scenarios()
    
    # Find all JSON files
    files = glob.glob(os.path.join(input_dir, "*.json"))
    print(f"Found {len(files)} session files in {input_dir}")
    
    results = []
    
    for file_path in files:
        try:
            with open(file_path, 'r') as f:
                session = json.load(f)
                
            # method 1: Weighted Scoring
            raw_scores, weighted_profile = calculate_weighted_scores(session, scenarios)
            
            # method 2: Bayesian Estimation
            bayes_probs, _ = estimate_guna_profile(session['responses'], scenarios)
            
            # Ground Truth (if available in dummy data)
            archetype = session.get('demographics', {}).get('archetype_label', 'unknown')
            
            row = {
                "session_id": session.get('sessionId'),
                "archetype": archetype,
                "weighted_sattva": weighted_profile['sattva'],
                "weighted_rajas": weighted_profile['rajas'],
                "weighted_tamas": weighted_profile['tamas'],
                "bayes_sattva": bayes_probs['sattva'] * 100,
                "bayes_rajas": bayes_probs['rajas'] * 100,
                "bayes_tamas": bayes_probs['tamas'] * 100,
            }
            results.append(row)
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    # Save to CSV
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"Analysis complete. Results saved to {output_file}")
    
    # Visualization
    plot_distributions(df)
    
def plot_distributions(df):
    plt.figure(figsize=(12, 5))
    
    # Plot Bayesian results by Archetype
    archetypes = df['archetype'].unique()
    
    for i, arch in enumerate(archetypes):
        subset = df[df['archetype'] == arch]
        if subset.empty: continue
        
        plt.subplot(1, len(archetypes), i+1)
        mean_s = subset['bayes_sattva'].mean()
        mean_r = subset['bayes_rajas'].mean()
        mean_t = subset['bayes_tamas'].mean()
        
        plt.bar(['Sattva', 'Rajas', 'Tamas'], [mean_s, mean_r, mean_t], color=['gold', 'red', 'grey'])
        plt.title(f"Archetype: {arch}\n(N={len(subset)})")
        plt.ylim(0, 100)
    
    plt.tight_layout()
    plt.savefig("guna_distribution_plot.png")
    print("Plot saved to guna_distribution_plot.png")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="dummy_data", help="Directory containing session JSONs")
    args = parser.parse_args()
    
    analyze_sessions(args.input)
