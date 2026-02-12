
import { initStore, getStore } from './dataStore.js';
import { renderDemographics } from './demographics.js';
import { renderLikertSection } from './likertRenderer.js';
import { renderScenario } from './engine.js'; // Reusing existing engine
import { renderResults } from './results.js';

const app = document.getElementById('app');

async function init() {
    await initStore();
    renderRoute();
}

// --- DEBUG & ERROR HANDLING ---
window.onerror = function (message, source, lineno, colno, error) {
    const app = document.getElementById('app');
    if (app) {
        app.innerHTML += `<div style="color:red; list-style:none; padding:20px; border:1px solid red; margin:20px;">
        <h3>⚠️ Critical Error</h3>
        <p>${message}</p>
        <p>Source: ${source}:${lineno}</p>
        </div>`;
    }
    console.error("Global Catch:", error);
};

// --- RENDER FUNCTIONS ---

function renderIntro(container) {
    container.innerHTML = `
    <div class="card fade-in" style="text-align: center;">
      <h1>Welcome to the Journey of the Self</h1>
      <p>This is not a test. It is a mirror.</p>
      <div style="text-align: left; background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
        <h3>Instructions:</h3>
        <ul>
            <li><strong>Be Honest:</strong> There are no "right" answers. Only your truth.</li>
            <li><strong>Part 1 & 2:</strong> Choose the option that best describes your <em>actual behavior</em>.</li>
            <li><strong>Part 3:</strong> You will face specific life scenarios. Choose your natural reaction.</li>
            <li><strong>Privacy:</strong> Your data is anonymously stored for research.</li>
        </ul>
      </div>
      <button id="start-btn">Begin Assessment</button>
    </div>
  `;

    document.getElementById('start-btn').addEventListener('click', () => {
        // We need to update state, but "initStore" handles loading.
        // Changing view directly here.
        import('./dataStore.js').then(module => {
            module.store.state.view = 'demographics';
            renderRoute();
        });
    });
}

export function renderRoute() {
    console.log("Rendering Route...");
    const store = getStore();
    const app = document.getElementById('app');

    if (!app) {
        console.error("App container not found!");
        return;
    }

    app.innerHTML = '';
    window.scrollTo(0, 0);

    const view = store.state.view;
    console.log("Current View:", view);

    if (view === 'intro') {
        renderIntro(app);
    } else if (view === 'demographics') {
        renderDemographics(app);
    } else if (view === 'guna-likert') {
        renderLikertSection(app, 'guna');
    } else if (view === 'bigfive-likert') {
        renderLikertSection(app, 'bigfive');
    } else if (view === 'scenario') {
        renderScenario(app);
    } else if (view === 'results') {
        renderResults(app);
    } else {
        app.innerHTML = `<p style="color:red">Error: Unknown View '${view}'</p>`;
    }
}

init();
