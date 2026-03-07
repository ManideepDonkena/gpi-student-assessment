import json
import pandas as pd
import numpy as np
import os
import sys

# --- CONFIG ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "data")
REPORTS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "reports")

def main():
    print("="*60)
    print("  EXECUTIVE SUMMARY: KEY STATS FOR MANUSCRIPT UPDATE")
    print("="*60)
    
    # 1. Sample Size (N)
    refined_json = os.path.join(DATA_DIR, "final_dataset_refined.json")
    if os.path.exists(refined_json):
        with open(refined_json, 'r') as f:
            data = json.load(f)
            N = len(data)
            print(f"📌 Sample Size (Refined): N = {N}")
    else:
        print("❌ Refined dataset not found.")
        N = "???"

    # 2. Reliability (Alpha)
    # We can re-calculate or just check the report. Re-calc is safer.
    # (Simplified re-calc for speed, or just placeholder from last run if saved)
    # Actually, let's just grep the latest report or print a reminder. 
    # Better: Calculate it quickly here.
    
    print("-" * 40)
    print("📌 Internal Consistency (Crunching...)")
    # (Skipping full calc for brevity, assuming run_full_pipeline did it. 
    # But user wants 'capture new info easily'. A script that *actually* gets the number is best.)
    # Let's try to parse the PHASE2 report if it exists.
    phase2_report = os.path.join(REPORTS_DIR, "PHASE2_RELIABILITY_REPORT.md")
    if os.path.exists(phase2_report):
        try:
            with open(phase2_report, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            # Look for "Overall Cronbach's Alpha: **0.XX**"
            import re
            match = re.search(r"Sattva.*?\*\*([\d\.]+)\*\*", content)
            if match: print(f"   - Sattva Alpha: {match.group(1)}")
            match = re.search(r"Rajas.*?\*\*([\d\.]+)\*\*", content)
            if match: print(f"   - Rajas Alpha:  {match.group(1)}")
            match = re.search(r"Tamas.*?\*\*([\d\.]+)\*\*", content)
            if match: print(f"   - Tamas Alpha:  {match.group(1)}")
        except Exception as e:
            print(f"⚠️ Could not read reliability report: {e}")
    else:
        print("   (Run analyze_cronbach.py to generate)")

    # 3. KMO & VIF & R2 (from defense_stats.json)
    defense_stats_path = os.path.join(DATA_DIR, "defense_stats.json")
    if os.path.exists(defense_stats_path):
        try:
            with open(defense_stats_path, 'r') as f:
                defense_stats = json.load(f)
            
            print("-" * 40)
            print("📌 Advanced Stats (from reviewer_defense_v2.py)")
            print(f"   - KMO Score: {defense_stats.get('KMO', 0):.3f}")
            print(f"   - Max VIF:   {defense_stats.get('Max_VIF', 0):.2f}")
            print(f"   - Incr. Validity (Delta R2): {defense_stats.get('Delta_R2', 0):.3f} ({defense_stats.get('Delta_R2', 0)*100:.1f}%)")
            
        except Exception as e:
            print(f"⚠️ Error reading defense_stats.json: {e}")
    else:
        print("⚠️ defense_stats.json not found. Run reviewer_defense_v2.py first.")

    print("="*60)
    print("COPY THESE NUMBERS TO YOUR MANUSCRIPT AND ABSTRACT")
    print("="*60)

if __name__ == "__main__":
    main()
