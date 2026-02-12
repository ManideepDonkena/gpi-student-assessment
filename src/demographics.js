
import { setDemographics } from './dataStore.js';
import { renderRoute } from './main.js';

export function renderDemographics(container) {
  const element = document.createElement('div');
  element.className = 'card fade-in';

  element.innerHTML = `
    <h1>About You</h1>
    <p>Help us understand your background. All data is <strong>anonymous</strong> and used only for research.</p>
    
    <form id="demo-form">
      <label>
        Age
        <input type="number" name="age" required min="14" max="80" placeholder="e.g., 21">
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
        Highest Education
        <select name="education" required>
          <option value="">Select...</option>
          <option value="High School">High School / 12th</option>
          <option value="UG (Pursuing)">Undergraduate (Pursuing)</option>
          <option value="UG (Completed)">Undergraduate (Completed)</option>
          <option value="PG (Pursuing)">Postgraduate (Pursuing)</option>
          <option value="PG (Completed)">Postgraduate (Completed)</option>
          <option value="PhD">PhD / Doctorate</option>
          <option value="Other">Other</option>
        </select>
      </label>

      <label>
        Current Occupation
        <select name="occupation" id="occupation-select" required>
          <option value="">Select...</option>
          <option value="Student">Student</option>
          <option value="Working Professional">Working Professional</option>
          <option value="Self-employed">Self-employed / Business</option>
          <option value="Homemaker">Homemaker</option>
          <option value="Retired">Retired</option>
          <option value="Other">Other</option>
        </select>
      </label>

      <!-- Conditional Fields: Student -->
      <div id="student-fields" style="display: none;">
        <label>
          Year of Study
          <select name="year">
            <option value="">Select...</option>
            <option value="1">1st Year</option>
            <option value="2">2nd Year</option>
            <option value="3">3rd Year</option>
            <option value="4">4th Year</option>
            <option value="PG">Post-Graduate</option>
            <option value="PhD">PhD</option>
          </select>
        </label>

        <label>
          Major / Stream
          <input type="text" name="major" placeholder="e.g., Computer Science, Psychology">
        </label>

        <label>
          Latest GPA / CPI / Percentage (approx)
          <input type="number" name="gpa" step="0.1" placeholder="e.g., 8.5 or 85">
        </label>
      </div>

      <!-- Conditional Fields: Working Professional -->
      <div id="professional-fields" style="display: none;">
        <label>
          Industry / Field
          <select name="industry">
            <option value="">Select...</option>
            <option value="IT / Software">IT / Software</option>
            <option value="Education">Education / Academia</option>
            <option value="Healthcare">Healthcare</option>
            <option value="Finance">Finance / Banking</option>
            <option value="Engineering">Engineering / Manufacturing</option>
            <option value="Government">Government / Public Sector</option>
            <option value="Business">Business / Consulting</option>
            <option value="Creative / Media">Creative / Media</option>
            <option value="Other">Other</option>
          </select>
        </label>

        <label>
          Years of Experience
          <select name="experience">
            <option value="">Select...</option>
            <option value="0-2">0 - 2 years</option>
            <option value="3-5">3 - 5 years</option>
            <option value="6-10">6 - 10 years</option>
            <option value="10+">10+ years</option>
          </select>
        </label>
      </div>

      <!-- Universal Fields -->
      <label>
        Spiritual / Meditation Practice
        <select name="spiritualPractice" required>
          <option value="">Select...</option>
          <option value="Regular">Regular (Daily / Weekly)</option>
          <option value="Occasional">Occasional</option>
          <option value="Rarely">Rarely</option>
          <option value="Never">Never</option>
        </select>
      </label>

      <label>
        Familiarity with Bhagavad Gita / Vedantic Philosophy
        <select name="gitaFamiliarity" required>
          <option value="">Select...</option>
          <option value="Very Familiar">Very Familiar (Read / Studied)</option>
          <option value="Somewhat">Somewhat Familiar</option>
          <option value="Heard of it">Heard of it</option>
          <option value="Not at all">Not at all</option>
        </select>
      </label>
      
      <button type="submit">Start Assessment</button>
    </form>
  `;

  // --- Conditional Field Logic ---
  const form = element.querySelector('form');
  const occupationSelect = element.querySelector('#occupation-select');
  const studentFields = element.querySelector('#student-fields');
  const professionalFields = element.querySelector('#professional-fields');

  occupationSelect.addEventListener('change', () => {
    const val = occupationSelect.value;

    // Hide all conditional fields
    studentFields.style.display = 'none';
    professionalFields.style.display = 'none';

    // Remove required from hidden fields
    studentFields.querySelectorAll('input, select').forEach(el => el.removeAttribute('required'));
    professionalFields.querySelectorAll('input, select').forEach(el => el.removeAttribute('required'));

    if (val === 'Student') {
      studentFields.style.display = 'block';
    } else if (val === 'Working Professional' || val === 'Self-employed') {
      professionalFields.style.display = 'block';
    }
  });

  // --- Handle Submit ---
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    const demographics = {
      age: formData.get('age'),
      gender: formData.get('gender'),
      education: formData.get('education'),
      occupation: formData.get('occupation'),
      spiritualPractice: formData.get('spiritualPractice'),
      gitaFamiliarity: formData.get('gitaFamiliarity')
    };

    // Add conditional fields based on occupation
    const occupation = formData.get('occupation');
    if (occupation === 'Student') {
      demographics.year = formData.get('year');
      demographics.major = formData.get('major');
      demographics.gpa = formData.get('gpa');
    } else if (occupation === 'Working Professional' || occupation === 'Self-employed') {
      demographics.industry = formData.get('industry');
      demographics.experience = formData.get('experience');
    }

    setDemographics(demographics);
    renderRoute();
  });

  container.appendChild(element);
}
