import eventBus from '../core/EventBus.js';

/**
 * @brief Theme manager service
 * @description Manages application theme and dark/light mode
 */
export class ThemeManager {
    constructor(dependencies = {}) {
        this.eventBus = dependencies.eventBus || eventBus;
        this.currentTheme = 'light';
        this.isInitialized = false;

        this.onThemeChange = this.onThemeChange.bind(this);
    }

    /**
     * @brief Initialize theme manager
     * @description Loads saved theme or detects system preference
     */
    async init() {
        if (this.isInitialized) return;

        // Load saved theme or detect system preference
        const savedTheme = localStorage.getItem('app-theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        this.currentTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
        
        this.applyTheme(this.currentTheme);
        this.setupEventListeners();
        
        this.isInitialized = true;
        console.info('ThemeManager: Initialized with theme:', this.currentTheme);
    }

    /**
     * @brief Set up event listeners
     */
    setupEventListeners() {
        this.eventBus.subscribe('theme:change', this.onThemeChange);
        
        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('app-theme')) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    /**
     * @brief Handle theme change events
     * @param {Object} data - Event data
     */
    onThemeChange(data) {
        if (data.theme && ['light', 'dark'].includes(data.theme)) {
            this.setTheme(data.theme);
        }
    }

    /**
     * @brief Set application theme
     * @param {string} theme - Theme name ('light' or 'dark')
     */
    setTheme(theme) {
        if (theme !== 'light' && theme !== 'dark') {
            console.warn('ThemeManager: Invalid theme:', theme);
            return;
        }

        this.currentTheme = theme;
        this.applyTheme(theme);
        
        // Save preference
        localStorage.setItem('app-theme', theme);
        
        this.eventBus.publish('theme:changed', { theme });
        console.info('ThemeManager: Theme changed to:', theme);
    }

    /**
     * @brief Apply theme to document
     * @param {string} theme - Theme name
     */
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        
        // Update meta theme-color for mobile browsers
        const metaThemeColor = document.querySelector('meta[name="theme-color"]');
        if (metaThemeColor) {
            metaThemeColor.setAttribute('content', theme === 'dark' ? '#1a1a1a' : '#ffffff');
        }
    }

    /**
     * @brief Toggle between light and dark themes
     */
    toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    /**
     * @brief Get current theme
     * @returns {string} Current theme
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * @brief Check if dark mode is active
     * @returns {boolean} Dark mode status
     */
    isDarkMode() {
        return this.currentTheme === 'dark';
    }

    /**
     * @brief Destroy theme manager
     */
    destroy() {
        this.eventBus.unsubscribe('theme:change', this.onThemeChange);
        this.isInitialized = false;
        console.info('ThemeManager: Destroyed');
    }
}