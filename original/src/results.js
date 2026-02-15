import { exportSessionData, getStore, submitFeedback } from './dataStore.js';
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

    <div id="results-footer" style="text-align: center; border-top: 1px solid #eee; padding-top: 20px;">
        <p style="margin-bottom: 20px; color: #27ae60; font-weight: bold;">${ui.thank_you}</p>
        
        <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
            <button id="download-btn" style="background: #34495e; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">${ui.download}</button>
            <button id="restart-btn" style="background: white; color: #34495e; border: 1px solid #34495e; padding: 10px 20px; border-radius: 5px; cursor: pointer;">${ui.take_again}</button>
        </div>
    </div>
  `;

  container.appendChild(element);

  // Helper to find footer for insertion
  const footer = element.querySelector('#results-footer');

  // --- 4. Gamification / Comparison (Calculated from N=84) ---
  const populationStats = {
    Sattva: { mean: 4.88, sd: 0.95 },
    Rajas: { mean: 3.84, sd: 1.17 },
    Tamas: { mean: 3.07, sd: 1.17 }
  };

  function erf(x) {
    // Save the sign of x
    var sign = (x >= 0) ? 1 : -1;
    x = Math.abs(x);

    // Constants for A&S formula 7.1.26
    var a1 = 0.254829592;
    var a2 = -0.284496736;
    var a3 = 1.421413741;
    var a4 = -1.453152027;
    var a5 = 1.061405429;
    var p = 0.3275911;

    var t = 1.0 / (1.0 + p * x);
    var y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);
    return sign * y;
  }

  function getPercentile(score, mean, sd) {
    const z = (score - mean) / sd;
    const p = 0.5 * (1 + erf(z / Math.sqrt(2)));
    return Math.round(p * 100);
  }

  // Calculate user percentiles
  const pSattva = getPercentile(parseFloat(rawGuna.Sattva), populationStats.Sattva.mean, populationStats.Sattva.sd);
  const pRajas = getPercentile(parseFloat(rawGuna.Rajas), populationStats.Rajas.mean, populationStats.Rajas.sd);
  const pTamas = getPercentile(parseFloat(rawGuna.Tamas), populationStats.Tamas.mean, populationStats.Tamas.sd);

  // Generate a "Badge"
  let badgeHTML = '';
  let shareStat = '';

  if (pSattva >= 80) {
    badgeHTML = `<div style="background: #eaffea; border: 1px solid #27ae60; color: #27ae60; padding: 10px; border-radius: 8px; display: inline-block; margin-bottom: 15px;">🏆 <strong>Top ${100 - pSattva}%</strong> in Sattva (Harmonious Balance)</div>`;
    shareStat = `I'm in the Top ${100 - pSattva}% for Focus & Balance (Sattva)! 🧘‍♂️`;
  } else if (pRajas >= 80) {
    badgeHTML = `<div style="background: #fff0eb; border: 1px solid #e74c3c; color: #e74c3c; padding: 10px; border-radius: 8px; display: inline-block; margin-bottom: 15px;">🔥 <strong>Top ${100 - pRajas}%</strong> in Rajas (Passion & Drive)</div>`;
    shareStat = `I have higher Drive (Rajas) than ${pRajas}% of students! 🔥`;
  } else if (pTamas <= 20) {
    badgeHTML = `<div style="background: #f0f4f8; border: 1px solid #34495e; color: #34495e; padding: 10px; border-radius: 8px; display: inline-block; margin-bottom: 15px;">⚡ <strong>Top ${pTamas}%</strong> in Energy (Low Inertia)</div>`;
    shareStat = `I have less Inertia (Tamas) than ${100 - pTamas}% of students! ⚡`;
  }

  // Add Comparison Card to UI
  const comparisonCard = document.createElement('div');
  comparisonCard.style.cssText = 'margin-top: 2rem; margin-bottom: 2rem; padding: 20px; background: #fff; border: 2px dashed #ccc; border-radius: 12px; text-align: center;';
  comparisonCard.innerHTML = `
    <h3 style="margin-top: 0; color: #555;">📊 How do you compare?</h3>
    <p style="font-size: 0.9em; color: #777;">Compared to University Average (N=84)</p>
    ${badgeHTML}
    <div style="display: flex; justify-content: space-around; margin-top: 10px; font-size: 0.9em;">
        <div>
            <strong>Sattva</strong><br>
            You are higher than<br>
            <span style="font-size: 1.2em; color: #27ae60; font-weight: bold;">${pSattva}%</span> of peers
        </div>
        <div>
            <strong>Rajas</strong><br>
            You are higher than<br>
            <span style="font-size: 1.2em; color: #e67e22; font-weight: bold;">${pRajas}%</span> of peers
        </div>
    </div>
  `;
  // Insert BEFORE footer
  element.insertBefore(comparisonCard, footer);

  // --- Feedback Functionality ---
  const feedbackCard = document.createElement('div');
  feedbackCard.style.cssText = 'margin-top: 2rem; margin-bottom: 2rem; background: #fff; border-radius: 12px; padding: 24px; border: 1px solid #e1e8ed; text-align: center;';
  feedbackCard.innerHTML = `
        <h3 style="margin-top: 0; color: #2c3e50;">💡 Help Us Improve</h3>
        <p style="color: #666; font-size: 0.9em; margin-bottom: 15px;">Do you have any suggestions or feedback for us?</p>
        
        <div id="feedback-form">
            <textarea id="feedback-text" rows="3" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-family: inherit; resize: vertical;" placeholder="Type your suggestions here..."></textarea>
            <button id="feedback-btn" style="margin-top: 10px; background: #34495e; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer;">Submit Feedback</button>
        </div>
        <div id="feedback-success" style="display: none; color: #27ae60; font-weight: bold; margin-top: 10px;">
            ✅ Thank you! Your feedback has been recorded.
        </div>
  `;
  // Insert BEFORE footer (after comparisonCard)
  element.insertBefore(feedbackCard, footer);

  // Add event listener for feedback
  const feedbackBtn = feedbackCard.querySelector('#feedback-btn');
  const feedbackText = feedbackCard.querySelector('#feedback-text');
  const feedbackForm = feedbackCard.querySelector('#feedback-form');
  const feedbackSuccess = feedbackCard.querySelector('#feedback-success');

  feedbackBtn.addEventListener('click', async () => {
    const text = feedbackText.value.trim();
    await submitFeedback(text || "No suggestions provided");
    feedbackForm.style.display = 'none';
    feedbackSuccess.style.display = 'block';
  });

  // --- Share Functionality ---
  // Create Share Button and inject into the button container
  const buttonContainer = element.querySelector('#download-btn').parentNode;
  const shareBtn = document.createElement('button');
  shareBtn.id = 'share-btn';
  shareBtn.style.cssText = 'background: linear-gradient(135deg, #8e44ad, #9b59b6); border: none; margin-right: 1rem; color: white; padding: 10px 20px; border-radius: 5px; cursor: pointer;';
  shareBtn.innerHTML = '📤 Share My Profile';

  // Insert as first button
  buttonContainer.insertBefore(shareBtn, buttonContainer.firstChild);

  shareBtn.addEventListener('click', async () => {
    const smartText = shareStat ? `${shareStat}\n\nMy Dominant Guna: ${dominantName}` : `I discovered my cognitive architecture! 🧠\n\nMy Dominant Guna: ${dominantName}`;
    const shareData = {
      title: 'My Guna Personality Profile',
      text: `${smartText}\n\nDiscover your profile here:`,
      url: 'https://manideepdonkena.github.io/gpi-student-assessment/original/'
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
      } else {
        const textToCopy = `${shareData.text} ${shareData.url}`;
        await navigator.clipboard.writeText(textToCopy);
        const originalText = shareBtn.innerHTML;
        shareBtn.innerHTML = "✅ Copied to Clipboard!";
        setTimeout(() => shareBtn.innerHTML = originalText, 2000);
      }
    } catch (err) {
      console.error('Error sharing:', err);
    }
  });


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

  // Handle PDF Download
  const downloadBtn = element.querySelector('#download-btn');
  downloadBtn.innerHTML = "📄 Download Report"; // Update text

  downloadBtn.addEventListener('click', () => {
    // Hide footer (buttons) and feedback for PDF
    const footer = element.querySelector('#results-footer');

    footer.style.display = 'none';
    feedbackCard.style.display = 'none';

    // Temporarily remove animation and shadow for clean print
    const originalAnimation = element.style.animation;
    const originalBoxShadow = element.style.boxShadow;
    element.style.animation = 'none';
    element.style.boxShadow = 'none';

    const opt = {
      margin: [10, 10, 10, 10],
      filename: `Guna_Profile_${getStore().state.sessionId.slice(0, 6)}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true, scrollY: 0 },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
      pagebreak: { mode: ['avoid-all', 'css', 'legacy'] }
    };

    // Generate PDF
    html2pdf().set(opt).from(element).save().then(() => {
      // Restore styles and buttons
      element.style.animation = originalAnimation;
      element.style.boxShadow = originalBoxShadow;
      footer.style.display = 'block';
      feedbackCard.style.display = 'block';
    });
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
