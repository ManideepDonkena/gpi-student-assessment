
import { exportSessionData, getStore } from './dataStore.js';
import { studentGunaItems, bigFiveItems } from './items.js';

export function renderResults(container) {
  const state = getStore().state;
  const gunaResponses = state.gunaResponses; // { S1: 4, R1: 2, ... }
  const bigFiveResponses = state.bigFiveResponses; // { BF1: 3, ... }

  // --- 1. Calculate Guna Scores ---
  const scores = { sattva: 0, rajas: 0, tamas: 0 };
  const counts = { sattva: 0, rajas: 0, tamas: 0 };

  // We iterate through the defined items to ensure we catch all categories correctly
  studentGunaItems.forEach(item => {
    const val = gunaResponses[item.id];
    if (val) {
      scores[item.category] += parseInt(val);
      counts[item.category]++;
    }
  });

  const finalGuna = {
    Sattva: (scores.sattva / (counts.sattva || 1)).toFixed(1),
    Rajas: (scores.rajas / (counts.rajas || 1)).toFixed(1),
    Tamas: (scores.tamas / (counts.tamas || 1)).toFixed(1)
  };

  // --- 2. Calculate Big Five Scores ---
  const bfScores = { extraversion: [], agreeableness: [], conscientiousness: [], neuroticism: [], openness: [] };

  bigFiveItems.forEach(item => {
    let val = parseInt(bigFiveResponses[item.id]);
    if (!val) return;

    // Reverse coding: 1->5, 2->4, 3->3, 4->2, 5->1
    if (item.reverse) {
      val = 6 - val;
    }
    bfScores[item.trait].push(val);
  });

  const finalBigFive = {};
  for (const trait in bfScores) {
    const vals = bfScores[trait];
    const sum = vals.reduce((a, b) => a + b, 0);
    finalBigFive[trait.charAt(0).toUpperCase() + trait.slice(1)] = (sum / (vals.length || 1)).toFixed(1);
  }

  // --- 3. Render DOM ---
  const element = document.createElement('div');
  element.className = 'card fade-in';
  element.style.maxWidth = '800px';

  element.innerHTML = `
    <h1>Assessment Complete</h1>
    <p>Here is your personalized personality profile based on the Triguna and Big Five models.</p>
    
    <div class="results-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 2rem;">
        <div class="chart-container">
            <h3>Triguna Profile</h3>
            <canvas id="gunaChart"></canvas>
            <div style="margin-top:1rem; text-align:center;">
                <p><strong>Sattva (Harmony):</strong> ${finalGuna.Sattva} / 5</p>
                <p><strong>Rajas (Passion):</strong> ${finalGuna.Rajas} / 5</p>
                <p><strong>Tamas (Inertia):</strong> ${finalGuna.Tamas} / 5</p>
            </div>
        </div>
        <div class="chart-container">
            <h3>Big Five Profile</h3>
            <canvas id="bigFiveChart"></canvas>
             <div style="margin-top:1rem; text-align:center; font-size: 0.9em;">
                ${Object.entries(finalBigFive).map(([k, v]) => `<span><strong>${k}:</strong> ${v}</span>`).join('<br>')}
            </div>
        </div>
    </div>

    <div style="margin-top: 3rem; text-align: center;">
        <p>You can download your raw data for the research study below.</p>
        <button id="download-btn">Download Session Data (JSON)</button>
        <button class="secondary" onclick="location.reload()" style="margin-left: 1rem;">Start New Session</button>
    </div>
  `;

  container.appendChild(element);

  // --- 4. Render Charts ---
  // Guna Chart (Radar or Bar)
  new Chart(document.getElementById('gunaChart'), {
    type: 'doughnut',
    data: {
      labels: ['Sattva', 'Rajas', 'Tamas'],
      datasets: [{
        data: [finalGuna.Sattva, finalGuna.Rajas, finalGuna.Tamas],
        backgroundColor: ['#FFD700', '#FF4500', '#808080'], // Gold, Red, Grey
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  });

  // Big Five Chart (Bar)
  new Chart(document.getElementById('bigFiveChart'), {
    type: 'bar',
    data: {
      labels: Object.keys(finalBigFive),
      datasets: [{
        label: 'Score (1-5)',
        data: Object.values(finalBigFive),
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true, max: 5 }
      },
      plugins: {
        legend: { display: false }
      }
    }
  });

  // Handle Download
  element.querySelector('#download-btn').addEventListener('click', () => {
    const data = exportSessionData();
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `session-${getStore().state.sessionId}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });
}
