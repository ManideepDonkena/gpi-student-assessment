"""
=============================================================
MASTER PIPELINE: Guna Personality Inventory Analysis
=============================================================
Runs ALL analysis phases in sequence:
  Step 0: Fetch data from Firebase (optional, if --fetch)
  Step 1: Clean & filter data
  Step 2: Phase 1 — Descriptive Statistics & Normality
  Step 3: Phase 2 — Reliability Analysis (Cronbach's Alpha)
  Step 4: Phase 3 — Correlation Analysis (Convergent Validity)
  Step 5: Phase 4 — Joint Factor Analysis (EFA)
  Step 6: Phase 5 — Item Refinement
  Step 7: Phase 6 — Demographics
  Step 8: Phase 7 — Scenario Validation (Criterion Validity)
  Step 9: Phase 8 — Incremental Validity
  Step 10: Phase 9 — Reviewer Defense (Implicit Variables)

Usage:
  python run_full_pipeline.py           # Run analysis only
  python run_full_pipeline.py --fetch   # Fetch new data first, then analyze
=============================================================
"""
import subprocess
import sys
import os
import time
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ANALYSIS_DIR = os.path.dirname(SCRIPT_DIR)

# ─── STEP DEFINITIONS ────────────────────────────────────
FETCH_STEP = ("Step 0: Fetch Data from Firebase", "fetch_original_data.py")

ANALYSIS_STEPS = [
    ("Step 1:  Clean & Filter Data",         "clean_and_analyze.py"),
    ("Step 2:  Phase 1 — Descriptives",      "deep_analysis_phase1.py"),
    ("Step 3:  Phase 2 — Reliability",       "analyze_cronbach.py"),
    ("Step 4:  Phase 3 — Correlations",      "deep_analysis_phase3.py"),
    ("Step 5:  Phase 4 — Factor Analysis",   "deep_analysis_phase4.py"),
    ("Step 6:  Phase 5 — Item Refinement",   "analyze_item_refinement.py"),
    ("Step 7:  Phase 6 — Demographics",      "deep_analysis_phase6.py"),
    ("Step 8:  Phase 7 — Scenario Valid.",    "deep_analysis_phase7.py"),
    ("Step 9:  Phase 8 — Incr. Validity",    "deep_analysis_phase8.py"),
    ("Step 10: Phase 9 — Reviewer Defense",  "deep_analysis_phase9.py"),
]


def run_step(step_name, script_name):
    script_path = os.path.join(SCRIPT_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"  ❌ SKIPPED: {script_name} not found")
        return False
    
    print(f"\n{'='*60}")
    print(f"  {step_name}")
    print(f"  Running: {script_name}")
    print(f"{'='*60}")
    
    start = time.time()
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=SCRIPT_DIR,
        capture_output=True, text=True
    )
    elapsed = time.time() - start
    
    # Print stdout
    if result.stdout:
        for line in result.stdout.strip().split('\n'):
            print(f"  {line}")
    
    if result.returncode != 0:
        print(f"  ❌ FAILED (exit code {result.returncode})")
        if result.stderr:
            for line in result.stderr.strip().split('\n')[-5:]:
                print(f"  ERROR: {line}")
        return False
    
    print(f"  ✅ Complete ({elapsed:.1f}s)")
    return True


def main():
    parser = argparse.ArgumentParser(description="GPI Analysis Pipeline")
    parser.add_argument("--fetch", action="store_true",
                        help="Fetch fresh data from Firebase before running analysis")
    parser.add_argument("--from-step", type=int, default=0,
                        help="Start from a specific step number (0=fetch, 1=clean, etc.)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("  GPI ANALYSIS PIPELINE")
    print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Fetch new data: {'Yes' if args.fetch else 'No'}")
    print(f"  Starting from: Step {args.from_step}")
    print("=" * 60)
    
    results = {}
    
    # Step 0: Data fetch (optional)
    if args.fetch and args.from_step <= 0:
        step_name, script_name = FETCH_STEP
        success = run_step(step_name, script_name)
        results[step_name] = "✅" if success else "❌"
        if not success:
            print("\n  ⚠️  Data fetch failed. Continuing with existing data...")
    
    # Analysis steps
    for i, (step_name, script_name) in enumerate(ANALYSIS_STEPS, start=1):
        if i < args.from_step:
            results[step_name] = "⏭️ Skipped"
            continue
        success = run_step(step_name, script_name)
        results[step_name] = "✅" if success else "❌"
    
    # ─── SUMMARY ──────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  PIPELINE SUMMARY")
    print(f"{'='*60}")
    for step, status in results.items():
        print(f"  {status} {step}")
    
    # List generated reports
    reports_dir = os.path.join(ANALYSIS_DIR, "reports")
    if os.path.exists(reports_dir):
        print(f"\n  📄 Generated Reports:")
        for f in sorted(os.listdir(reports_dir)):
            if f.endswith('.md'):
                size = os.path.getsize(os.path.join(reports_dir, f))
                print(f"    {f} ({size//1024}KB)")
    
    images_dir = os.path.join(ANALYSIS_DIR, "images")
    if os.path.exists(images_dir):
        print(f"\n  🖼️  Generated Images:")
        for f in sorted(os.listdir(images_dir)):
            if f.endswith('.png'):
                print(f"    {f}")
    
    # Data files
    data_dir = os.path.join(ANALYSIS_DIR, "data")
    if os.path.exists(data_dir):
        print(f"\n  💾 Data Files:")
        for f in sorted(os.listdir(data_dir)):
            if f.endswith(('.json', '.csv')):
                size = os.path.getsize(os.path.join(data_dir, f))
                print(f"    {f} ({size//1024}KB)")


if __name__ == "__main__":
    main()
