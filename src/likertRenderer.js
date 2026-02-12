
import { getStore, submitGunaResponses, submitBigFiveResponses } from './dataStore.js';
import { renderRoute } from './main.js';

export function renderLikertSection(container, type) {
  const store = getStore();
  const items = type === 'guna' ? store.state.gunaItems : store.state.bigFiveItems;
  const title = type === 'guna' ? 'Part 1: Self-Reflection' : 'Part 2: Personality Traits';
  const desc = type === 'guna'
    ? 'For each situation, choose the option that best describes your usual behavior (1 = Never, 5 = Always).'
    : 'I see myself as someone who... (1 = Disagree Strongly, 5 = Agree Strongly)';

  const element = document.createElement('div');
  element.className = 'card fade-in';

  // Render form
  let html = `
    <h2>${title}</h2>
    <p>${desc}</p>
    <form id="likert-form">
  `;

  items.forEach(item => {
    // Determine labels based on type
    const labels = type === 'guna'
      ? ['Never', 'Rarely', 'Sometimes', 'Often', 'Always']
      : ['Disagree', 'Slightly Disagree', 'Neutral', 'Slightly Agree', 'Agree'];

    html += `
      <div class="likert-item">
        <p>${item.text}</p>
        <div class="likert-options">
          <label><span>${labels[0]}</span><input type="radio" name="${item.id}" value="1" required></label>
          <label><span>${labels[1]}</span><input type="radio" name="${item.id}" value="2" required></label>
          <label><span>${labels[2]}</span><input type="radio" name="${item.id}" value="3" required></label>
          <label><span>${labels[3]}</span><input type="radio" name="${item.id}" value="4" required></label>
          <label><span>${labels[4]}</span><input type="radio" name="${item.id}" value="5" required></label>
        </div>
      </div>
    `;
  });

  html += `<br><button type="submit">Continue</button></form>`;
  element.innerHTML = html;

  // --- Behavioral Tracking ---
  const startTime = Date.now();
  let cursorDistance = 0;
  let answerChanges = 0;
  let lastX = 0;
  let lastY = 0;

  // Track Answer Changes
  element.querySelectorAll('input[type="radio"]').forEach(radio => {
    radio.addEventListener('change', () => {
      answerChanges++;
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
    document.removeEventListener('mousemove', trackMouse); // Cleanup

    const formData = new FormData(e.target);
    const responses = {};

    items.forEach(item => {
      responses[item.id] = parseInt(formData.get(item.id));
    });

    const metadata = {
      timeMs: Date.now() - startTime,
      cursorDistancePx: Math.round(cursorDistance),
      answerChanges: answerChanges
    };

    if (type === 'guna') {
      submitGunaResponses(responses, metadata);
    } else {
      submitBigFiveResponses(responses, metadata);
    }
    renderRoute();
  });

  container.appendChild(element);
}
