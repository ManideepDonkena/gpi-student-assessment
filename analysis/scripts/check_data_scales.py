import json
import pandas as pd
import numpy as np

def check_scales():
    with open("bfi44_cleaned.json", "r") as f:
        data = json.load(f)

    guna_vals = []
    bfi_vals = []

    for s in data:
        g = s.get('gunaResponses', {}).values()
        b = s.get('bigFiveResponses', {}).values()
        guna_vals.extend(g)
        bfi_vals.extend(b)

    g_series = pd.Series(guna_vals)
    b_series = pd.Series(bfi_vals)

    print("--- Data Scale Verification ---")
    print(f"Guna (SRT) Range: Min={g_series.min()}, Max={g_series.max()}")
    print(f"BFI Range:        Min={b_series.min()}, Max={b_series.max()}")
    
    print("\nDetailed Stats:")
    print(f"Guna Mean: {g_series.mean():.2f}, Std: {g_series.std():.2f}")
    print(f"BFI Mean:  {b_series.mean():.2f}, Std: {b_series.std():.2f}")

if __name__ == "__main__":
    check_scales()
