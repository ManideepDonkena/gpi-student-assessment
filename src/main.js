
import { initStore, getStore } from './dataStore.js';
import { renderDemographics } from './demographics.js';
import { renderLikertSection } from './likertRenderer.js';
import { renderScenario } from './engine.js'; // Reusing existing engine
import { renderResults } from './results.js';
import { renderReflection } from './reflection.js';

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
    <div class="card fade-in" style="text-align: center; max-width: 700px; margin: 0 auto;">
      
      <p style="font-size: 1.1em; color: #888; font-style: italic; margin-bottom: 0;">त्रिविधा भवति श्रद्धा</p>
      <h1 style="font-size: 2em; margin: 10px 0; color: #2c3e50;">Discover Your Inner Nature</h1>
      <p style="font-size: 1.05em; color: #555; line-height: 1.7;">
        According to the Bhagavad Gita, every person is a unique blend of three fundamental qualities — 
        <strong style="color: #DAA520;">Sattva</strong> (harmony), 
        <strong style="color: #FF4500;">Rajas</strong> (passion), and 
        <strong style="color: #708090;">Tamas</strong> (inertia). 
        This assessment reveals <em>your</em> unique balance.
      </p>

      <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin: 24px 0;">
        <div style="background: linear-gradient(135deg, #E8F4FD, #D6EAF8); padding: 16px; border-radius: 12px;">
          <div style="font-size: 2em;">🧠</div>
          <p style="font-weight: bold; margin: 6px 0 2px; color: #2980B9;">Part 1</p>
          <p style="font-size: 0.8em; color: #666;">Personality Traits<br>(10 questions)</p>
        </div>
        <div style="background: linear-gradient(135deg, #FFF8DC, #FFEFD5); padding: 16px; border-radius: 12px;">
          <div style="font-size: 2em;">🧘</div>
          <p style="font-weight: bold; margin: 6px 0 2px; color: #B8860B;">Part 2</p>
          <p style="font-size: 0.8em; color: #666;">Self-Reflection<br>(57 questions)</p>
        </div>
        <div style="background: linear-gradient(135deg, #F5EEF8, #EBDEF0); padding: 16px; border-radius: 12px;">
          <div style="font-size: 2em;">🎭</div>
          <p style="font-weight: bold; margin: 6px 0 2px; color: #8E44AD;">Part 3</p>
          <p style="font-size: 0.8em; color: #666;">Life Scenarios<br>(3 situations)</p>
        </div>
      </div>

      <div style="text-align: left; background: #f8f9fa; padding: 16px 20px; border-radius: 10px; margin: 16px 0; border-left: 4px solid #3498db;">
        <p style="margin: 0 0 8px; font-weight: bold; color: #2c3e50;">📋 Before you begin:</p>
        <ul style="margin: 0; padding-left: 20px; line-height: 1.8; color: #555;">
            <li>There are <strong>no right or wrong answers</strong> — only your truth.</li>
            <li>Answer based on your <strong>actual behavior</strong>, not what you think is ideal.</li>
            <li>Takes approximately <strong>8 - 12 minutes</strong>.</li>
            <li>Your data is <strong>100% anonymous</strong> and used only for academic research.</li>
        </ul>
      </div>

      <p style="font-size: 0.9em; color: #888; margin-bottom: 20px;">
        🎁 At the end, you'll receive your <strong>personalized Triguna profile</strong> with insights about your personality.
      </p>

      <button id="start-btn" style="font-size: 1.1em; padding: 14px 40px;">Begin the Journey →</button>
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
  } else if (view === 'reflection') {
    renderReflection(app);
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
