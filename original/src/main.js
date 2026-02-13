
import { initStore, getStore, logViewDuration, resetSession } from './dataStore.js';
import { renderDemographics } from './demographics.js';
import { renderLikertSection } from './likertRenderer.js';
import { renderScenario } from './engine.js';
import { renderResults } from './results.js';
import { renderReflection } from './reflection.js';
import { translations } from './translations.js';

const app = document.getElementById('app');

async function init() {
  await initStore();
  const store = getStore();

  // If we have a session in progress (view != intro), force show Intro first
  // so user can choose to Resume or Start New.
  if (store.state.view && store.state.view !== 'intro') {
    console.log("Session found, showing Intro for Resume/New choice.");
    renderRoute('intro');
  } else {
    renderRoute();
  }
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
  const lang = localStorage.getItem('gpi_lang') || 'en';
  const t = translations[lang] || translations['en'];
  const ui = t.intro;
  const common = t.ui;

  const store = getStore();
  const hasSession = store.state.view && store.state.view !== 'intro';

  container.innerHTML = `
    <div class="card fade-in" style="text-align: center; max-width: 700px; margin: 0 auto; position: relative;">
      
      <!-- Language Switcher -->
      <button id="lang-switch-btn" style="display: none; position: absolute; top: 10px; right: 10px; background: transparent; border: 1px solid #ddd; font-size: 0.8em; padding: 4px 8px; border-radius: 4px; color: #666; cursor: pointer;">
        🌐 ${common.change_lang || "Change Language"}
      </button>

      <p style="font-size: 1.1em; color: #888; font-style: italic; margin-bottom: 0;">${ui.subtitle}</p>
      <h1 style="font-size: 2em; margin: 10px 0; color: #2c3e50;">${ui.title}</h1>
      <p style="font-size: 1.05em; color: #555; line-height: 1.7;">
        ${ui.desc}
      </p>

      <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin: 24px 0;">
        <div style="background: linear-gradient(135deg, #FFF8DC, #FFEFD5); padding: 16px; border-radius: 12px;">
          <div style="font-size: 2em;">🧘</div>
          <p style="font-weight: bold; margin: 6px 0 2px; color: #B8860B;">${ui.p1_title}</p>
          <p style="font-size: 0.8em; color: #666;">${ui.p1_desc}</p>
        </div>
        <div style="background: linear-gradient(135deg, #E8F4FD, #D6EAF8); padding: 16px; border-radius: 12px;">
          <div style="font-size: 2em;">🧠</div>
          <p style="font-weight: bold; margin: 6px 0 2px; color: #2980B9;">${ui.p2_title}</p>
          <p style="font-size: 0.8em; color: #666;">${ui.p2_desc}</p>
        </div>
        <div style="background: linear-gradient(135deg, #F5EEF8, #EBDEF0); padding: 16px; border-radius: 12px;">
          <div style="font-size: 2em;">🎭</div>
          <p style="font-weight: bold; margin: 6px 0 2px; color: #8E44AD;">${ui.p3_title}</p>
          <p style="font-size: 0.8em; color: #666;">${ui.p3_desc}</p>
        </div>
      </div>

      <div style="text-align: left; background: #f8f9fa; padding: 16px 20px; border-radius: 10px; margin: 16px 0; border-left: 4px solid #3498db;">
        <p style="margin: 0 0 8px; font-weight: bold; color: #2c3e50;">${ui.before_title}</p>
        <ul style="margin: 0; padding-left: 20px; line-height: 1.8; color: #555;">
            <li>${ui.li1}</li>
            <li>${ui.li2}</li>
            <li>${ui.li3}</li>
            <li>${ui.li4}</li>
        </ul>
      </div>

      <p style="font-size: 0.9em; color: #888; margin-bottom: 20px;">
        ${ui.footer}
      </p>

      ${hasSession ? `
        <div style="background: #e8f5e9; padding: 20px; border-radius: 10px; border: 1px solid #c8e6c9;">
            <p style="margin: 0 0 15px; font-weight: bold; color: #2e7d32;">${common.session_msg}</p>
            <div style="display: flex; gap: 15px; justify-content: center;">
                <button id="resume-btn" style="background: #2e7d32; color: white;">${common.resume_btn}</button>
                <button id="new-btn" style="background: white; color: #d32f2f; border: 1px solid #d32f2f;">${common.new_session_btn}</button>
            </div>
        </div>
      ` : `
        <button id="start-btn" style="font-size: 1.1em; padding: 14px 40px;">${common.start_btn}</button>
      `}
    </div>
  `;

  // Language Switcher Logic
  document.getElementById('lang-switch-btn').addEventListener('click', () => {
    // Clear language preference and reload to show modal
    localStorage.removeItem('gpi_lang');
    sessionStorage.removeItem('lang_selected');
    location.reload();
  });

  if (hasSession) {
    document.getElementById('resume-btn').addEventListener('click', () => {
      // Resume: User requested to start from Reflection to "re-prime"
      renderRoute('reflection');
    });
    document.getElementById('new-btn').addEventListener('click', () => {
      if (confirm('Are you sure? This will delete your answers but keep your demographics.\n\n(क्या आप सुनिश्चित हैं? यह आपके उत्तरों को हटा देगा लेकिन आपकी पृष्ठभूमि की जानकारी को सुरक्षित रखेगा।)')) {
        // Start New: Keep Demographics = true
        resetSession({ keepDemographics: true });
        initStore().then(() => {
          // If we kept demographics, go to Reflection.
          if (Object.keys(store.state.demographics).length > 0) {
            renderRoute('reflection');
          } else {
            renderRoute('demographics');
          }
        });
      }
    });
  } else {
    document.getElementById('start-btn').addEventListener('click', () => {
      import('./dataStore.js').then(module => {
        module.store.state.view = 'demographics';
        renderRoute();
      });
    });
  }
}

export function renderRoute(viewOverride) {
  const store = getStore();
  const app = document.getElementById('app');

  if (!app) {
    console.error("App container not found!");
    return;
  }

  const view = viewOverride || store.state.view;
  console.log("Rendering View:", view);

  // --- Timing Tracking ---
  const now = Date.now();
  if (window.lastView && window.lastView !== view) {
    const duration = now - window.lastViewTime;
    logViewDuration(window.lastView, duration);
    console.log(`Time on ${window.lastView}: ${duration}ms`);
  }
  window.lastView = view;
  window.lastViewTime = now;

  app.innerHTML = '';
  window.scrollTo(0, 0);

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
