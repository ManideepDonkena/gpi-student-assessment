
import re
import json

# User provided text
user_text = """I prefer to live in the village rather than the city		I often feel like a victim		I am willing to break the rules to achieve my goals		I have very little interest in spiritual understanding		I am satisfied with my life		Fruits and vegetables are among my favorite foods		All living entities are essentially spiritual		 In conducting my activities, I do not consider traditional wisdom		I often act without considering the consequences of my actions		I usually feel discontented with life		I become happy when I think about the material assets I possess		 I am not very much affected by the joys and sorrows of life		I often criticize and insult other people		I am against violence		I am good at using willpower to achieve goals		I enjoy spending time in bars		Cleanliness is very important to me		Spiritual advancement is very important for me		Others say that my intelligence is very sharp		I am a very active person		I often feel depressed.		I often put off or delay my responsibilities.		Respecting ones elders is very important		I greatly admire materially successful people		When I speak, I really try not to irritate others		I believe life is over when the body dies		 I often feel helpless		I become elated when things work out well for me		I enjoy foods with strong tastes		I am constantly dissatisfied with my position in life		Having possessions is very important to me		When things are tough, I often bail out		 I am straightforward in my dealings with other people		I have more energy than most people		 I feel that my knowledge is always increasing		People should not have sex unless they are married and want children		I prefer city night life to a walk in the forest		For me, sex life is a major source of happiness		 I take guidance from higher ethical and moral laws before I act		 I enjoy intoxicating substances (including coffee, cigarettes and alcohol)		Being truthful is extremely important		I feel proud when I give charity		I often feel greedy		I become greatly distressed when things don`t work out for me		I am often angry		 I do not have strong determination		 I often feel fearful		 I greatly enjoy sleeping		 I do not have doubts about my responsibilities in life		 I often sacrifice my pleasure to please God		 I often feel emotionally unbalanced		 I enjoy eating meat		 I often study books of traditional wisdom		 I am self-controlled		 I am very dutiful		 When I give charity, I often do it grudgingly		 I am generally even-tempered		 In my life I usually experience deep happiness that is not dependent on anything external		 Spiritually, all living entities are equal		 I often get exploited in my relationships		 Self-realization is not important for me		 I often feel dejected		 I carry out my responsibilities regardless of whether there is success or failure		 I often neglect my responsibilities to my family		 I am easily affected by the joys and sorrows of life		 I often whine		 Regardless of what I acquire or achieve, I have an uncontrollable desire to obtain more		 I am currently struggling with an addiction, physical or psychological, to some type of intoxicant (including caffeine, cigarettes and alcohol)		 My determination is unbreakable		 I often envy others		 My job is a source of anxiety		 I never think about giving up my wealth and position for a simpler life		 It often happens that those things that brought me happiness later become the source of my suffering		 I sometimes cheat people		 The most important thing to know is how to increase one`s enjoyment of physical pleasures, like sex and eating		 I often feel mentally unbalanced		 I don`t have much will power		 I often neglect my responsibilities to my friends		 I often act violently towards others		 I am good at controlling my senses and emotions"""

# Questions.md mapping (reconstructed from file content)
# Format: {QuestionText: {Category, ID}}
db = {}

# SATTVA
sattva_qs = [
("J","I prefer to live in the village rather than the city"),
("R","I am satisfied with my life"),
("T","Fruits and vegetables are among my favorite foods"),
("V","All living entities are essentially spiritual"),
("AF","I am not very much affected by the joys and sorrows of life"),
("AJ","I am against violence"),
("AP","Cleanliness is very important to me"),
("AR","Spiritual advancement is very important for me"),
("AT","Others say that my intelligence is very sharp"),
("BB","Respecting ones elders is very important"),
("BF","When I speak, I really try not to irritate others"),
("BV","I am straightforward in my dealings with other people"),
("BZ","I feel that my knowledge is always increasing"),
("CB","People should not have sex unless they are married and want children"),
("CH","I take guidance from higher ethical and moral laws before I act"),
("CL","Being truthful is extremely important"),
("DB","I do not have doubts about my responsibilities in life"),
("DD","I often sacrifice my pleasure to please God"),
("DJ","I often study books of traditional wisdom"),
("DN","I am very dutiful"),
("DL","I am self-controlled"),
("DR","I am generally even-tempered"),
("DT","In my life I usually experience deep happiness that is not dependent on anything external"),
("DV","Spiritually, all living entities are equal"),
("ED","I carry out my responsibilities regardless of whether there is success or failure"),
("EP","My determination is unbreakable"),
("FL","I am good at controlling my senses and emotions")
]
for k,v in sattva_qs: db[v.strip().lower()] = {'id': k, 'cat': 'sattva'}

