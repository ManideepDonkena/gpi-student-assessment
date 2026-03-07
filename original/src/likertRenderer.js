
import { getStore, submitGunaResponses, submitBigFiveResponses, updateGunaResponse, updateBigFiveResponse } from './dataStore.js';
import { translations } from './translations.js';
import { renderRoute } from './main.js';

export function renderLikertSection(container, type) {
  /* --- Translation Logic --- */
  const lang = localStorage.getItem('gpi_lang') || 'en';
  const t = translations[lang] || translations['en'];

  const store = getStore();
  const items = type === 'guna' ? store.state.gunaItems : store.state.bigFiveItems;
  const savedResponses = type === 'guna' ? store.state.gunaResponses : store.state.bigFiveResponses;

  // Update Header (using translations)
  const title = type === 'guna' ? t.ui.part2 : t.ui.part1;
  const desc = type === 'guna'
    ? 'For each statement, indicate your level of agreement (1 = Strongly Disagree, 7 = Strongly Agree).'
    : 'I see myself as someone who... (1 = Disagree Strongly, 5 = Agree Strongly)';

  const element = document.createElement('div');
  element.className = 'card fade-in';

  // Render form
  let html = `
    <h2>${title}</h2>
    <p>${desc}</p>
    <form id="likert-form" novalidate>
      <div id="items-container"></div>
      <div style="text-align: center; margin-top: 30px;">
        <button type="submit" class="btn-primary">${t.ui.next}</button>
      </div>
    </form>
  `;

  // We construct the items HTML separately
  let itemsHtml = "";

  let currentDomain = "";
  items.forEach((item, idx) => {
    // Inject Header if domain changes (Only for Guna items)
    if (false && type === 'guna' && item.domain && item.domain !== currentDomain) {
      currentDomain = item.domain;
      let domainTitle = currentDomain.charAt(0).toUpperCase() + currentDomain.slice(1) + " Life";
      if (currentDomain === 'inner') domainTitle = "Inner Thoughts & Ethics";

      itemsHtml += `<h3 style="margin-top: 30px; border-bottom: 2px solid #eee; padding-bottom: 5px;">${domainTitle}</h3>`;
    }

    // Determine labels based on type
    const labels = type === 'guna'
      ? [
        (t.likert?.guna && t.likert.guna["1"]) || 'Strongly Disagree',
        (t.likert?.guna && t.likert.guna["2"]) || 'Disagree',
        (t.likert?.guna && t.likert.guna["3"]) || 'Somewhat Disagree',
        (t.likert?.guna && t.likert.guna["4"]) || 'Neutral',
        (t.likert?.guna && t.likert.guna["5"]) || 'Somewhat Agree',
        (t.likert?.guna && t.likert.guna["6"]) || 'Agree',
        (t.likert?.guna && t.likert.guna["7"]) || 'Strongly Agree'
      ]
      : [
        (t.likert?.bigfive && t.likert.bigfive["1"]) || 'Disagree Strongly',
        (t.likert?.bigfive && t.likert.bigfive["2"]) || 'Disagree a little',
        (t.likert?.bigfive && t.likert.bigfive["3"]) || 'Neutral',
        (t.likert?.bigfive && t.likert.bigfive["4"]) || 'Agree a little',
        (t.likert?.bigfive && t.likert.bigfive["5"]) || 'Agree Strongly'
      ];

    // Translation Lookup for Item Text
    const itemText = (t.items && t.items[item.id]) ? t.items[item.id] : item.text;

    itemsHtml += `
      <div class="question-card" data-id="${item.id}" data-type="${type}">
        <p class="question-text">${itemText}</p>
        <div class="likert-options" style="display: flex; justify-content: space-between; gap: 5px;">
    `;

    labels.forEach((label, index) => {
      // Value is index + 1
      const val = index + 1;
      const isChecked = savedResponses && savedResponses[item.id] == val ? 'checked' : '';
      itemsHtml += `
          <label style="flex: 1; text-align: center; font-size: 0.85em; cursor: pointer;">
            <div style="margin-bottom: 5px;">${val}</div>
            <input type="radio" name="${item.id}" value="${val}" required ${isChecked}>
            <div style="margin-top: 5px; line-height: 1.2;">${label}</div>
          </label>
        `;
    });
    itemsHtml += `
        </div>
      </div>
    `;
  });

  // Inject items HTML into the main structure (hacky but works with the original design)
  // Actually, I'll just set innerHTML of element, but I need to insert itemsHtml into the form.
  // The structure above had <div id="items-container"></div>

  element.innerHTML = html;
  element.querySelector('#items-container').innerHTML = itemsHtml;

  // --- Behavioral Tracking ---
  const startTime = Date.now();
  let accumulatedHiddenTime = 0;
  let lastHideTime = 0;

  // Handle Tab Switching / Visibility
  let switchCount = 0;
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      lastHideTime = Date.now();
      switchCount++;
    } else {
      if (lastHideTime > 0) {
        accumulatedHiddenTime += (Date.now() - lastHideTime);
        lastHideTime = 0;
      }
    }
  });

  let cursorDistance = 0;
  let answerChanges = 0;
  let lastX = 0;
  let lastY = 0;

  // Track Answer Changes & Details
  const detailedResponses = {};

  element.querySelectorAll('input[type="radio"]').forEach(radio => {
    radio.addEventListener('change', (e) => {
      answerChanges++;

      // Capture details
      const qId = e.target.name;
      const val = parseInt(e.target.value);
      const item = items.find(i => i.id === qId);

      detailedResponses[qId] = {
        id: qId,
        value: val,
        text: item ? item.text : "Unknown",
        // Calculate reaction time relative to section load (minus hidden time)
        reactionTimeMs: Math.max(0, (Date.now() - startTime) - accumulatedHiddenTime),
        timestamp: new Date().toISOString()
      };

      // Auto-save partial response
      if (type === 'guna') {
        updateGunaResponse(qId, val, detailedResponses[qId]);
      } else {
        updateBigFiveResponse(qId, val, detailedResponses[qId]);
      }
    });
  });

  // Track Mouse Movement
  const trackMouse = (e) => {
    if (lastX !== 0 && lastY !== 0) {
      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;
      cursorDistance += Math.sqrt(dx * dx + dy * dy);
    }
    lastX = e.clientX;
    lastY = e.clientY;
  };

  document.addEventListener('mousemove', trackMouse);

  // Handle Submit
  element.querySelector('form').addEventListener('submit', (e) => {
    e.preventDefault();

    // --- Manual Validation for iOS Safari ---
    const form = e.target;
    if (!form.checkValidity()) {
      const firstInvalid = form.querySelector('input:invalid');
      if (firstInvalid) {
        // Scroll to the error
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Visual Cue
        const card = firstInvalid.closest('.question-card');
        if (card) {
          card.style.transition = "background-color 0.3s";
          const originalBg = card.style.backgroundColor;
          card.style.backgroundColor = "#fff0f0"; // Light red
          setTimeout(() => card.style.backgroundColor = originalBg, 2000);
        }

        alert("Please answer all questions to proceed.");
      }
      return;
    }

    document.removeEventListener('mousemove', trackMouse); // Cleanup

    const formData = new FormData(e.target);
    const responses = {};

    items.forEach(item => {
      responses[item.id] = parseInt(formData.get(item.id));
    });

    const metadata = {
      timeMs: Math.max(0, (Date.now() - startTime) - accumulatedHiddenTime),
      cursorDistancePx: Math.round(cursorDistance),
      answerChanges: answerChanges,
      idleTimeMs: accumulatedHiddenTime,
      tabSwitches: switchCount
    };

    if (type === 'guna') {
      submitGunaResponses(responses, metadata, detailedResponses);
    } else {
      submitBigFiveResponses(responses, metadata, detailedResponses);
    }
    renderRoute();
  });

  container.appendChild(element);
}
