
import { studentGunaItems, bigFiveItems } from './items.js';

export function calculateScores(state) {
    const gunaResponses = state.gunaResponses; // { S1: 4, R1: 2, ... }
    const bigFiveResponses = state.bigFiveResponses; // { BF1: 3, ... }

    // --- 1. Calculate Guna Scores ---
    const scores = { sattva: 0, rajas: 0, tamas: 0 };
    const counts = { sattva: 0, rajas: 0, tamas: 0 };

    // We iterate through the defined items to ensure we catch all categories correctly
    studentGunaItems.forEach(item => {
        const val = gunaResponses[item.id];
        if (val) {
            scores[item.category] += parseInt(val);
            counts[item.category]++;
        }
    });

    // Raw Mean Scores
    const rawGuna = {
        Sattva: (scores.sattva / (counts.sattva || 1)).toFixed(2),
        Rajas: (scores.rajas / (counts.rajas || 1)).toFixed(2),
        Tamas: (scores.tamas / (counts.tamas || 1)).toFixed(2)
    };

    // Normalized Scores (sum = 1)
    const rawTotal = parseFloat(rawGuna.Sattva) + parseFloat(rawGuna.Rajas) + parseFloat(rawGuna.Tamas);
    const normGuna = {
        Sattva: (parseFloat(rawGuna.Sattva) / (rawTotal || 1)),
        Rajas: (parseFloat(rawGuna.Rajas) / (rawTotal || 1)),
        Tamas: (parseFloat(rawGuna.Tamas) / (rawTotal || 1))
    };

    // Dominant Guna
    const dominant = Object.entries(normGuna).sort((a, b) => b[1] - a[1])[0];
    const dominantName = dominant[0];

    // --- 2. Calculate Big Five Scores ---
    const bfScores = { extraversion: [], agreeableness: [], conscientiousness: [], neuroticism: [], openness: [] };

    bigFiveItems.forEach(item => {
        let val = parseInt(bigFiveResponses[item.id]);
        if (!val) return;

        // Reverse coding
        if (item.reverse) {
            val = 6 - val;
        }
        // Handle trait names (lowercase in items.js, maybe?)
        // items.js uses lowercase 'extraversion', but let's check.
        // Assuming trait names in items.js match keys in bfScores.
        if (bfScores[item.trait]) {
            bfScores[item.trait].push(val);
        }
    });

    const finalBigFive = {};
    for (const trait in bfScores) {
        const vals = bfScores[trait];
        const sum = vals.reduce((a, b) => a + b, 0);
        // Capitalize for output
        const key = trait.charAt(0).toUpperCase() + trait.slice(1);
        finalBigFive[key] = (sum / (vals.length || 1)).toFixed(1);
    }

    // Return structure matching what results.js expects
    return {
        gunaRaw: rawGuna,
        gunaNormalized: {
            Sattva: normGuna.Sattva.toFixed(3),
            Rajas: normGuna.Rajas.toFixed(3),
            Tamas: normGuna.Tamas.toFixed(3)
        },
        dominantGuna: dominantName,
        bigFive: finalBigFive
    };
}
