
import { exportSessionData, getStore, submitFeedback } from './dataStore.js';
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

  // Detailed interpretations grounded in Bhagavad Gita (Ch. 14, 17, 18) and Wolf (1998) / Das (1999) research
  const gunaInterpretations = {
    Sattva: {
      emoji: '🧘',
      title: 'Sattva-Pradhāna (Goodness Predominant)',
      description: 'The Gita describes Sattva as "nirmalam" (pure) and "prakāśakam" (illuminating). When Sattva predominates, knowledge arises through all the gates of the body (BG 14.11). You tend toward truthfulness, self-discipline, compassion for all beings, and a natural desire for learning. Wolf (1998) found that Sattva-dominant individuals score higher on life satisfaction, ethical reasoning, and emotional stability.',
      strengths: ['Clarity of thought & wisdom (jñānam — BG 14.17)', 'Inner contentment independent of external things (sukha — BG 14.6)', 'Ethical conduct & truthfulness (dharma-aligned action)', 'Equal respect for all living beings (sama-darśana — BG 5.18)'],
      growth: 'Krishna warns that even Sattva can bind through attachment to happiness and knowledge (BG 14.6). True liberation lies in going beyond all three gunas through devotion and selfless action (nistraiguṇya — BG 14.26).',
      gita: '"सत्त्वात्सञ्जायते ज्ञानम्" — From Sattva, knowledge is born (BG 14.17)'
    },
    Rajas: {
      emoji: '🔥',
      title: 'Rajo-Pradhāna (Passion Predominant)',
      description: 'Krishna describes Rajas as "rāgātmakam" — born of passionate desire and attachment (BG 14.7). When Rajas predominates, there is greed, constant activity, restlessness, and longing (BG 14.12). You are driven by ambition, thrive in competition, and are energized by achievement. Wolf (1998) found that Rajas correlates with materialism, external motivation, and attachment to outcomes.',
      strengths: ['Dynamic energy & capacity for action (pravṛtti — BG 14.12)', 'Strong motivation & goal-pursuit (ārambha — BG 14.12)', 'Leadership initiative & decisiveness', 'Drive that can be channeled toward higher purposes (niṣkāma karma — BG 3.19)'],
      growth: 'The Gita teaches that Rajasic action "bound by attachment to results" leads to suffering (BG 14.16). The remedy is Karma Yoga — performing actions with full energy but without clinging to outcomes: "karmaṇy evādhikāras te mā phaleṣu kadācana" (BG 2.47).',
      gita: '"रजो रागात्मकं विद्धि तृष्णासङ्गसमुद्भवम्" — Know Rajas as born of craving and attachment (BG 14.7)'
    },
    Tamas: {
      emoji: '🌙',
      title: 'Tamo-Pradhāna (Inertia Predominant)',
      description: 'Krishna describes Tamas as "ajñānajam" — born of ignorance, causing delusion in all beings (BG 14.8). When Tamas predominates, there is darkness, inactivity, negligence, and confusion (BG 14.13). This often reflects a phase of life marked by stress, avoidance, or exhaustion rather than a permanent state. Wolf (1998) found that Tamas correlates with depression, low self-efficacy, and avoidance behaviors — but awareness of these patterns is itself a Sattvic quality.',
      strengths: ['Self-awareness of patterns that need change', 'Capacity for deep rest & necessary withdrawal', 'Grounded connection to physical needs', 'Potential for transformative growth when redirected'],
      growth: 'The Gita prescribes cultivating Sattva to overcome Tamas: regulate sleep and wakefulness (BG 6.17), perform duties even without motivation (svadharma — BG 3.35), and associate with Sattvic influences. Even small disciplined actions weaken Tamas progressively: "nābhukto jaṭharo nāsti" — no fire is too small to start.',
      gita: '"तमस्त्वज्ञानजं विद्धि मोहनं सर्वदेहिनाम्" — Know Tamas as born of ignorance, deluding all beings (BG 14.8)'
    }
  };

  const interp = gunaInterpretations[dominantName];

  // Sort gunas for secondary/tertiary
  const sortedGunas = Object.entries(normGuna).sort((a, b) => b[1] - a[1]);
  const secondaryName = sortedGunas[1][0];
  const secondaryPct = (sortedGunas[1][1] * 100).toFixed(1);

  element.innerHTML = `
    <h1 style="margin-bottom: 5px;">Your Personality Profile</h1>
    <p style="color: #777; font-style: italic;">Based on the Triguna model from Bhagavad Gita & modern Big Five psychology</p>
    
    <div class="results-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 2rem;">

        <!-- LEFT: Triguna Profile -->
        <div class="chart-container">
            <h3>Triguna Balance</h3>
            <canvas id="gunaChart"></canvas>

            <table style="width: 100%; margin-top: 12px; border-collapse: collapse; font-size: 0.85em;">
                <thead>
                    <tr style="border-bottom: 2px solid #ddd;">
                        <th style="text-align: left; padding: 6px;">Guna</th>
                        <th style="text-align: center; padding: 6px;">Mean</th>
                        <th style="text-align: center; padding: 6px;">Balance</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 6px;">🟡 Sattva</td>
                        <td style="text-align: center;">${rawGuna.Sattva}/7</td>
                        <td style="text-align: center;">${(normGuna.Sattva * 100).toFixed(1)}%</td>
                    </tr>
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 6px;">🔴 Rajas</td>
                        <td style="text-align: center;">${rawGuna.Rajas}/7</td>
                        <td style="text-align: center;">${(normGuna.Rajas * 100).toFixed(1)}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px;">⚫ Tamas</td>
                        <td style="text-align: center;">${rawGuna.Tamas}/7</td>
                        <td style="text-align: center;">${(normGuna.Tamas * 100).toFixed(1)}%</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- RIGHT: Big Five Profile -->
        <div class="chart-container">
            <h3>Big Five Profile (1-5 Scale)</h3>
            <canvas id="bigFiveChart"></canvas>
            <div style="margin-top:1rem; text-align:center; font-size: 0.9em;">
                ${Object.entries(finalBigFive).map(([k, v]) => `<span><strong>${k}:</strong> ${v}</span>`).join('<br>')}
            </div>
        </div>
    </div>

    <!-- INTERPRETATION SECTION -->
    <div style="margin-top: 2.5rem; background: linear-gradient(135deg, #fafbfc, #f0f4f8); border-radius: 12px; padding: 24px; border: 1px solid #e1e8ed;">
        
        <div style="text-align: center; margin-bottom: 16px;">
            <span style="font-size: 2.5em;">${interp.emoji}</span>
            <h2 style="margin: 8px 0 4px; color: #2c3e50;">${interp.title}</h2>
            <p style="color: #888; font-size: 0.9em;">Dominant: <strong>${dominantName}</strong> (${dominantPct}%) · Secondary: <strong>${secondaryName}</strong> (${secondaryPct}%)</p>
        </div>

        <p style="line-height: 1.7; color: #444; text-align: center; max-width: 600px; margin: 0 auto 20px;">${interp.description}</p>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px;">
            <div style="background: white; padding: 16px; border-radius: 10px; border-left: 4px solid #27ae60;">
                <p style="font-weight: bold; margin: 0 0 8px; color: #27ae60;">✨ Your Strengths</p>
                <ul style="margin: 0; padding-left: 18px; line-height: 1.8; font-size: 0.9em; color: #555;">
                    ${interp.strengths.map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>
            <div style="background: white; padding: 16px; border-radius: 10px; border-left: 4px solid #e67e22;">
                <p style="font-weight: bold; margin: 0 0 8px; color: #e67e22;">🌱 Path Forward</p>
                <p style="margin: 0; line-height: 1.7; font-size: 0.9em; color: #555;">${interp.growth}</p>
            </div>
        </div>

        <div style="text-align: center; margin-top: 20px; padding: 12px; background: #fff9e6; border-radius: 8px; border: 1px solid #f0e0a0;">
            <p style="margin: 0; font-style: italic; color: #8B7D3C; font-size: 0.95em;">📖 ${interp.gita}</p>
        </div>
    </div>

    <!-- WHAT THIS MEANS -->
    <div style="margin-top: 2rem; padding: 20px; background: #f8f9fa; border-radius: 10px; text-align: center;">
        <h3 style="color: #2c3e50; margin-top: 0;">🔬 What does this mean?</h3>
        <p style="color: #666; line-height: 1.7; max-width: 600px; margin: 0 auto;">
            The Triguna are not permanent labels — they are tendencies that shift with your lifestyle, habits, and awareness. 
            <strong>Everyone has all three gunas.</strong> The goal is not to eliminate Rajas or Tamas, but to cultivate 
            <strong>Sattva as the guiding force</strong> while using Rajasic energy for action and Tamasic rest for recovery.
        </p>
    </div>

    <!-- BIG FIVE INTERPRETATION -->
    <div style="margin-top: 2rem; background: linear-gradient(135deg, #f0f4ff, #e8f0fe); border-radius: 12px; padding: 24px; border: 1px solid #d0daf0;">
        <h2 style="text-align: center; color: #2c3e50; margin-top: 0;">🧠 Your Big Five Profile</h2>
        <p style="text-align: center; color: #888; font-size: 0.85em; margin-bottom: 20px;">Based on the BFI-10 (Rammstedt & John, 2007) — the most widely validated personality model in psychology (Costa & McCrae, 1992)</p>
        <div id="bf-interp-container"></div>
    </div>

    <!-- FEEDBACK SECTION -->
    <div style="margin-top: 2rem; background: #fff; border-radius: 12px; padding: 24px; border: 1px solid #e1e8ed; text-align: center;">
        <h3 style="margin-top: 0; color: #2c3e50;">💡 Help Us Improve</h3>
        <p style="color: #666; font-size: 0.9em; margin-bottom: 15px;">Do you have any suggestions or feedback for us?</p>
        
        <div id="feedback-form">
            <textarea id="feedback-text" rows="3" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-family: inherit; resize: vertical;" placeholder="Type your suggestions here..."></textarea>
            <button id="feedback-btn" style="margin-top: 10px; background: #34495e; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer;">Submit Feedback</button>
        </div>
        <div id="feedback-success" style="display: none; color: #27ae60; font-weight: bold; margin-top: 10px;">
            ✅ Thank you! Your feedback has been recorded.
        </div>
    </div>

    <!-- FEEDBACK SECTION -->
    <div style="margin-top: 2rem; background: #fff; border-radius: 12px; padding: 24px; border: 1px solid #e1e8ed; text-align: center;">
        <h3 style="margin-top: 0; color: #2c3e50;">💡 Help Us Improve</h3>
        <p style="color: #666; font-size: 0.9em; margin-bottom: 15px;">Do you have any suggestions or feedback for us?</p>
        
        <div id="feedback-form">
            <textarea id="feedback-text" rows="3" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 8px; font-family: inherit; resize: vertical;" placeholder="Type your suggestions here..."></textarea>
            <button id="feedback-btn" style="margin-top: 10px; background: #34495e; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer;">Submit Feedback</button>
        </div>
        <div id="feedback-success" style="display: none; color: #27ae60; font-weight: bold; margin-top: 10px;">
            ✅ Thank you! Your feedback has been recorded.
        </div>
    </div>

    <div style="margin-top: 2rem; text-align: center;">
        <p style="color: #888;">Thank you for contributing to this research! 🙏</p>
        
        <!-- Viral Loop: Share Button -->
        <button id="share-btn" style="background: linear-gradient(135deg, #8e44ad, #9b59b6); border: none; margin-right: 1rem;">
            📤 Share My Profile
        </button>

        <button id="download-btn">Download Data (JSON)</button>
        <button class="secondary" onclick="location.reload()" style="margin-left: 1rem;">Take Again</button>
    </div>
  `;

  container.appendChild(element);

  // --- 4. Gamification / Comparison (Simulated from N=80) ---
  const populationStats = {
    Sattva: { mean: 5.00, sd: 0.91 },
    Rajas: { mean: 3.94, sd: 0.96 },
    Tamas: { mean: 3.09, sd: 1.17 }
  };

  function getPercentile(score, mean, sd) {
    const z = (score - mean) / sd;
    // Approximation of CDF for normal distribution
    const p = 0.5 * (1 + Math.erf(z / Math.sqrt(2)));
    return Math.round(p * 100);
  }

  // Calculate user percentiles
  const pSattva = getPercentile(parseFloat(rawGuna.Sattva), populationStats.Sattva.mean, populationStats.Sattva.sd);
  const pRajas = getPercentile(parseFloat(rawGuna.Rajas), populationStats.Rajas.mean, populationStats.Rajas.sd);
  // For Tamas, lower is usually "better" (less inertia), but higher means more of the trait.
  // We'll frame it neutrally: "Higher than X%"
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
  comparisonCard.style.cssText = 'margin-top: 2rem; padding: 20px; background: #fff; border: 2px dashed #ccc; border-radius: 12px; text-align: center;';
  comparisonCard.innerHTML = `
    <h3 style="margin-top: 0; color: #555;">📊 How do you compare?</h3>
    <p style="font-size: 0.9em; color: #777;">Compared to University Average (N=80)</p>
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

  // Insert before the share button container (which is the last child of container usually)
  container.insertBefore(comparisonCard, container.lastChild);


  // --- Share Functionality ---
  const shareBtn = element.querySelector('#share-btn');
  shareBtn.addEventListener('click', async () => {
    // Use the smart stat if available, else default text
    const smartText = shareStat ? `${shareStat}\n\nMy Dominant Guna: ${dominantName}` : `I discovered my cognitive architecture! 🧠\n\nMy Dominant Guna: ${dominantName}`;

    const shareData = {
      title: 'My Guna Personality Profile',
      text: `${smartText}\n\nDiscover your profile here:`,
      url: 'https://manideepdonkena.github.io/gpi-student-assessment/'
    };

    try {
      if (navigator.share) {
        await navigator.share(shareData);
      } else {
        // Fallback for desktop
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

  // --- Build Big Five Interpretations (imperative, avoids nested template literal issue) ---
  const bfDescriptions = {
    Extraversion: {
      high: 'You are outgoing, energetic, and draw energy from social interactions. Research links high extraversion with positive emotions and leadership emergence (Judge et al., 2002).',
      low: 'You prefer solitude or small groups and recharge through quiet reflection. Introverts tend to show deeper focus and more deliberate decision-making (Cain, 2012).',
      icon: '🗣️'
    },
    Agreeableness: {
      high: 'You are trusting, cooperative, and considerate of others. High agreeableness predicts better teamwork and relationship satisfaction (Graziano & Tobin, 2009).',
      low: 'You are more competitive and skeptical, prioritizing logic over social harmony. This can predict stronger negotiation outcomes and critical thinking (Costa & McCrae, 1992).',
      icon: '🤝'
    },
    Conscientiousness: {
      high: 'You are organized, disciplined, and goal-directed. Conscientiousness is the strongest Big Five predictor of academic and job performance (Barrick & Mount, 1991).',
      low: 'You are flexible and spontaneous, preferring to adapt rather than plan rigidly. This can foster creativity but may benefit from external structure (Costa & McCrae, 1992).',
      icon: '📋'
    },
    Neuroticism: {
      high: 'You experience emotions intensely and may be more sensitive to stress. This heightened awareness can drive vigilance and empathy, but managing stress is important (Barlow et al., 2014).',
      low: 'You are emotionally stable and resilient under pressure. Low neuroticism is consistently linked to better stress management and well-being (Costa & McCrae, 1992).',
      icon: '🌊'
    },
    Openness: {
      high: 'You are curious, imaginative, and open to new experiences. High openness predicts creativity, intellectual engagement, and appreciation for art and ideas (McCrae, 1987).',
      low: 'You prefer practical, conventional approaches and value consistency. This predicts reliability and comfort with established routines (Costa & McCrae, 1992).',
      icon: '🎨'
    }
  };

  const bfContainer = element.querySelector('#bf-interp-container');
  Object.entries(finalBigFive).forEach(([trait, score]) => {
    const s = parseFloat(score);
    const info = bfDescriptions[trait];
    if (!info) return;
    const level = s >= 3.5 ? 'high' : 'low';
    const label = s >= 3.5 ? 'High' : s >= 2.5 ? 'Moderate' : 'Low';
    const barColor = s >= 3.5 ? '#3498db' : s >= 2.5 ? '#95a5a6' : '#e74c3c';

    const card = document.createElement('div');
    card.style.cssText = 'background: white; border-radius: 10px; padding: 14px 16px; margin-bottom: 10px; border-left: 4px solid ' + barColor;
    card.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <strong style="color: #2c3e50;">${info.icon} ${trait}</strong>
        <span style="background: ${barColor}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.8em;">${label} (${score}/5)</span>
      </div>
      <p style="margin: 0; font-size: 0.85em; line-height: 1.6; color: #555;">${info[level]}</p>
    `;
    bfContainer.appendChild(card);
  });

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
              return `${guna}: ${pct}% (Mean: ${rawGuna[guna]}/7)`;
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
