
import { getStore } from './dataStore.js';
import { renderRoute } from './main.js';

export function renderReflection(container) {
    const element = document.createElement('div');
    element.className = 'card fade-in';
    element.style.maxWidth = '700px';
    element.style.margin = '0 auto';

    element.innerHTML = `
    <div style="text-align: center;">
      <span style="font-size: 3em;">🪞</span>
      <h1 style="margin: 10px 0 5px; color: #2c3e50;">A Moment of Honesty</h1>
      <p style="color: #888; font-style: italic;">Before you begin, take a breath and read this.</p>
    </div>

    <div style="background: linear-gradient(135deg, #fef9e7, #fdf2e9); border-radius: 12px; padding: 20px; margin: 20px 0; border-left: 4px solid #DAA520;">
      <p style="font-size: 1.05em; line-height: 1.8; color: #444; margin: 0;">
        <strong>When was the last time you truly thought about who you are?</strong>
      </p>
      <p style="line-height: 1.8; color: #555; margin: 12px 0 0;">
        Not your name, your job, or your grades — but your <em>tendencies</em>. How you react when no one is watching. 
        What you do when things get hard. Whether you keep promises even when it's inconvenient.
      </p>
    </div>

    <div style="background: #f0f7ff; border-radius: 12px; padding: 20px; margin: 16px 0;">
      <p style="font-weight: bold; color: #2c3e50; margin: 0 0 12px;">🎯 Why your honesty matters:</p>
      <ul style="margin: 0; padding-left: 20px; line-height: 2; color: #555;">
        <li>This assessment works <strong>only if you answer truthfully</strong> — not what sounds good, but what is real.</li>
        <li>There are <strong>no "good" or "bad" answers</strong>. Every personality pattern has strengths.</li>
        <li>Choosing "Sometimes" for every question gives you a <strong>meaningless result</strong> — it won't reflect who you actually are.</li>
        <li>Think of <strong>specific real examples</strong> from your life before choosing each answer.</li>
      </ul>
    </div>

    <div style="background: #fff; border: 2px solid #e8e8e8; border-radius: 12px; padding: 20px; margin: 16px 0;">
      <p style="font-weight: bold; color: #2c3e50; margin: 0 0 12px;">💡 How to answer well:</p>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
        <div style="background: #fce4ec; padding: 12px; border-radius: 8px;">
          <p style="margin: 0 0 4px; font-weight: bold; color: #c0392b; font-size: 0.9em;">❌ Don't think:</p>
          <p style="margin: 0; font-size: 0.85em; color: #666;">"What should a good person say?"</p>
        </div>
        <div style="background: #e8f5e9; padding: 12px; border-radius: 8px;">
          <p style="margin: 0 0 4px; font-weight: bold; color: #27ae60; font-size: 0.9em;">✅ Instead think:</p>
          <p style="margin: 0; font-size: 0.85em; color: #666;">"What do I actually do in this situation?"</p>
        </div>
        <div style="background: #fce4ec; padding: 12px; border-radius: 8px;">
          <p style="margin: 0 0 4px; font-weight: bold; color: #c0392b; font-size: 0.9em;">❌ Don't default to:</p>
          <p style="margin: 0; font-size: 0.85em; color: #666;">"Sometimes" for everything</p>
        </div>
        <div style="background: #e8f5e9; padding: 12px; border-radius: 8px;">
          <p style="margin: 0 0 4px; font-weight: bold; color: #27ae60; font-size: 0.9em;">✅ Instead recall:</p>
          <p style="margin: 0; font-size: 0.85em; color: #666;">A real recent example, then decide</p>
        </div>
      </div>
    </div>

    <div style="text-align: center; margin-top: 24px; padding: 16px; background: #fff9e6; border-radius: 10px; border: 1px solid #f0e0a0;">
      <p style="margin: 0; font-style: italic; color: #8B7D3C; font-size: 0.95em;">
        📖 "आत्मैव ह्यात्मनो बन्धुरात्मैव रिपुरात्मनः"<br>
        <span style="font-style: normal; color: #666; font-size: 0.9em;">"The self is the friend of the self, and the self is the enemy of the self." — BG 6.5</span>
      </p>
    </div>

    <div style="text-align: center; margin-top: 24px;">
      <p style="color: #888; font-size: 0.9em; margin-bottom: 16px;">
        Take 10 seconds. Close your eyes. Think of who you really are — then proceed.
      </p>
      <button id="reflection-continue-btn" style="font-size: 1.1em; padding: 14px 40px;" disabled>
        I'm Ready to Be Honest →
      </button>
      <p id="countdown-text" style="color: #aaa; font-size: 0.8em; margin-top: 8px;">Please wait 10 seconds...</p>
    </div>
  `;

    container.appendChild(element);

    // Countdown timer - forces user to actually pause and reflect
    let seconds = 10;
    const btn = element.querySelector('#reflection-continue-btn');
    const countdownText = element.querySelector('#countdown-text');

    const timer = setInterval(() => {
        seconds--;
        if (seconds > 0) {
            countdownText.textContent = `Please wait ${seconds} seconds...`;
        } else {
            clearInterval(timer);
            btn.disabled = false;
            btn.style.opacity = '1';
            countdownText.textContent = '';
        }
    }, 1000);

    btn.addEventListener('click', () => {
        const store = getStore();
        store.state.view = 'guna-likert';
        renderRoute();
    });
}
