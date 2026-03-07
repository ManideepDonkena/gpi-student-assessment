import json

def calculate_tamas(responses):
    scores = []
    for q_id, val in responses.items():
        if q_id.startswith("T_"):
            scores.append(val)
    return sum(scores)/len(scores) if scores else 0

def search_raw():
    path = "original_gpi_dump.json"
    with open(path, "r") as f:
        data = json.load(f)
        
    print(f"Total Raw Sessions: {len(data)}")
    
    candidates = []
    
    for i, s in enumerate(data):
        demos = s.get('demographics', {})
        age = demos.get('age')
        gender = demos.get('gender')
        
        if gender == 'Male' and str(age) == '19':
            tamas = calculate_tamas(s.get('gunaResponses', {}))
            if tamas > 5.0:
                print(f"Raw Match at Index {i}: Tamas={tamas:.4f}, Age={age}")
                candidates.append((i, tamas))
                
    if not candidates:
        print("No candidates found in raw data.")

if __name__ == "__main__":
    search_raw()
