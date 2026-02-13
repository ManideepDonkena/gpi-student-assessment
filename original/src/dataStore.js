
const STORAGE_KEY = 'gpi_original_session_v1';

export const store = {
    state: {
        view: 'intro', // intro, demographics, guna-likert, bigfive-likert, scenario, results
        sessionId: crypto.randomUUID(),
        startTime: new Date().toISOString(),
        viewTimings: {}, // Track time spent on each view
        demographics: {},

        // Guna Likert Section
        gunaItems: [],
        gunaItems: [],
        gunaResponses: {},
        gunaDetails: {}, // Stores text + timestamp per question
        gunaMetadata: { timeMs: 0, cursorDistancePx: 0, answerChanges: 0 },

        // Big Five Section
        bigFiveItems: [],
        bigFiveItems: [],
        bigFiveResponses: {},
        bigFiveDetails: {},
        bigFiveMetadata: { timeMs: 0, cursorDistancePx: 0, answerChanges: 0 },

        // Scenario Section
        scenarios: [],
        currentScenarioIndex: 0,
        scenarioResponses: [],
        // Scenario metadata is stored per-response in logScenarioResponse
        version: 'original-gpi' // Tag for filtering data later
    }
};

export async function initStore() {
    try {
        const { studentGunaItems, bigFiveItems } = await import('./items.js');
        store.state.gunaItems = studentGunaItems;
        store.state.bigFiveItems = bigFiveItems;

        // Try to fetch scenarios, handle GitHub Pages structure
        try {
            const response = await fetch('./src/scenarios.json');
            if (!response.ok) throw new Error("404 Not Found");
            const allScenarios = await response.json();
            store.state.scenarios = allScenarios.slice(0, 5);
        } catch (fetchErr) {
            console.warn("Fetch failed, using mock scenarios", fetchErr);
            throw fetchErr; // Trigger catch block below for fallback
        }

        // Check for saved session
        restoreSession();

    } catch (e) {
        console.error("Failed to load items/scenarios", e);
        // Fallback Scenarios to prevent crash
        store.state.scenarios = [
            {
                id: "fallback_1",
                text: "You find a wallet on the ground with cash inside. No ID. What do you do?",
                options: [
                    { text: "Turn it in to the nearest authority.", guna: "sattva" },
                    { text: "Keep the cash but leave the wallet.", guna: "rajas" },
                    { text: "Walk past it. Not your problem.", guna: "tamas" }
                ]
            }
        ];
    }
}

export function getStore() {
    return store;
}

export function setDemographics(data) {
    store.state.demographics = data;
    store.state.view = 'reflection';
    saveSession();
}

export function logViewDuration(viewName, durationMs) {
    if (!store.state.viewTimings[viewName]) {
        store.state.viewTimings[viewName] = 0;
    }
    store.state.viewTimings[viewName] += durationMs;
}

export function submitGunaResponses(responses, metadata, details) {
    store.state.gunaResponses = responses;
    store.state.gunaMetadata = metadata;
    store.state.gunaDetails = details || {};
    store.state.view = 'bigfive-likert';
    saveSession();
}

export function updateGunaResponse(id, value, detailed) {
    store.state.gunaResponses[id] = value;
    if (detailed) {
        store.state.gunaDetails[id] = detailed;
    }
    saveSession();
}

export function submitBigFiveResponses(responses, metadata, details) {
    store.state.bigFiveResponses = responses;
    store.state.bigFiveMetadata = metadata;
    store.state.bigFiveDetails = details || {};
    store.state.bigFiveDetails = details || {};
    store.state.view = 'scenario';
    saveSession();
}

export function updateBigFiveResponse(id, value, detailed) {
    store.state.bigFiveResponses[id] = value;
    if (detailed) {
        store.state.bigFiveDetails[id] = detailed;
    }
    saveSession();
}

export function logScenarioResponse(response) {
    store.state.scenarioResponses.push(response);

    if (store.state.currentScenarioIndex < store.state.scenarios.length - 1) {
        store.state.currentScenarioIndex++;
    } else {
        store.state.endTime = new Date().toISOString();

        // Auto-save to Firebase
        // We compute scores first so they are saved in the DB
        import('./scoring.js').then(scoring => {
            store.state.computedScores = scoring.calculateScores(store.state);

            import('./firebase.js').then(module => {
                module.saveSessionData(store.state).then(id => {
                    console.log("Session saved to Firebase:", id);
                    store.state.firebaseId = id; // Store ID to show to user if needed
                }).catch(err => console.error("Firebase save failed", err));
            });
        });

        store.state.view = 'results';
    }
}

export function exportSessionData() {
    return JSON.stringify(store.state, null, 2);
}

// --- Persistence Logic ---
function saveSession() {
    try {
        const s = store.state;
        const dataToSave = {
            view: s.view,
            sessionId: s.sessionId,
            startTime: s.startTime,
            demographics: s.demographics,
            viewTimings: s.viewTimings,
            gunaResponses: s.gunaResponses,
            gunaDetails: s.gunaDetails,
            gunaMetadata: s.gunaMetadata,
            bigFiveResponses: s.bigFiveResponses,
            bigFiveDetails: s.bigFiveDetails,
            bigFiveMetadata: s.bigFiveMetadata,
            scenarioResponses: s.scenarioResponses,
            computedScores: s.computedScores,
            firebaseId: s.firebaseId
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(dataToSave));
    } catch (e) {
        console.warn("LocalStorage save failed", e);
    }
}

function restoreSession() {
    try {
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved) {
            const data = JSON.parse(saved);
            if (data.sessionId) {
                console.log("Restoring session:", data.sessionId);
                Object.assign(store.state, data);
            }
        }
    } catch (e) {
        console.warn("LocalStorage restore failed", e);
    }
}
