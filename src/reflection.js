
import { getStore } from './dataStore.js';
import { renderRoute } from './main.js';

export function renderReflection(container) {
  const element = document.createElement('div');
  element.className = 'card fade-in';
  element.style.maxWidth = '650px';
  element.style.margin = '0 auto';

  element.innerHTML = `
    <div style="text-align: center; margin-bottom: 20px;">
      <span style="font-size: 2.8em;">🪞</span>
      <h1 style="margin: 8px 0 4px; color: #2c3e50; font-size: 1.6em;">Before You Begin</h1>
    </div>

    <!-- Key Point 1: No good/bad answers -->
    <div style="background: #f0f7ff; border-radius: 10px; padding: 18px; margin: 14px 0; border-left: 4px solid #3498db;">
      <p style="margin: 0; font-size: 1.02em; line-height: 1.7; color: #444;">
        ✅ There are <strong>no "good" or "bad" answers</strong>. Every personality pattern has its own strengths.
      </p>
    </div>

    <!-- Key Point 2: Don't default to Sometimes -->
    <div style="background: #fef9e7; border-radius: 10px; padding: 18px; margin: 14px 0; border-left: 4px solid #DAA520;">
      <p style="margin: 0; font-size: 1.02em; line-height: 1.7; color: #444;">
        ⚠️ Choosing <strong>"Sometimes" for every question</strong> gives you a <strong>meaningless result</strong> — it won't reflect who you actually are.
      </p>
    </div>

    <!-- Key Point 3: Think of real examples -->
    <div style="background: #e8f5e9; border-radius: 10px; padding: 18px; margin: 14px 0; border-left: 4px solid #27ae60;">
      <p style="margin: 0; font-size: 1.02em; line-height: 1.7; color: #444;">
        💡 Think of <strong>specific real examples</strong> from your life before choosing each answer.
      </p>
    </div>

    <!-- Do / Don't -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 18px 0;">
      <div style="background: #e8f5e9; padding: 14px; border-radius: 10px; text-align: center;">
        <p style="margin: 0 0 6px; font-weight: bold; color: #27ae60; font-size: 0.95em;">✅ Think:</p>
        <p style="margin: 0; font-size: 0.9em; color: #555; font-style: italic;">"What do I actually do in this situation?"</p>
      </div>
      <div style="background: #fce4ec; padding: 14px; border-radius: 10px; text-align: center;">
        <p style="margin: 0 0 6px; font-weight: bold; color: #c0392b; font-size: 0.95em;">❌ Don't default to:</p>
        <p style="margin: 0; font-size: 0.9em; color: #555; font-style: italic;">"Sometimes" for everything</p>
      </div>
      <div style="background: #e8f5e9; padding: 14px; border-radius: 10px; text-align: center;">
        <p style="margin: 0 0 6px; font-weight: bold; color: #27ae60; font-size: 0.95em;">✅ Recall:</p>
        <p style="margin: 0; font-size: 0.9em; color: #555; font-style: italic;">A real recent example, then decide</p>
      </div>
      <div style="background: #fce4ec; padding: 14px; border-radius: 10px; text-align: center;">
        <p style="margin: 0 0 6px; font-weight: bold; color: #c0392b; font-size: 0.95em;">❌ Don't think:</p>
        <p style="margin: 0; font-size: 0.9em; color: #555; font-style: italic;">"What should a good person say?"</p>
      </div>
    </div>

    <!-- BG 6.5 Verse -->
    <div style="text-align: center; margin: 22px 0 18px; padding: 18px; background: #fff9e6; border-radius: 10px; border: 1px solid #f0e0a0;">
      <p style="margin: 0 0 6px; font-size: 1.05em; color: #8B7D3C; font-weight: bold;">
        उद्धरेदात्मनात्मानं नात्मानमवसादयेत् ।<br>
        आत्मैव ह्यात्मनो बन्धुरात्मैव रिपुरात्मनः ॥
      </p>
      <p style="margin: 6px 0 0; font-size: 0.88em; color: #666; font-style: italic;">
        "One must deliver himself with the help of his mind, and not degrade himself.<br>
        The mind is the friend of the conditioned soul, and his enemy as well."
      </p>
      <p style="margin: 6px 0 0; font-size: 0.8em; color: #999;">
        — Bhagavad-gītā 6.5 (Śrīla Prabhupāda, Vedabase)
      </p>
    </div>

    <!-- Instruction -->
    <p style="text-align: center; color: #888; font-size: 0.92em; margin: 10px 0 18px;">
      Take 10 seconds. Close your eyes. Think of who you really are — then proceed.
    </p>

    <!-- Mandatory Checkbox -->
    <div style="text-align: center; margin: 16px 0;">
      <label style="cursor: pointer; font-size: 0.95em; color: #444; display: inline-flex; align-items: center; gap: 8px;">
        <input type="checkbox" id="honesty-checkbox" style="width: 18px; height: 18px; cursor: pointer; accent-color: #27ae60;">
        <span>I have read the above and I will answer honestly</span>
      </label>
    </div>

    <!-- Continue Button -->
    <div style="text-align: center; margin-top: 14px;">
      <button id="reflection-continue-btn" style="font-size: 1.1em; padding: 14px 40px; opacity: 0.5;" disabled>
        I'm Ready →
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
