
import { setDemographics } from './dataStore.js';
import { renderRoute } from './main.js';

export function renderDemographics(container) {
  const element = document.createElement('div');
  element.className = 'card fade-in';

  element.innerHTML = `
    <h1>Student Self-Assessment Protocol</h1>
    <p>This study explores decision-making styles and personality traits in academic settings. Please answer honestly.</p>
    
    <form id="demo-form">
      <label>
        Age
        <input type="number" name="age" required min="16" max="40">
      </label>
      
      <label>
        Gender
        <select name="gender" required>
          <option value="">Select...</option>
          <option value="Male">Male</option>
          <option value="Female">Female</option>
          <option value="Non-binary">Non-binary</option>
          <option value="Prefer not to say">Prefer not to say</option>
        </select>
      </label>
      
      <label>
        Year of Study
        <select name="year" required>
          <option value="">Select...</option>
          <option value="1">1st Year</option>
          <option value="2">2nd Year</option>
          <option value="3">3rd Year</option>
          <option value="4">4th Year</option>
          <option value="PG">Post-Graduate</option>
        </select>
      </label>

      <label>
        Major / Stream
        <input type="text" name="major" placeholder="e.g., Computer Science, Psychology" required>
      </label>

      <label>
        Latest GPA / Percentage (approx)
        <input type="number" name="gpa" step="0.1" placeholder="e.g. 8.5 or 85" required>
      </label>
      
      <button type="submit">Start Assessment</button>
    </form>
  `;

  element.querySelector('form').addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    setDemographics({
      age: formData.get('age'),
      gender: formData.get('gender'),
      year: formData.get('year'),
      major: formData.get('major'),
      gpa: formData.get('gpa')
    });
    renderRoute();
  });

  container.appendChild(element);
}
