/**
 * @brief Theme management script
 * @details Handles dark/light mode switching and persistence
 * @author Rafael Passos Domingues
 * @version 1.0.0
 */

(function() {
    'use strict';

    const THEME_KEY = 'bluevelvet-theme';
    const DARK_MODE_CLASS = 'dark-mode';
    const LIGHT_MODE_CLASS = 'light-mode';
    const THEME_TOGGLE_ID = 'themeToggle';

    /**
     * @brief Initialize theme on page load
     */
    function initializeTheme() {
        const savedTheme = localStorage.getItem(THEME_KEY);
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        const shouldBeDark = savedTheme ? savedTheme === 'dark' : prefersDark;
        
        if (shouldBeDark) {
            setDarkMode();
        } else {
            setLightMode();
        }
    }

    /**
     * @brief Set dark mode
     */
    function setDarkMode() {
        const app = document.getElementById('app');
        if (app) {
            app.classList.remove(LIGHT_MODE_CLASS);
            app.classList.add(DARK_MODE_CLASS);
        }
        localStorage.setItem(THEME_KEY, 'dark');
        updateThemeToggleIcon(true);
    }

    /**
     * @brief Set light mode
     */
    function setLightMode() {
        const app = document.getElementById('app');
        if (app) {
            app.classList.remove(DARK_MODE_CLASS);
            app.classList.add(LIGHT_MODE_CLASS);
        }
        localStorage.setItem(THEME_KEY, 'light');
        updateThemeToggleIcon(false);
    }

    /**
     * @brief Toggle between dark and light mode
     */
    function toggleTheme() {
        const app = document.getElementById('app');
        if (app.classList.contains(DARK_MODE_CLASS)) {
            setLightMode();
        } else {
            setDarkMode();
        }
    }

    /**
     * @brief Update theme toggle button icon
     * @param isDark Whether dark mode is active
     */
    function updateThemeToggleIcon(isDark) {
        const toggle = document.getElementById(THEME_TOGGLE_ID);
        if (toggle) {
            const icon = toggle.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-moon', 'fa-sun');
                icon.classList.add(isDark ? 'fa-sun' : 'fa-moon');
            }
        }
    }

    /**
     * @brief Listen for system theme changes
     */
    function listenForSystemThemeChanges() {
        const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
        darkModeQuery.addEventListener('change', (e) => {
            if (!localStorage.getItem(THEME_KEY)) {
                if (e.matches) {
                    setDarkMode();
                } else {
                    setLightMode();
                }
            }
        });
    }

    /**
     * @brief Setup event listeners
     */
    function setupEventListeners() {
        const themeToggle = document.getElementById(THEME_TOGGLE_ID);
        if (themeToggle) {
            themeToggle.addEventListener('click', toggleTheme);
        }
    }

    /**
     * @brief Initialize on DOM ready
     */
    document.addEventListener('DOMContentLoaded', function() {
        initializeTheme();
        setupEventListeners();
        listenForSystemThemeChanges();
    });

    // Expose functions globally if needed
    window.bluevelvetTheme = {
        setDarkMode,
        setLightMode,
        toggleTheme
    };

})();
