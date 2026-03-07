import json
import os
import pandas as pd
from dateutil import parser

# --- PATH CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ANALYSIS_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(ANALYSIS_DIR, "data")
json_file = os.path.join(DATA_DIR, "original_gpi_dump.json")

if not os.path.exists(json_file):
    print(f"Error: {json_file} not found.")
    exit()

print(f"Loading {json_file}...")
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total sessions: {len(data)}")

feedback_list = []

for session in data:
    feedback = session.get('feedback')
    
    # Store even if empty for debug
    entry = {
        'Timestamp': session.get('uploadedAt'),
        'SessionID': session.get('sessionId'),
        'FirebaseID': session.get('firebase_id', 'N/A'),
        'Feedback': feedback
    }
    
    # Check if feedback is meaningful
    if feedback and str(feedback).strip().lower() not in ['none', 'null', 'nan', 'undefined', '']:
        feedback_list.append(entry)

# Convert to DF for nice printing
df = pd.DataFrame(feedback_list)

if df.empty:
    print("\n--- No valid feedback found in JSON dump ---")
else:
    # Sort by time
    def parse_ts(x):
        try:
             return parser.parse(x) if x else pd.Timestamp.min
        except:
             return pd.Timestamp.min
             
    df['ParsedTime'] = df['Timestamp'].apply(parse_ts)
    df = df.sort_values('ParsedTime', ascending=False)
    
    print(f"\n--- Found {len(df)} Feedback Entries ---")
    for _, row in df.iterrows():
        print(f"Time: {row['Timestamp']}")
        print(f"User: {row['SessionID']}") 
        print(f"Msg : {row['Feedback']}")
        print("-" * 40)
