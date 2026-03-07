import pandas as pd

try:
    df = pd.read_json("c:/Users/donke/Desktop/IKS_Work/Gunabased Survey/student-assessment/analysis/data/final_dataset_refined.json")
    if 'demographics' in df.columns:
        demog = pd.DataFrame(df['demographics'].tolist())
        print("Unique values in gitaFamiliarity:")
        print(demog['gitaFamiliarity'].unique())
        print("\nValue Counts:")
        print(demog['gitaFamiliarity'].value_counts(dropna=False))
    else:
        print("Demographics column not found.")
except Exception as e:
    print(f"Error: {e}")
