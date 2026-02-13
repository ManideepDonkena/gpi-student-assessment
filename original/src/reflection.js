
import { getStore } from './dataStore.js';
import { renderRoute } from './main.js';
import { translations } from './translations.js';

export function renderReflection(container) {
  const lang = localStorage.getItem('gpi_lang') || 'en';
  const t = translations[lang] || translations['en'];
  const ui = t.reflection;

  const element = document.createElement('div');
  element.className = 'card fade-in';
  element.style.maxWidth = '650px';
  element.style.margin = '0 auto';

  element.innerHTML = `
    <div style="text-align: center; margin-bottom: 20px;">
      <span style="font-size: 2.8em;">🪞</span>
      <h1 style="margin: 8px 0 4px; color: #2c3e50; font-size: 1.6em;">${ui.title}</h1>
    </div>

    <!-- Key Point 1: No good/bad answers -->
    <div style="background: #f0f7ff; border-radius: 10px; padding: 18px; margin: 14px 0; border-left: 4px solid #3498db;">
      <p style="margin: 0; font-size: 1.02em; line-height: 1.7; color: #444;">
        ${ui.point1}
      </p>
    </div>

    <!-- Key Point 2: Don't default to Sometimes -->
    <div style="background: #fef9e7; border-radius: 10px; padding: 18px; margin: 14px 0; border-left: 4px solid #DAA520;">
      <p style="margin: 0; font-size: 1.02em; line-height: 1.7; color: #444;">
        ${ui.point2}
      </p>
    </div>

    <!-- Key Point 3: Think of real examples -->
    <div style="background: #e8f5e9; border-radius: 10px; padding: 18px; margin: 14px 0; border-left: 4px solid #27ae60;">
      <p style="margin: 0; font-size: 1.02em; line-height: 1.7; color: #444;">
        ${ui.point3}
      </p>
    </div>

    <!-- Do / Don't -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 18px 0;">
      <div style="background: #e8f5e9; padding: 14px; border-radius: 10px; text-align: center;">
        <p style="margin: 0 0 6px; font-weight: bold; color: #27ae60; font-size: 0.95em;">${ui.think}</p>
        <p style="margin: 0; font-size: 0.9em; color: #555; font-style: italic;">${ui.think_desc}</p>
      </div>
      <div style="background: #fce4ec; padding: 14px; border-radius: 10px; text-align: center;">
        <p style="margin: 0 0 6px; font-weight: bold; color: #c0392b; font-size: 0.95em;">${ui.dont}</p>
        <p style="margin: 0; font-size: 0.9em; color: #555; font-style: italic;">${ui.dont_desc}</p>
      </div>
      <div style="background: #e8f5e9; padding: 14px; border-radius: 10px; text-align: center;">
        <p style="margin: 0 0 6px; font-weight: bold; color: #27ae60; font-size: 0.95em;">${ui.recall}</p>
        <p style="margin: 0; font-size: 0.9em; color: #555; font-style: italic;">${ui.recall_desc}</p>
      </div>
      <div style="background: #fce4ec; padding: 14px; border-radius: 10px; text-align: center;">
        <p style="margin: 0 0 6px; font-weight: bold; color: #c0392b; font-size: 0.95em;">${ui.dont_think}</p>
        <p style="margin: 0; font-size: 0.9em; color: #555; font-style: italic;">${ui.dont_think_desc}</p>
      </div>
    </div>

    <!-- BG 6.5 Verse -->
    <div style="text-align: center; margin: 22px 0 18px; padding: 18px; background: #fff9e6; border-radius: 10px; border: 1px solid #f0e0a0;">
      <p style="margin: 0 0 6px; font-size: 1.05em; color: #8B7D3C; font-weight: bold;">
        उद्धरेदात्मनात्मानं नात्मानमवसादयेत् ।<br>
        आत्मैव ह्यात्मनो बन्धुरात्मैव रिपुरात्मनः ॥
      </p>
      <p style="margin: 6px 0 0; font-size: 0.88em; color: #666; font-style: italic;">
        ${ui.gita_quote}
      </p>
      <p style="margin: 6px 0 0; font-size: 0.8em; color: #999;">
        — Bhagavad-gītā 6.5 (Śrīla Prabhupāda, Vedabase)
      </p>
    </div>

    <!-- Instruction -->
    <p style="text-align: center; color: #888; font-size: 0.92em; margin: 10px 0 18px;">
      ${ui.take_time}
    </p>

    <!-- Mandatory Checkbox -->
    <div style="text-align: center; margin: 16px 0;">
      <label style="cursor: pointer; font-size: 0.95em; color: #444; display: inline-flex; align-items: center; gap: 8px;">
        <input type="checkbox" id="honesty-checkbox" style="width: 18px; height: 18px; cursor: pointer; accent-color: #27ae60;">
        <span>${ui.checkbox}</span>
      </label>
    </div>

    <!-- Continue Button -->
    <div style="text-align: center; margin-top: 14px;">
      <button id="reflection-continue-btn" style="font-size: 1.1em; padding: 14px 40px; opacity: 0.5;" disabled>
        ${ui.ready_btn}
      </button>
    </div>
  `;

  container.appendChild(element);

  // Button only activates when checkbox is ticked
  const checkbox = element.querySelector('#honesty-checkbox');
  const btn = element.querySelector('#reflection-continue-btn');

  checkbox.addEventListener('change', () => {
    btn.disabled = !checkbox.checked;
    btn.style.opacity = checkbox.checked ? '1' : '0.5';
  });

  btn.addEventListener('click', () => {
    const store = getStore();
    store.state.view = 'guna-likert';
    renderRoute();
  });
}
