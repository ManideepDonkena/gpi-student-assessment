import { exportSessionData, getStore } from './dataStore.js';
import { studentGunaItems, bigFiveItems } from './items.js';
import { translations } from './translations.js';

export function renderResults(container) {
  const lang = localStorage.getItem('gpi_lang') || 'en';
  const t = translations[lang] || translations['en'];
  const ui = t.results;

  const state = getStore().state;
  const gunaResponses = state.gunaResponses; // { S1: 4, R1: 2, ... }
  const bigFiveResponses = state.bigFiveResponses; // { BF1: 3, ... }

  // Use translations for interpretations
  const gunaDescriptions = t.results.interpretations;
  const bfDescriptions = t.results.bigfive;

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

  const chartT = t.charts || {
    Sattva: "Sattva", Rajas: "Rajas", Tamas: "Tamas",
    Mean: "Mean", Pct: "%", Dom: "Dom", Sec: "Sec",
    Guna: "Guna", Score: "Score",
    Extraversion: "Extraversion", Agreeableness: "Agreeableness",
    Conscientiousness: "Conscientiousness", Neuroticism: "Neuroticism", Openness: "Openness"
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
    const traitKey = item.trait.toLowerCase();
    if (bfScores[traitKey]) {
      bfScores[traitKey].push(val);
    }
  });

  const finalBigFive = {};
  for (const trait in bfScores) {
    const vals = bfScores[trait];
    const sum = vals.reduce((a, b) => a + b, 0);
    // Capitalize trait name for finalBigFive keys (consistent with scoring.js)
    const traitKey = trait.charAt(0).toUpperCase() + trait.slice(1);
    finalBigFive[traitKey] = (sum / (vals.length || 1)).toFixed(1);
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
  // element.style.maxWidth = '900px'; // CSS handles this

  // Helper for Big Five Color
  const getScoreColor = (s) => s >= 3.5 ? '#27ae60' : s >= 2.5 ? '#f39c12' : '#e74c3c';

  const domDesc = gunaDescriptions[dominantName];

  // Prepare Secondary Guna
  const sortedGunas = Object.entries(normGuna).sort((a, b) => b[1] - a[1]);
  const secondaryName = sortedGunas[1][0];
  const secondaryPct = (sortedGunas[1][1] * 100).toFixed(1);

  element.innerHTML = `
    <div style="text-align: center; margin-bottom: 30px;">
      <span style="font-size: 3em;">🌟</span>
      <h1 style="color: #2c3e50; margin: 10px 0;">${ui.title}</h1>
      <p style="color: #666; font-style: italic;">${ui.subtitle}</p>
    </div>

    <!-- Triguna Section -->
    <div style="margin-bottom: 40px;">
      <h2 style="border-bottom: 2px solid #eee; padding-bottom: 10px; color: #e67e22;">${ui.triguna_title}</h2>
      
      <div class="results-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 2rem;">
        <!-- Chart -->
        <div style="height: 250px;">
            <canvas id="gunsChart"></canvas>
        </div>
        <!-- Table -->
        <div>
             <table style="width: 100%; border-collapse: collapse; font-size: 0.9em;">
                <thead>
                    <tr style="border-bottom: 2px solid #ddd;">
                        <th style="text-align: left; padding: 6px;">${chartT.Guna}</th>
                        <th style="text-align: center; padding: 6px;">${chartT.Mean}</th>
                        <th style="text-align: center; padding: 6px;">${chartT.Pct}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 6px;">🟡 ${chartT.Sattva}</td>
                        <td style="text-align: center;">${rawGuna.Sattva}</td>
                        <td style="text-align: center;">${(normGuna.Sattva * 100).toFixed(1)}%</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 6px;">🔴 ${chartT.Rajas}</td>
                        <td style="text-align: center;">${rawGuna.Rajas}</td>
                        <td style="text-align: center;">${(normGuna.Rajas * 100).toFixed(1)}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px;">⚫ ${chartT.Tamas}</td>
                        <td style="text-align: center;">${rawGuna.Tamas}</td>
                        <td style="text-align: center;">${(normGuna.Tamas * 100).toFixed(1)}%</td>
                    </tr>
                </tbody>
            </table>
            <p style="text-align: center; font-size: 0.85em; color: #666; margin-top: 10px;">
                ${chartT.Dom}: <strong>${dominantName}</strong> (${dominantPct}%) · ${chartT.Sec}: <strong>${secondaryName}</strong> (${secondaryPct}%)
            </p>
        </div>
      </div>
      
      <div style="background: #fdfdfd; padding: 20px; border-radius: 12px; border-left: 5px solid #e67e22; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-top: 20px;">
        <h3 style="margin-top: 0; color: #d35400;">${domDesc.title}</h3>
        <p style="line-height: 1.6; color: #444;">${domDesc.description}</p>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
            <div style="background: #fff8e1; padding: 10px 15px; border-radius: 8px;">
                <p style="margin: 0; font-weight: bold; color: #8d6e63;">${ui.strengths}</p>
                <ul style="margin: 5px 0 0 20px; color: #5d4037; font-size: 0.9em;">
                    ${domDesc.strengths.map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>

            <div style="background: #e8f5e9; padding: 10px 15px; border-radius: 8px;">
                <p style="margin: 0; font-weight: bold; color: #2e7d32;">${ui.growth}</p>
                <p style="margin: 5px 0 0; color: #1b5e20; font-size: 0.9em;">${domDesc.growth}</p>
            </div>
        </div>

        <p style="margin-top: 12px; font-size: 0.9em; color: #888; font-style: italic; text-align: center;">
            ${domDesc.gita}
        </p>
      </div>
    </div>

    <!-- Big Five Section -->
    <div style="margin-bottom: 40px;">
      <h2 style="border-bottom: 2px solid #eee; padding-bottom: 10px; color: #2980b9;">${ui.bigfive_title}</h2>
      <div style="height: 300px; margin: 20px 0;">
        <canvas id="bigFiveChart"></canvas>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px;">
        ${Object.entries(finalBigFive).map(([trait, score]) => {
    const s = parseFloat(score);
    const level = s >= 3.5 ? 'high' : 'low';
    // Use translated trait name name
    const wTrait = bfDescriptions[trait];
    const desc = wTrait ? wTrait[level] : '';
    const label = chartT[trait] || trait; // Fallback to key
    return `
            <div style="background: #f8fbff; padding: 15px; border-radius: 8px; border: 1px solid #e1e8ed;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <strong style="color: #2c3e50;">${label}</strong>
                    <span style="background: ${getScoreColor(s)}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.85em;">${s.toFixed(1)} / 5</span>
                </div>
                <p style="font-size: 0.9em; color: #555; margin: 0; line-height: 1.5;">${desc}</p>
            </div>
           `;
  }).join('')}
      </div>
    </div>

    <!-- Educational Context -->
    <div style="background: #f4f6f7; padding: 20px; border-radius: 10px; margin-bottom: 30px;">
        <h4 style="margin-top: 0; color: #7f8c8d;">${ui.what_means}</h4>
        <p style="font-size: 0.95em; color: #666; line-height: 1.6;">
            ${ui.what_means_desc}
        </p>
    </div>

    <div style="text-align: center; border-top: 1px solid #eee; padding-top: 20px;">
        <p style="margin-bottom: 20px; color: #27ae60; font-weight: bold;">${ui.thank_you}</p>
        
        <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
            <button id="download-btn" style="background: #34495e; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">${ui.download}</button>
            <button id="restart-btn" style="background: white; color: #34495e; border: 1px solid #34495e; padding: 10px 20px; border-radius: 5px; cursor: pointer;">${ui.take_again}</button>
        </div>
    </div>
  `;

  container.appendChild(element);

  // --- 4. Render Charts ---
  new Chart(document.getElementById('gunsChart'), {
    type: 'doughnut',
    data: {
      labels: [chartT.Sattva, chartT.Rajas, chartT.Tamas],
      datasets: [{
        data: [normGuna.Sattva, normGuna.Rajas, normGuna.Tamas],
        backgroundColor: ['#FFD700', '#FF4500', '#808080'],
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'right' }
      }
    }
  });

  new Chart(document.getElementById('bigFiveChart'), {
    type: 'bar',
    data: {
      labels: Object.keys(finalBigFive).map(trait => chartT[trait] || trait),
      datasets: [{
        label: chartT.Score,
        data: Object.values(finalBigFive),
        backgroundColor: ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#3498db'],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
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

  // Handle Restart
  element.querySelector('#restart-btn').addEventListener('click', () => {
    // We should probably ask for confirmation or just reload
    // But clearing session is good practice if they want to start over?
    // Actually reload() will trigger the main.js logic, which might show Resume/New.
    // So we should explicitely clear session if "Take Again" means "Start New".
    // But "Take Again" usually implies starting fresh.
    // Let's use resetSession() if available, but I didn't import it.
    // I'll just reload for now, the user can choose "Start New" on the next screen if my main.js logic is correct.
    // OR I can navigate to intro.
    location.reload();
  });
}
