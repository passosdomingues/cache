/**
 * Pinakes — Frontend Application Entry Point
 *
 * Modules:
 *   - autocomplete.js  : debounced dropdown (≥2 chars, 200ms)
 *   - theme.js         : dark/light toggle + persistence
 *   - sidebar.js       : tuning panel open/close
 *   - a11y.js          : font size + contrast controls
 *   - search.js        : loading state, keyboard shortcuts, quote syntax
 */

import { initAutocomplete } from './modules/autocomplete.js';
import { initTheme }        from './modules/theme.js';
import { initSidebar }      from './modules/sidebar.js';
import { initA11y }         from './modules/a11y.js';
import { initSearch }       from './modules/search.js';

document.addEventListener('DOMContentLoaded', () => {
    // Initialise Lucide icons first so all modules can reference them
    if (window.lucide) window.lucide.createIcons();

    initTheme();
    initSidebar();
    initA11y();
    initSearch();
    initAutocomplete('/api/autocomplete');
});
