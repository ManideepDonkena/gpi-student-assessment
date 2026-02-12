
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

  // Raw Mean Scores (for statistical analysis: CFA, reliability, regression)
  const rawGuna = {
    Sattva: (scores.sattva / (counts.sattva || 1)).toFixed(2),
    Rajas: (scores.rajas / (counts.rajas || 1)).toFixed(2),
    Tamas: (scores.tamas / (counts.tamas || 1)).toFixed(2)
  };

  // Normalized Scores (sum = 1, for profile visualization)
  const rawTotal = parseFloat(rawGuna.Sattva) + parseFloat(rawGuna.Rajas) + parseFloat(rawGuna.Tamas);
  const normGuna = {
    Sattva: (parseFloat(rawGuna.Sattva) / (rawTotal || 1)),
    Rajas: (parseFloat(rawGuna.Rajas) / (rawTotal || 1)),
    Tamas: (parseFloat(rawGuna.Tamas) / (rawTotal || 1))
  };

  // Dominant Guna
  const dominant = Object.entries(normGuna).sort((a, b) => b[1] - a[1])[0];
  const dominantName = dominant[0];
  const dominantPct = (dominant[1] * 100).toFixed(1);

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

  // Store computed scores in state for Firebase/download
  state.computedScores = {
    gunaRaw: rawGuna,
    gunaNormalized: {
      Sattva: normGuna.Sattva.toFixed(3),
      Rajas: normGuna.Rajas.toFixed(3),
      Tamas: normGuna.Tamas.toFixed(3)
    },
    dominantGuna: dominantName,
    bigFive: finalBigFive
  };

  // --- 3. Render DOM ---
  const element = document.createElement('div');
  element.className = 'card fade-in';
  element.style.maxWidth = '900px';

  const gunaDescriptions = {
    Sattva: 'Balance, wisdom, clarity, and inner peace.',
    Rajas: 'Ambition, energy, desire, and restlessness.',
    Tamas: 'Inertia, comfort-seeking, and resistance to change.'
  };

  element.innerHTML = `
    <h1>Assessment Complete</h1>
    <p>Here is your personalized personality profile based on the Triguna and Big Five models.</p>
    
    <div class="results-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 2rem;">

        <!-- LEFT: Triguna Profile -->
        <div class="chart-container">
            <h3>Triguna Profile</h3>
            <canvas id="gunaChart"></canvas>

            <div style="margin-top: 1rem; background: #f0f7ff; border-radius: 8px; padding: 12px; text-align: center;">
                <p style="margin: 0; font-size: 0.85em; color: #666;">Dominant Guna</p>
                <p style="margin: 4px 0 0; font-size: 1.3em; font-weight: bold; color: #2c3e50;">${dominantName} (${dominantPct}%)</p>
                <p style="margin: 4px 0 0; font-size: 0.8em; color: #555; font-style: italic;">${gunaDescriptions[dominantName]}</p>
            </div>

            <table style="width: 100%; margin-top: 12px; border-collapse: collapse; font-size: 0.85em;">
                <thead>
                    <tr style="border-bottom: 2px solid #ddd;">
                        <th style="text-align: left; padding: 6px;">Guna</th>
                        <th style="text-align: center; padding: 6px;">Mean (1-5)</th>
                        <th style="text-align: center; padding: 6px;">Proportion</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 6px;">🟡 Sattva</td>
                        <td style="text-align: center;">${rawGuna.Sattva}</td>
                        <td style="text-align: center;">${(normGuna.Sattva * 100).toFixed(1)}%</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 6px;">🔴 Rajas</td>
                        <td style="text-align: center;">${rawGuna.Rajas}</td>
                        <td style="text-align: center;">${(normGuna.Rajas * 100).toFixed(1)}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px;">⚫ Tamas</td>
                        <td style="text-align: center;">${rawGuna.Tamas}</td>
                        <td style="text-align: center;">${(normGuna.Tamas * 100).toFixed(1)}%</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- RIGHT: Big Five Profile -->
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
  // Guna Chart - uses NORMALIZED values for proportional donut
  new Chart(document.getElementById('gunaChart'), {
    type: 'doughnut',
    data: {
      labels: ['Sattva', 'Rajas', 'Tamas'],
      datasets: [{
        data: [normGuna.Sattva, normGuna.Rajas, normGuna.Tamas],
        backgroundColor: ['#FFD700', '#FF4500', '#808080'],
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' },
        tooltip: {
          callbacks: {
            label: function (context) {
              const pct = (context.parsed * 100).toFixed(1);
              const guna = context.label;
              return `${guna}: ${pct}% (Mean: ${rawGuna[guna]}/5)`;
            }
          }
        }
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
