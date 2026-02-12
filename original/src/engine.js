
import { getStore, logScenarioResponse } from './dataStore.js';
import { renderRoute } from './main.js'; // Ensure circular dependency works or refactor if needed. 
// In vanilla JS modules, imports are live bindings, so this usually works fine.

export function renderScenario(container) {
  const store = getStore();
  const scenario = store.state.scenarios[store.state.currentScenarioIndex];

  const startTime = Date.now();
  let hoverCount = 0;

  const element = document.createElement('div');
  element.className = 'card fade-in';

  element.innerHTML = `
    <div class="scenario-header">
      <div class="progress-bar">
        <div class="progress-fill" style="width: ${((store.state.currentScenarioIndex + 1) / store.state.scenarios.length) * 100}%"></div>
      </div>
      <h2>Part 3: Situational Judgment - ${store.state.currentScenarioIndex + 1} / ${store.state.scenarios.length}</h2>
      <p class="category-tag">Scenario ${store.state.currentScenarioIndex + 1} of ${store.state.scenarios.length}</p>
    </div>
    
    <div class="scenario-content">
      <p class="scenario-text">${scenario.text}</p>
      
      <div class="choice-container">
        ${scenario.options.map(option => `
          <button class="choice-btn" data-id="${option.guna}">
            ${option.text}
          </button>
        `).join('')}
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
