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
    }

    /**
     * @brief Initialize theme manager
     * @description Loads saved theme or detects system preference
     */
    async init() {
        if (this.isInitialized) return;

        const savedTheme = localStorage.getItem('app-theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Use saved theme, otherwise system preference, otherwise default to dark
        this.currentTheme = savedTheme || (systemPrefersDark ? 'dark' : 'dark'); // Default to dark
        
        this.applyTheme(this.currentTheme);
        this.setupEventListeners();
        
        this.isInitialized = true;
        console.info('ThemeManager: Initialized with theme:', this.currentTheme);
    }

    /**
     * @brief Set up event listeners
     */
    setupEventListeners() {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('app-theme')) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    /**
     * @brief Set a new theme
     * @param {string} theme - Theme name ('light' or 'dark')
     */
    setTheme(theme) {
        if (theme !== 'light' && theme !== 'dark') {
            console.warn(`ThemeManager: Invalid theme '${theme}'. Defaulting to 'light'.`);
            theme = 'light';
        }

        this.currentTheme = theme;
        this.applyTheme(theme);
        
        localStorage.setItem('app-theme', theme);
        
        // Dispara evento para atualizar os componentes
        this.eventBus.publish('theme:changed', { theme });
        this.eventBus.publish('accessibility:announce', `Theme changed to ${theme} mode.`);
        
        console.info('ThemeManager: Theme changed to:', theme);
    }

    /**
     * @brief Apply theme to document
     * @param {string} theme - Theme name
     */
    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        document.documentElement.className = theme; // Adicione esta linha
        
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
        console.info('ThemeManager: Destroyed');
    }
}