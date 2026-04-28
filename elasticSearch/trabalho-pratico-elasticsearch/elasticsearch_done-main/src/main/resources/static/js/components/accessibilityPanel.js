/**
 * @brief Controller for the accessibility settings panel.
 *
 * Manages the floating panel visibility and delegates state changes
 * to the ThemeManager service. Updates button active states to reflect
 * current user preferences.
 *
 * @module accessibilityPanel
 */
import { toggleTheme, toggleContrast, setFontScale, getPreferences } from '../services/themeManager.js';

export class AccessibilityPanel {
  /**
   * @brief Initializes the accessibility panel and binds all controls.
   */
  constructor() {
    this.panel = document.getElementById('a11y-panel');
    this.toggleBtn = document.getElementById('a11y-toggle-btn');
    this.closeBtn = document.getElementById('a11y-panel-close');
    this.isOpen = false;

    if (!this.panel || !this.toggleBtn) return;

    this.bindEvents();
    this.syncState();
  }

  /**
   * @brief Binds click events on all panel controls.
   */
  bindEvents() {
    this.toggleBtn.addEventListener('click', () => this.toggle());
    this.closeBtn?.addEventListener('click', () => this.close());

    /* Theme toggle */
    const themeBtn = document.getElementById('theme-toggle-btn');
    themeBtn?.addEventListener('click', () => {
      const newTheme = toggleTheme();
      this.updateThemeButton(newTheme);
    });

    /* Contrast toggle */
    const contrastBtn = document.getElementById('contrast-toggle-btn');
    contrastBtn?.addEventListener('click', () => {
      const newContrast = toggleContrast();
      this.updateContrastButton(newContrast);
    });

    /* Font scale buttons */
    const fontBtns = document.querySelectorAll('.font-scale-btn');
    fontBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const level = btn.getAttribute('data-scale');
        setFontScale(level);
        this.updateFontButtons(level);
      });
    });

    /* Close when clicking outside */
    document.addEventListener('click', (e) => {
      if (this.isOpen && !this.panel.contains(e.target) && !this.toggleBtn.contains(e.target)) {
        this.close();
      }
    });

    /* Close on Escape */
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) {
        this.close();
      }
    });
  }

  /**
   * @brief Toggles panel visibility.
   */
  toggle() {
    this.isOpen ? this.close() : this.open();
  }

  /**
   * @brief Opens the accessibility panel.
   */
  open() {
    this.panel.classList.add('is-open');
    this.panel.setAttribute('aria-hidden', 'false');
    this.isOpen = true;
  }

  /**
   * @brief Closes the accessibility panel.
   */
  close() {
    this.panel.classList.remove('is-open');
    this.panel.setAttribute('aria-hidden', 'true');
    this.isOpen = false;
  }

  /**
   * @brief Synchronizes button states with stored preferences on init.
   */
  syncState() {
    const prefs = getPreferences();
    this.updateThemeButton(prefs.theme);
    this.updateContrastButton(prefs.contrast);
    this.updateFontButtons(prefs.fontSize);
  }

  /**
   * @brief Updates the theme toggle button icon and label.
   * @param {string} theme - "dark" or "light".
   */
  updateThemeButton(theme) {
    const darkIcon = document.getElementById('theme-icon-dark');
    const lightIcon = document.getElementById('theme-icon-light');
    const label = document.getElementById('theme-label-text');

    if (theme === 'light') {
      darkIcon && (darkIcon.style.display = 'none');
      lightIcon && (lightIcon.style.display = '');
      label && (label.textContent = 'Light');
    } else {
      darkIcon && (darkIcon.style.display = '');
      lightIcon && (lightIcon.style.display = 'none');
      label && (label.textContent = 'Dark');
    }
  }

  /**
   * @brief Updates the contrast toggle button label.
   * @param {string} contrast - "high" or "normal".
   */
  updateContrastButton(contrast) {
    const label = document.getElementById('contrast-label-text');
    const btn = document.getElementById('contrast-toggle-btn');
    if (contrast === 'high') {
      label && (label.textContent = 'High');
      btn?.classList.add('active');
    } else {
      label && (label.textContent = 'Normal');
      btn?.classList.remove('active');
    }
  }

  /**
   * @brief Updates font scale button group active state.
   * @param {string} level - "small", "medium", or "large".
   */
  updateFontButtons(level) {
    document.querySelectorAll('.font-scale-btn').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-scale') === level);
    });
  }
}