# RAJAS
rajas_qs = [
("N","I am willing to break the rules to achieve my goals"),
("AB","I usually feel discontented with life"),
("AD","I become happy when I think about the material assets I possess"),
("AL","I am good at using willpower to achieve goals"),
("AV","I am a very active person"),
("BD","I greatly admire materially successful people"),
("BH","I believe life is over when the body dies"),
("BL","I become elated when things work out well for me"),
("BN","I enjoy foods with strong tastes"),
("BP","I am constantly dissatisfied with my position in life"),
("BR","Having possessions is very important to me"),
("BT","When things are tough, I often bail out"),
("BX","I have more energy than most people"),
("CD","I prefer city night life to a walk in the forest"),
("CF","For me, sex life is a major source of happiness"),
("CN","I feel proud when I give charity"),
("CP","I often feel greedy"),
("CR","I become greatly distressed when things don`t work out for me"),
("DP","When I give charity, I often do it grudgingly"),
("EH","I am easily affected by the joys and sorrows of life"),
("EL","Regardless of what I acquire or achieve, I have an uncontrollable desire to obtain more"),
("ER","I often envy others"),
("ET","My job is a source of anxiety"),
("EV","I never think about giving up my wealth and position for a simpler life"),
("EX","It often happens that those things that brought me happiness later become the source of my suffering")
]
for k,v in rajas_qs: db[v.strip().lower()] = {'id': k, 'cat': 'rajas'}

# TAMAS
tamas_qs = [
("L","I often feel like a victim"),
("P","I have very little interest in spiritual understanding"),
("X","In conducting my activities, I do not consider traditional wisdom"),
("Z","I often act without considering the consequences of my actions"),
("AH","I often criticize and insult other people"),
("AN","I enjoy spending time in bars"),
("AX","I often feel depressed."),
("AZ","I often put off or delay my responsibilities."),
("BJ","I often feel helpless"),
("CJ","I enjoy intoxicating substances (including coffee, cigarettes and alcohol)"),
("CV","I do not have strong determination"),
("CX","I often feel fearful"),
("CZ","I greatly enjoy sleeping"),
("DF","I often feel emotionally unbalanced"),
("DH","I enjoy eating meat"),
("DX","I often get exploited in my relationships"),
("DZ","Self-realization is not important for me"),
("EB","I often feel dejected"),
("EF","I often neglect my responsibilities to my family"),
("EJ","I often whine"),
("EN","I am currently struggling with an addiction, physical or psychological, to some type of intoxicant (including caffeine, cigarettes and alcohol)"),
("EZ","I sometimes cheat people"),
("FB","The most important thing to know is how to increase one`s enjoyment of physical pleasures, like sex and eating"),
("FD","I often feel mentally unbalanced"),
("FF","I don`t have much will power"),
("FH","I often neglect my responsibilities to my friends"),
("FJ","I often act violently towards others")
]
for k,v in tamas_qs: db[v.strip().lower()] = {'id': k, 'cat': 'tamas'}

# Clean up db keys removing quotes/apostrophes variations
normalized_db = {}
for k,v in db.items():
    clean_k = re.sub(r'[`\'\u2019]', '', k).strip()
    normalized_db[clean_k] = v

# Parse user input
items = [x.strip() for x in re.split(r'\t+', user_text) if x.strip()]

found_count = 0
missing = []
valid_items = []

print(f'Total items provided: {len(items)}')

for i, item in enumerate(items):
    clean_item = re.sub(r'[`\'\u2019]', '', item.lower()).strip()
    
    # Check if exact match exists
    found_data = normalized_db.get(clean_item)
    
    if not found_data:
        # Check stripping trailing period
        if clean_item.endswith('.'):
             found_data = normalized_db.get(clean_item[:-1])
    
    if found_data:
        found_count += 1
        valid_items.append({
            'id': found_data['id'],
            'text': item,
            'category': found_data['cat'],
            'domain': 'general' # Default domain
        })
    else:
        missing.append(item)

print(f'Matched: {found_count}')
print(f'Missing: {len(missing)}')
for m in missing:
    print(f'MISSING: {m}')

# Output valid items as JSON for easy copy-paste
# print(json.dumps(valid_items, indent=4))
