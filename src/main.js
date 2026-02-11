
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

export function renderRoute() {
    const store = getStore();
    app.innerHTML = '';
    window.scrollTo(0, 0);

    const view = store.state.view;

    if (view === 'demographics') {
        renderDemographics(app);
    } else if (view === 'guna-likert') {
        renderLikertSection(app, 'guna');
    } else if (view === 'bigfive-likert') {
        renderLikertSection(app, 'bigfive');
    } else if (view === 'scenario') {
        renderScenario(app);
    } else if (view === 'results') {
        renderResults(app);
    }
}

init();
