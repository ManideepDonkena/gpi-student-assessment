
// REFINED PROXY QUESTIONNAIRE (58 Items)
// Based on "Proxy GPI Questionnaire" derived from Purified Factor Analysis

export const studentGunaItems = [
    // --- SATTVA (Purity & Balance) ---
    { id: "S1", text: "When given a choice at a buffet, how often do you naturally gravitate towards fresh fruits and salads over heavy or spicy dishes?", category: "sattva" },
    { id: "S2", text: "When you look at an animal or another person, to what extent do you feel a deep, underlying connection or shared 'life force' with them?", category: "sattva" },
    { id: "S3", text: "If an elderly family member gives you advice that contradicts your own plans, how likely are you to listen respectfully and seriously consider their perspective?", category: "sattva" },
    { id: "S4", text: "In a heated argument, how much effort do you make to keep your tone calm and avoid using harsh words?", category: "sattva" },
    { id: "S5", text: "If a cashier gives you too much change, how likely are you to immediately point out the mistake and return the money?", category: "sattva" },
    { id: "S6", text: "How much time per week do you spend voluntarily learning something new (reading, watching documentaries) just for the sake of understanding?", category: "sattva" },
    { id: "S7", text: "When facing a difficult decision where you could gain personally by bending the rules, how often do you stop to ask yourself 'Is this the right thing to do?'", category: "sattva" },
    { id: "S8", text: "Imagine you made a mistake at work/school that no one else noticed. How likely are you to admit it voluntarily?", category: "sattva" },
    { id: "S9", text: "If you promise to help a friend move house, but wake up feeling tired and lazy, how likely are you to go anyway simply because you gave your word?", category: "sattva" },
    { id: "S10", text: "Think about a time when you had nothing to do and no entertainment. How comfortable/happy were you just 'being' with yourself?", category: "sattva" },
    { id: "S11", text: "How often do you treat the campus janitor/security guard with the exact same respect and patience as you do your Professor or Dean?", category: "sattva" },
    { id: "S12", text: "If you are working on a project that looks like it will fail, do you continue to put in your best effort until the very end?", category: "sattva" },
    { id: "S13", text: "Before taking action, how often do you consult higher ethical or moral principles?", category: "sattva" },
    { id: "S14", text: "How often do you feel that 'self-realization' or 'spiritual growth' is irrelevant to your real-life goals?", category: "sattva", reverse: true },

    // --- RAJAS (Passion & Activity) ---
    { id: "R1", text: "If taking a shortcut (like skipping a queue or bending a regulation) would guarantee you a major win, how likely are you to take it?", category: "rajas" },
    { id: "R2", text: "If a friend invites you to a lecture on philosophy or spirituality, how likely are you to decline because you find it 'boring' or 'useless'?", category: "rajas" },
    { id: "R3", text: "When solving a problem, do you prefer to rely entirely on your own logic/modern methods rather than looking at how things were traditionally done?", category: "rajas" },
    { id: "R4", text: "How often do you check your social media likes or exam grades and feel a sudden rush of pride or superiority?", category: "rajas" },
    { id: "R5", text: "Who do you follow/discuss more: Rich influencers & celebrities vs. Scientists & Social Workers?", category: "rajas" },
    { id: "R6", text: "To what extent do you live your life with the assumption that this physical existence is the only reality that matters?", category: "rajas" },
    { id: "R7", text: "When you achieve a goal, how long does the 'high' last before you start looking for the next big thing?", category: "rajas" },
    { id: "R8", text: "How much do you crave spicy, salty, or very rich foods (like fried snacks or heavy desserts) compared to plain, simple meals?", category: "rajas" },
    { id: "R9", text: "If you lost your phone or favorite watch today, how strictly would it affect your mood and sense of self-worth for the next week?", category: "rajas" },
    { id: "R10", text: "Given a free Friday night, would you rather go to a busy club/party or take a quiet walk in nature?", category: "rajas" },
    { id: "R11", text: "How much of your daily mental energy is spent thinking about or pursuing romantic/sexual gratification?", category: "rajas" },
    { id: "R12", text: "When looking at a buffet or a sale, do you often take more than you actually need, just because it's available?", category: "rajas" },
    { id: "R13", text: "If someone asks for a donation, do you feel annoyed or resentful, even if you eventually give a small amount?", category: "rajas" },
    { id: "R14", text: "After buying something you really wanted, how quickly do you start wanting a better version of it?", category: "rajas" },
    { id: "R15", text: "How often do you feel you could be genuinely happy living in a simple house without luxury items?", category: "rajas", reverse: true },
    { id: "R16", text: "How frequently do you prioritize physical enjoyment (like food, comfort, or sex) over your other responsibilities?", category: "rajas" },


    // --- TAMAS (Inertia & Ignorance) ---
    { id: "T1", text: "When things go wrong in your life, how often do you feel that it was completely someone else's fault at 'the world is against you'?", category: "tamas" },
    { id: "T2", text: "How often do you do something impulsive (like staying up late or skipping work) and regret it the next morning?", category: "tamas" },
    { id: "T3", text: "On a typical day, what percentage of the time do you feel a general sense of 'blah' or dissatisfaction for no specific reason?", category: "tamas" },
    { id: "T4", text: "In your head or with friends, how often do you find yourself making fun of or judging strangers/acquaintances?", category: "tamas" },
    { id: "T5", text: "How often do you struggle to get out of bed because the day ahead feels pointless or too heavy?", category: "tamas" },
    { id: "T6", text: "If you have a deadline in 3 days, do you start now, or wait until the night before (even if it stresses you out)?", category: "tamas" },
    { id: "T7", text: "When faced with a complex problem, is your first instinct to try and solve it, or to freeze and wait for someone else to help?", category: "tamas" },
    { id: "T8", text: "Do you frequently look at your life and feel 'stuck' or like you are 'falling behind' everyone else?", category: "tamas" },
    { id: "T9", text: "If a gym workout or a study session gets difficult, how likely are you to quit early and tell yourself 'I'll do it tomorrow'?", category: "tamas" },
    { id: "T10", text: "If you miss a bus or drop your coffee, does it ruin your entire morning?", category: "tamas" },
    { id: "T11", text: "How many times a week do you feel a flash of rage (at traffic, people, or technology)?", category: "tamas" },
    { id: "T12", text: "How many New Year's resolutions or self-improvement plans have you started and dropped within 2 weeks?", category: "tamas" },
    { id: "T13", text: "Do you often feel a vague sense of dread or anxiety about the future without knowing exactly why?", category: "tamas" },
    { id: "T14", text: "Do your moods swing wildly during the day (e.g., fine one minute, crying/angry the next)?", category: "tamas" },
    { id: "T15", text: "Do you feel like you are always the one giving in relationships while others just take from you?", category: "tamas" },
    { id: "T16", text: "How often do you feel 'down in the dumps' or 'low energy' even when nothing bad has happened?", category: "tamas" },
    { id: "T17", text: "Do you often 'forget' or avoid doing chores/errands that your family asked you to do?", category: "tamas" },
    { id: "T18", text: "When you talk to friends, how much of the conversation is you complaining about your problems vs. discussing ideas?", category: "tamas" },
    { id: "T19", text: "When a friend succeeds (gets a job/promotion), is your first feeling happiness for them, or a pang of 'Why not me?'", category: "tamas" },
    { id: "T20", text: "On Sunday evening, do you feel a knot in your stomach thinking about work/school on Monday?", category: "tamas" },
    { id: "T21", text: "If you could get away with not paying a bus fare or sneaking into a movie, would you do it?", category: "tamas" },
    { id: "T22", text: "If there is a box of cookies in front of you and you decided not to eat one, how long can you resist before giving in?", category: "tamas" },
    { id: "T23", text: "How often do you find yourself wishing you could escape to a quiet village rather than living in the busy city?", category: "tamas" },
    { id: "T24", text: "How often do you feel controlled by a physical or psychological habit/addiction that you can't break?", category: "tamas" },
    { id: "T25", text: "I often feel mentally unbalanced", category: "tamas" },
    { id: "T26", text: "I often neglect my responsibilities to my friends", category: "tamas" },
    { id: "T27", text: "I often act violently towards others", category: "tamas" }
];

