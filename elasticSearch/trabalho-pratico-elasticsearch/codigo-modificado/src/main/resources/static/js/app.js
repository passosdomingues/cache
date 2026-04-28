/**
 * @brief Application entry point. Initializes all ES Module components.
 *
 * Orchestrates the lifecycle of the Autocomplete, Sidebar,
 * AccessibilityPanel, and ThemeManager modules once the DOM is ready.
 *
 * @module app
 */
import { Autocomplete } from './components/autocomplete.js';
import { Sidebar } from './components/sidebar.js';
import { AccessibilityPanel } from './components/accessibilityPanel.js';
import { initThemeManager } from './services/themeManager.js';

document.addEventListener('DOMContentLoaded', () => {
  /* Initialize theme preferences before any visual render */
  initThemeManager();

  /* Re-render Lucide icons after deferred script loads */
  if (window.lucide) {
    lucide.createIcons();
  }

  /* Mount interactive components */
  new Autocomplete();
  new Sidebar();
  new AccessibilityPanel();
});
