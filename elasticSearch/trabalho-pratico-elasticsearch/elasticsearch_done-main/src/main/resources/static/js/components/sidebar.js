/**
 * @brief Controller for the hyperparameter tuning sidebar.
 *
 * Handles drawer interactions, form submission for tuning query params,
 * and live updates of range slider values.
 *
 * @module sidebar
 */
export class Sidebar {
  constructor() {
    this.sidebar = document.getElementById('sidebar');
    this.backdrop = document.getElementById('sidebar-backdrop');
    this.openBtn = document.getElementById('hamburger-btn');
    this.closeBtn = document.getElementById('sidebar-close-btn');
    
    this.form = document.getElementById('tuning-form');
    this.resetBtn = document.getElementById('reset-tuning-btn');
    
    this.isOpen = false;

    if (!this.sidebar || !this.openBtn) return;
    this.bindEvents();
    this.bindSliders();
    this.bindForm();
  }

  bindEvents() {
    this.openBtn.addEventListener('click', () => this.open());
    this.closeBtn?.addEventListener('click', () => this.close());
    this.backdrop?.addEventListener('click', () => this.close());

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) {
        this.close();
      }
    });
  }

  bindSliders() {
    /* Update label values dynamically when dragging sliders */
    ['slop', 'phraseBoost', 'titleBoost'].forEach(id => {
      const input = document.getElementById(id);
      const valDisplay = document.getElementById(`${id}-val`);
      if (input && valDisplay) {
        input.addEventListener('input', (e) => {
          let val = e.target.value;
          /* Ensure float display for boosts */
          if (id.includes('Boost') && !val.includes('.')) {
            val += '.0';
          }
          valDisplay.textContent = val;
        });
      }
    });
  }

  bindForm() {
    if (!this.form) return;

    /* Handle unchecked checkboxes before submit */
    this.form.addEventListener('submit', () => {
      const highlightBox = document.getElementById('highlight');
      const highlightHidden = document.getElementById('highlight-hidden');
      if (highlightBox && highlightHidden) {
        highlightHidden.disabled = highlightBox.checked;
      }

      const spellBox = document.getElementById('spellCheck');
      const spellHidden = document.getElementById('spellCheck-hidden');
      if (spellBox && spellHidden) {
        spellHidden.disabled = spellBox.checked;
      }
    });

    /* Handle reset defaults */
    this.resetBtn?.addEventListener('click', () => {
      document.getElementById('fuzziness').value = 'AUTO';
      
      const pBoost = document.getElementById('phraseBoost');
      pBoost.value = '2.0';
      document.getElementById('phraseBoost-val').textContent = '2.0';
      
      const tBoost = document.getElementById('titleBoost');
      tBoost.value = '1.5';
      document.getElementById('titleBoost-val').textContent = '1.5';
      
      const slop = document.getElementById('slop');
      slop.value = '0';
      document.getElementById('slop-val').textContent = '0';
      
      document.getElementById('highlight').checked = true;
      document.getElementById('spellCheck').checked = true;
      
      this.form.submit();
    });
  }

  open() {
    this.sidebar.classList.add('is-open');
    this.backdrop.classList.add('is-visible');
    this.sidebar.setAttribute('aria-hidden', 'false');
    this.isOpen = true;
    document.body.style.overflow = 'hidden';
    this.closeBtn?.focus();
  }

  close() {
    this.sidebar.classList.remove('is-open');
    this.backdrop.classList.remove('is-visible');
    this.sidebar.setAttribute('aria-hidden', 'true');
    this.isOpen = false;
    document.body.style.overflow = '';
    this.openBtn?.focus();
  }
}