export const bigFiveItems = [
    // BFI-10 Items (Rammstedt & John, 2007)
    // Scale: 1 (Disagree strong) to 5 (Agree strong)
    { id: "BF1", text: "I see myself as someone who is reserved.", trait: "extraversion", reverse: true },
    { id: "BF2", text: "I see myself as someone who is generally trusting.", trait: "agreeableness", reverse: false },
    { id: "BF3", text: "I see myself as someone who tends to be lazy.", trait: "conscientiousness", reverse: true },
    { id: "BF4", text: "I see myself as someone who is relaxed, handles stress well.", trait: "neuroticism", reverse: true },
    { id: "BF5", text: "I see myself as someone who has few artistic interests.", trait: "openness", reverse: true },
    { id: "BF6", text: "I see myself as someone who is outgoing, sociable.", trait: "extraversion", reverse: false },
    { id: "BF7", text: "I see myself as someone who tends to find fault with others.", trait: "agreeableness", reverse: true },
    { id: "BF8", text: "I see myself as someone who does a thorough job.", trait: "conscientiousness", reverse: false },
    { id: "BF9", text: "I see myself as someone who gets nervous easily.", trait: "neuroticism", reverse: false },
    { id: "BF10", text: "I see myself as someone who has an active imagination.", trait: "openness", reverse: false }
];
