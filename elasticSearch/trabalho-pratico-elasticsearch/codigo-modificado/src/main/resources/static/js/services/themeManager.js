/**
 * @brief Singleton service for managing theme, contrast, and font scale preferences.
 *
 * Persists user preferences to localStorage and respects the system
 * prefers-color-scheme media query on first visit. Applies all state
 * via data attributes on the document root element.
 *
 * @module themeManager
 */

const STORAGE_KEY = 'pinakes-preferences';

const FONT_SCALES = {
  small:  0.875,
  medium: 1,
  large:  1.125
};

/**
 * @brief Reads saved preferences from localStorage.
 * @returns {Object} Stored preferences or empty object.
 */
function loadPreferences() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

/**
 * @brief Persists the given preferences object to localStorage.
 * @param {Object} prefs - The preferences to save.
 */
function savePreferences(prefs) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
  } catch {
    /* Storage unavailable -- fail silently */
  }
}

/**
 * @brief Detects the user's preferred color scheme from the OS.
 * @returns {string} "light" or "dark".
 */
function detectSystemTheme() {
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    return 'light';
  }
  return 'dark';
}

/**
 * @brief Applies all current preferences to the document root element.
 * @param {Object} prefs - Object with theme, contrast, and fontSize keys.
 */
function applyPreferences(prefs) {
  const root = document.documentElement;

  root.setAttribute('data-theme', prefs.theme || 'dark');

  if (prefs.contrast === 'high') {
    root.setAttribute('data-contrast', 'high');
  } else {
    root.removeAttribute('data-contrast');
  }

  const scale = FONT_SCALES[prefs.fontSize] || FONT_SCALES.medium;
  root.style.setProperty('--font-scale', scale);
}

/** @type {Object} Current in-memory preferences. */
let currentPrefs = {};

/**
 * @brief Initializes the theme manager on page load.
 *
 * Reads stored preferences, falls back to system theme detection,
 * and applies the resolved state to the DOM.
 */
export function initThemeManager() {
  currentPrefs = loadPreferences();

  if (!currentPrefs.theme) {
    currentPrefs.theme = detectSystemTheme();
  }
  if (!currentPrefs.fontSize) {
    currentPrefs.fontSize = 'medium';
  }
  if (!currentPrefs.contrast) {
    currentPrefs.contrast = 'normal';
  }

  applyPreferences(currentPrefs);
}

/**
 * @brief Toggles between dark and light themes.
 * @returns {string} The new active theme ("dark" or "light").
 */
export function toggleTheme() {
  currentPrefs.theme = currentPrefs.theme === 'dark' ? 'light' : 'dark';
  applyPreferences(currentPrefs);
  savePreferences(currentPrefs);
  return currentPrefs.theme;
}

/**
 * @brief Toggles high contrast mode on or off.
 * @returns {string} The new contrast state ("high" or "normal").
 */
export function toggleContrast() {
  currentPrefs.contrast = currentPrefs.contrast === 'high' ? 'normal' : 'high';
  applyPreferences(currentPrefs);
  savePreferences(currentPrefs);
  return currentPrefs.contrast;
}

/**
 * @brief Sets the font scale level.
 * @param {string} level - One of "small", "medium", or "large".
 * @returns {string} The applied font size level.
 */
export function setFontScale(level) {
  if (!FONT_SCALES[level]) return currentPrefs.fontSize;
  currentPrefs.fontSize = level;
  applyPreferences(currentPrefs);
  savePreferences(currentPrefs);
  return currentPrefs.fontSize;
}

/**
 * @brief Returns a snapshot of the current preferences.
 * @returns {Object} Object with theme, contrast, and fontSize keys.
 */
export function getPreferences() {
  return { ...currentPrefs };
}
