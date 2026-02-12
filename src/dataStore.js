
export const store = {
    state: {
        view: 'intro', // intro, demographics, guna-likert, bigfive-likert, scenario, results
        sessionId: crypto.randomUUID(),
        startTime: new Date().toISOString(),
        demographics: {},

        // Guna Likert Section
        gunaItems: [],
        gunaResponses: {},
        gunaMetadata: { timeMs: 0, cursorDistancePx: 0, answerChanges: 0 },

        // Big Five Section
        bigFiveItems: [],
        bigFiveResponses: {},
        bigFiveMetadata: { timeMs: 0, cursorDistancePx: 0, answerChanges: 0 },

        // Scenario Section
        scenarios: [],
        currentScenarioIndex: 0,
        scenarioResponses: []
        // Scenario metadata is stored per-response in logScenarioResponse
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
    store.state.view = 'guna-likert';
}

export function submitGunaResponses(responses, metadata) {
    store.state.gunaResponses = responses;
    store.state.gunaMetadata = metadata;
    store.state.view = 'bigfive-likert';
}

export function submitBigFiveResponses(responses, metadata) {
    store.state.bigFiveResponses = responses;
    store.state.bigFiveMetadata = metadata;
    store.state.view = 'scenario';
}

export function logScenarioResponse(response) {
    store.state.scenarioResponses.push(response);

    if (store.state.currentScenarioIndex < store.state.scenarios.length - 1) {
        store.state.currentScenarioIndex++;
    } else {
        store.state.endTime = new Date().toISOString();

        // Auto-save to Firebase
        import('./firebase.js').then(module => {
            module.saveSessionData(store.state).then(id => {
                console.log("Session saved to Firebase:", id);
                store.state.firebaseId = id; // Store ID to show to user if needed
            }).catch(err => console.error("Firebase save failed", err));
        });

        store.state.view = 'results';
    }
}

export function exportSessionData() {
    return JSON.stringify(store.state, null, 2);
}
