
import json
import random
import os

OUTPUT_DIR = "dummy_students"
NUM_STUDENTS = 200

# BFI-10 Item Map (Trait, Reverse?)
BFI_MAP = {
    "BF1": ("extraversion", True),
    "BF2": ("agreeableness", False),
    "BF3": ("conscientiousness", True),
    "BF4": ("neuroticism", True),
    "BF5": ("openness", True),
    "BF6": ("extraversion", False),
    "BF7": ("agreeableness", True),
    "BF8": ("conscientiousness", False),
    "BF9": ("neuroticism", False),
    "BF10": ("openness", False)
}

def generate_student():
    student_id = f"stu_{random.randint(10000, 99999)}"
    
    # 1. Generate Latent Traits (Correlated)
    dom_guna = random.choice(['sattva', 'rajas', 'tamas'])
    
    if dom_guna == 'sattva':
        l_sattva = random.uniform(0.6, 0.9)
        l_rajas = random.uniform(0.1, 0.5)
        l_tamas = random.uniform(0.1, 0.4)
    elif dom_guna == 'rajas':
        l_sattva = random.uniform(0.1, 0.6)
        l_rajas = random.uniform(0.6, 0.9)
        l_tamas = random.uniform(0.1, 0.5)
    else: # tamas
        l_sattva = random.uniform(0.1, 0.4)
        l_rajas = random.uniform(0.1, 0.5)
        l_tamas = random.uniform(0.6, 0.9)
        
    # Generate Big Five latents based on Gunas
    l_consc = 0.5 * l_sattva - 0.4 * l_tamas + random.gauss(0, 0.1)
    l_agree = 0.4 * l_sattva + random.gauss(0, 0.1)
    l_neuro = 0.4 * l_rajas + 0.3 * l_tamas - 0.3 * l_sattva + random.gauss(0, 0.1)
    l_extra = 0.5 * l_rajas + random.gauss(0, 0.1)
    l_open = 0.3 * l_sattva - 0.3 * l_tamas + random.gauss(0, 0.1)
    
    # helper
    def to_likert(val, reverse=False):
        val = max(0, min(1, val))
        if reverse: val = 1 - val
        score = int(1 + val * 4 + 0.5)
        return max(1, min(5, score))

    # 2. Generate Item Responses
    guna_resps = {}
    for i in range(1, 16):
        guna_resps[f"S{i}"] = to_likert(l_sattva + random.gauss(0, 0.15))
        guna_resps[f"R{i}"] = to_likert(l_rajas + random.gauss(0, 0.15))
        guna_resps[f"T{i}"] = to_likert(l_tamas + random.gauss(0, 0.15))
        
    bf_resps = {}
    for i in range(1, 11):
        iid = f"BF{i}"
        trait, reverse = BFI_MAP[iid]
        if trait == "extraversion": latent = l_extra
        elif trait == "agreeableness": latent = l_agree
        elif trait == "conscientiousness": latent = l_consc
        elif trait == "neuroticism": latent = l_neuro
        elif trait == "openness": latent = l_open
        
        bf_resps[iid] = to_likert(latent, reverse)
        
    # 3. Simulate Behavioral Metadata
    # Hypotheses:
    # Rajas -> High activity (cursor), fast time (impulsive), high changes (restless)
    # Tamas -> Low activity, slow time (lethargic), low changes (passive)
    # Sattva -> Moderate/High activity (engaged), moderate time (thoughtful)
    
    # Base values
    base_time = 60000 # 60s
    base_dist = 5000  # 5000px
    base_changes = 2
    
    # Modifiers
    time_mod = 1.0 + (l_tamas * 0.5) - (l_rajas * 0.3)  # Tamas slows down, Rajas speeds up
    dist_mod = 1.0 + (l_rajas * 0.6) - (l_tamas * 0.4)  # Rajas moves more, Tamas moves less
    change_mod = 1.0 + (l_rajas * 0.5) + (l_sattva * 0.2) # Rajas changes often (unsure/restless), Sattva (refining)
    
    # Add randomness
    time_taken = int(base_time * time_mod * random.uniform(0.8, 1.2))
    cursor_dist = int(base_dist * dist_mod * random.uniform(0.8, 1.2))
    ans_changes = int(base_changes * change_mod * random.uniform(0, 1.5))
    
    # Store in both sections (splitting arbitrarily for simulation)
    guna_meta = { "timeMs": int(time_taken*0.6), "cursorDistancePx": int(cursor_dist*0.6), "answerChanges": int(ans_changes*0.6) }
    bf_meta = { "timeMs": int(time_taken*0.4), "cursorDistancePx": int(cursor_dist*0.4), "answerChanges": int(ans_changes*0.4) }
        
    return {
        "sessionId": student_id,
        "demographics": {"year": str(random.randint(1,4)), "gpa": round(random.uniform(6.0, 9.5), 1)},
        "gunaResponses": guna_resps,
        "gunaMetadata": guna_meta,
        "bigFiveResponses": bf_resps,
        "bigFiveMetadata": bf_meta
    }

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"Generating {NUM_STUDENTS} dummy student sessions...")
    for _ in range(NUM_STUDENTS):
        data = generate_student()
        with open(f"{OUTPUT_DIR}/{data['sessionId']}.json", 'w') as f:
            json.dump(data, f, indent=2)
            
    print(f"Done. Saved to {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
