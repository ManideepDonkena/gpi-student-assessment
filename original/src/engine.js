
import { getStore, logScenarioResponse } from './dataStore.js';
import { renderRoute } from './main.js';
import { translations } from './translations.js';

export function renderScenario(container) {
  const store = getStore();
  const scenario = store.state.scenarios[store.state.currentScenarioIndex];

  // Translation Logic
  const lang = localStorage.getItem('gpi_lang') || 'en';
  const t = translations[lang] || translations['en'];
  const sjtT = t.sjt || {}; // Situational Judgment Translations

  // Fallback to English/Store text if translation missing
  const scenarioText = sjtT[scenario.id] || scenario.text;

  const startTime = Date.now();
  let hoverCount = 0;

  const element = document.createElement('div');
  element.className = 'card fade-in';

  // Map options to translations based on index
  // options[0] -> SC1_OPT1, options[1] -> SC1_OPT2
  const renderedOptions = scenario.options.map((option, index) => {
    const optKey = `${scenario.id}_OPT${index + 1}`;
    const optText = sjtT[optKey] || option.text;
    return `
        <button class="choice-btn" data-id="${option.guna}">
          ${optText}
        </button>
      `;
  }).join('');

  element.innerHTML = `
    <div class="scenario-header">
      <div class="progress-bar">
        <div class="progress-fill" style="width: ${((store.state.currentScenarioIndex + 1) / store.state.scenarios.length) * 100}%"></div>
      </div>
      <h2>${t.intro.p3_title}: ${store.state.currentScenarioIndex + 1} / ${store.state.scenarios.length}</h2>
      <p class="category-tag">${t.intro.p3_desc.split('<br>')[0]} ${store.state.currentScenarioIndex + 1}</p>
    </div>
    
    <div class="scenario-content">
      <p class="scenario-text">${scenarioText}</p>
      
      <div class="choice-container">
        ${renderedOptions}
      </div>
    </div>
  `;

  const buttons = element.querySelectorAll('.choice-btn');
  buttons.forEach(btn => {
    btn.addEventListener('mouseenter', () => hoverCount++);

    btn.addEventListener('click', (e) => {
      const choiceId = e.target.dataset.id || (e.target.closest('.choice-btn') ? e.target.closest('.choice-btn').dataset.id : 'unknown');
      const endTime = Date.now();

      logScenarioResponse({
        scenarioId: scenario.id,
        choiceId: choiceId,
        timeToSelectMs: endTime - startTime,
        hoverCount: hoverCount,
        timestamp: new Date().toISOString()
      });

      renderRoute();
    });
  });

  container.appendChild(element);
}
