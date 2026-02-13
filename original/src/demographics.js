
import { setDemographics } from './dataStore.js';
import { renderRoute } from './main.js';
import { translations } from './translations.js';

export function renderDemographics(container) {
  const lang = localStorage.getItem('gpi_lang') || 'en';
  const t = translations[lang] || translations['en'];
  const ui = t.demographics;

  const element = document.createElement('div');
  element.className = 'card fade-in';

  element.innerHTML = `
    <h1>${ui.title}</h1>
    <p>${ui.desc}</p>
    
    <form id="demo-form">
      <label>
        ${ui.age}
        <input type="number" name="age" required min="14" max="80" placeholder="e.g., 21">
      </label>
      
      <label>
        ${ui.gender}
        <select name="gender" required>
          <option value="">${ui.select}</option>
          <option value="Male">${ui.male}</option>
          <option value="Female">${ui.female}</option>
          <option value="Non-binary">${ui.nonbinary}</option>
          <option value="Prefer not to say">${ui.prefer_not}</option>
        </select>
      </label>

      <label>
        ${ui.education}
        <select name="education" required>
          <option value="">${ui.select}</option>
          <option value="High School">${ui.highschool}</option>
          <option value="UG (Pursuing)">${ui.ug_pursuing}</option>
          <option value="UG (Completed)">${ui.ug_completed}</option>
          <option value="PG (Pursuing)">${ui.pg_pursuing}</option>
          <option value="PG (Completed)">${ui.pg_completed}</option>
          <option value="PhD">${ui.phd}</option>
          <option value="Other">${ui.other}</option>
        </select>
      </label>

      <label>
        ${ui.occupation}
        <select name="occupation" id="occupation-select" required>
          <option value="">${ui.select}</option>
          <option value="Student">${ui.student}</option>
          <option value="Working Professional">${ui.professional}</option>
          <option value="Self-employed">${ui.self_employed}</option>
          <option value="Homemaker">${ui.homemaker}</option>
          <option value="Retired">${ui.retired}</option>
          <option value="Other">${ui.other}</option>
        </select>
      </label>

      <!-- Conditional Fields: Student -->
      <div id="student-fields" style="display: none;">
        <label>
          Year of Study
          <select name="year">
            <option value="">${ui.select}</option>
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
            <option value="">${ui.select}</option>
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
            <option value="">${ui.select}</option>
            <option value="0-2">0 - 2 years</option>
            <option value="3-5">3 - 5 years</option>
            <option value="6-10">6 - 10 years</option>
            <option value="10+">10+ years</option>
          </select>
        </label>
      </div>

      <!-- Universal Fields -->
      <label>
        ${ui.spiritual}
        <select name="spiritualPractice" required>
          <option value="">${ui.select}</option>
          <option value="Regular">${ui.regular}</option>
          <option value="Occasional">${ui.occasional}</option>
          <option value="Rarely">${ui.rarely}</option>
          <option value="Never">${ui.never}</option>
        </select>
      </label>

      <label>
        ${ui.gita}
        <select name="gitaFamiliarity" required>
          <option value="">${ui.select}</option>
          <option value="Very Familiar">${ui.familiar_very}</option>
          <option value="Somewhat">${ui.familiar_some}</option>
          <option value="Heard of it">${ui.familiar_heard}</option>
          <option value="Not at all">${ui.familiar_not}</option>
        </select>
      </label>
      
      <button type="submit">${ui.start_btn}</button>
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
