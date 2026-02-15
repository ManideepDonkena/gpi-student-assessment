import pandas as pd
import os

csv_file = "firebase_data.csv"

if not os.path.exists(csv_file):
    print("CSV file not found.")
    exit()

df = pd.read_csv(csv_file)

# Check if Feedback column exists
if "Feedback" not in df.columns:
    print("Feedback column missing from CSV.")
    exit()

# Filter for non-empty feedback
df['Feedback'] = df['Feedback'].astype(str)
feedback_df = df[df['Feedback'] != 'nan']
feedback_df = feedback_df[feedback_df['Feedback'].str.strip() != '']

print(f"\n--- User Feedback ({len(feedback_df)} entries) ---\n")

if feedback_df.empty:
    print("No feedback found in the dataset.")
else:
    for index, row in feedback_df.iterrows():
        print(f"User: {row['SessionID']} ({row.get('Timestamp', 'No Time')})")
        print(f"Dominant Guna: {row.get('Dominant_Guna', 'Unknown')}")
        print(f"Feedback: {row['Feedback']}")
        print("-" * 40)
