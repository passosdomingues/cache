/**
 * @file ThemeManager.js
 * @brief Comprehensive theme management with CSS variables and persistence
 * @description Handles theme switching, CSS custom properties, and user preference persistence
 */

class ThemeManager {
    /**
     * @brief Creates a new ThemeManager instance
     * @constructor
     * @param {Object} configuration - Theme configuration options
     */
    constructor(configuration = {}) {
        /**
         * @private
         * @type {string}
         * @description Current active theme name
         */
        this.currentTheme = configuration.defaultTheme || 'light';

        /**
         * @private
         * @type {Object}
         * @description Available theme definitions
         */
        this.themes = configuration.themes || {
            light: {
                '--primary-color': '#264B93',
                '--secondary-color': '#A16DAE', 
                '--background-color': '#FFFFFF',
                '--text-color': '#1F3D68',
                '--surface-color': '#E4F5FC',
                '--border-color': '#264B9322'
            },
            dark: {
                '--primary-color': '#6495ED',
                '--secondary-color': '#A16DAE',
                '--background-color': '#1A1A1A',
                '--text-color': '#E4E4E4',
                '--surface-color': '#2D2D2D',
                '--border-color': '#FFFFFF22'
            }
        };

        /**
         * @private
         * @type {boolean}
         * @description Tracks initialization status
         */
        this.isInitialized = false;

        this.initialize = this.initialize.bind(this);
        this.applyTheme = this.applyTheme.bind(this);
    }

    /**
     * @brief Initializes the theme manager and applies stored preferences
     * @method initialize
     * @returns {Promise<void>}
     */
    async initialize() {
        try {
            // Load saved theme preference or detect system preference
            const savedTheme = localStorage.getItem('user-theme');
            const systemPreference = this.detectSystemThemePreference();
            
            const initialTheme = savedTheme || systemPreference || this.currentTheme;
            await this.applyTheme(initialTheme);
            
            this.isInitialized = true;
            console.info('ThemeManager initialized successfully');
        } catch (error) {
            console.error('ThemeManager initialization failed:', error);
            // Apply default theme as fallback
            await this.applyTheme('light');
        }
    }

    /**
     * @brief Detects system-level theme preference
     * @method detectSystemThemePreference
     * @returns {string|null} System theme preference or null if not detectable
     * @private
     */
    detectSystemThemePreference() {
        if (typeof window === 'undefined' || !window.matchMedia) return null;
        
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    /**
     * @brief Applies specified theme to document
     * @method applyTheme
     * @param {string} themeName - Name of theme to apply
     * @returns {Promise<void>}
     */
    async applyTheme(themeName) {
        if (!this.themes[themeName]) {
            console.warn(`Theme "${themeName}" not found. Falling back to default.`);
            themeName = Object.keys(this.themes)[0];
        }

        try {
            const theme = this.themes[themeName];
            const rootElement = document.documentElement;
            
            // Apply all CSS custom properties
            Object.entries(theme).forEach(([property, value]) => {
                rootElement.style.setProperty(property, value);
            });
            
            // Update internal state
            this.currentTheme = themeName;
            
            // Persist user preference
            localStorage.setItem('user-theme', themeName);
            
            // Dispatch theme change event
            this.dispatchThemeChangeEvent(themeName, theme);
            
            console.info(`Theme "${themeName}" applied successfully`);
        } catch (error) {
            console.error(`Error applying theme "${themeName}":`, error);
            throw error;
        }
    }

    /**
     * @brief Dispatches theme change event for application components
     * @method dispatchThemeChangeEvent
     * @param {string} themeName - Activated theme name
     * @param {Object} themeData - Theme configuration data
     * @private
     */
    dispatchThemeChangeEvent(themeName, themeData) {
        const themeChangeEvent = new CustomEvent('theme:changed', {
            detail: {
                themeName,
                themeData,
                timestamp: Date.now()
            },
            bubbles: true
        });
        
        window.dispatchEvent(themeChangeEvent);
    }

    /**
     * @brief Gets current active theme
     * @method getCurrentTheme
     * @returns {string} Current theme name
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * @brief Gets all available themes
     * @method getAvailableThemes
     * @returns {Array<string>} Array of available theme names
     */
    getAvailableThemes() {
        return Object.keys(this.themes);
    }

    /**
     * @brief Adds new theme to available themes
     * @method addTheme
     * @param {string} themeName - Unique theme identifier
     * @param {Object} themeProperties - CSS custom properties for theme
     * @returns {void}
     */
    addTheme(themeName, themeProperties) {
        if (this.themes[themeName]) {
            console.warn(`Theme "${themeName}" already exists. Overwriting.`);
        }
        
        this.themes[themeName] = { ...themeProperties };
        console.info(`Theme "${themeName}" added successfully`);
    }

    /**
     * @brief Toggles between light and dark themes
     * @method toggleTheme
     * @returns {Promise<void>}
     */
    async toggleTheme() {
        const newTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        await this.applyTheme(newTheme);
    }

    /**
     * @brief Cleans up theme manager resources
     * @method destroy
     * @returns {void}
     */
    destroy() {
        // Remove all custom theme properties
        const rootElement = document.documentElement;
        Object.keys(this.themes).forEach(themeName => {
            Object.keys(this.themes[themeName]).forEach(property => {
                rootElement.style.removeProperty(property);
            });
        });
        
        this.isInitialized = false;
        console.info('ThemeManager destroyed successfully');
    }
}

export default ThemeManager;