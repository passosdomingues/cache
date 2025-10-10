/**
 * @brief Main application initialization and view management
 * @details Orchestrates the SPA functionality and coordinates between modules
 */

import { ViewManager } from './modules/ViewManager.js';
import { Router } from './modules/Router.js';
import { ThemeManager } from './modules/ThemeManager.js';
import { AccessibilityManager } from './modules/AccessibilityManager.js';

/**
 * @brief Main Application Class
 * @class App
 * @description Central application controller that initializes all subsystems
 */
class App {
    /**
     * @brief Creates an instance of the main application
     * @constructor
     */
    constructor() {
        this.viewManager = null;
        this.router = null;
        this.themeManager = null;
        this.accessibilityManager = null;
        this.isInitialized = false;
        
        this.init = this.init.bind(this);
        this.handleViewChange = this.handleViewChange.bind(this);
    }

    /**
     * @brief Initializes all application subsystems
     * @method init
     * @returns {Promise<void>}
     */
    async init() {
        try {
            // Initialize core managers
            this.themeManager = new ThemeManager();
            this.accessibilityManager = new AccessibilityManager();
            this.viewManager = new ViewManager();
            this.router = new Router();

            // Set up event listeners and inter-manager communication
            this.setupEventListeners();
            this.setupErrorHandling();

            // Initialize subsystems
            await Promise.all([
                this.themeManager.init(),
                this.accessibilityManager.init(),
                this.viewManager.init(),
                this.router.init()
            ]);

            this.isInitialized = true;
            console.log('Application initialized successfully');

            // Dispatch custom event for initialization complete
            window.dispatchEvent(new CustomEvent('app:initialized'));

        } catch (error) {
            console.error('Failed to initialize application:', error);
            this.handleInitializationError(error);
        }
    }

    /**
     * @brief Sets up global event listeners for application-level events
     * @method setupEventListeners
     */
    setupEventListeners() {
        // Listen for view change events from the router
        window.addEventListener('router:viewchange', this.handleViewChange);
        
        // Listen for theme changes
        window.addEventListener('theme:changed', (event) => {
            this.onThemeChange(event.detail);
        });

        // Global error handling
        window.addEventListener('error', this.handleGlobalError);
        window.addEventListener('unhandledrejection', this.handlePromiseRejection);
    }

    /**
     * @brief Handles view changes triggered by the router
     * @method handleViewChange
     * @param {CustomEvent} event - The view change event
     */
    async handleViewChange(event) {
        const { viewName, viewData } = event.detail;
        
        try {
            await this.viewManager.renderView(viewName, viewData);
            
            // Update ARIA live region for screen readers
            this.accessibilityManager.announceViewChange(viewName);
            
        } catch (error) {
            console.error(`Error rendering view ${viewName}:`, error);
            await this.viewManager.renderErrorView(error);
        }
    }

    /**
     * @brief Handles theme change events
     * @method onThemeChange
     * @param {Object} themeData - The new theme configuration
     */
    onThemeChange(themeData) {
        // Update any theme-dependent components
        document.documentElement.setAttribute('data-theme', themeData.theme);
    }

    /**
     * @brief Sets up global error handling
     * @method setupErrorHandling
     */
    setupErrorHandling() {
        this.handleGlobalError = this.handleGlobalError.bind(this);
        this.handlePromiseRejection = this.handlePromiseRejection.bind(this);
    }

    /**
     * @brief Handles global JavaScript errors
     * @method handleGlobalError
     * @param {ErrorEvent} errorEvent - The error event
     */
    handleGlobalError(errorEvent) {
        console.error('Global error:', errorEvent.error);
        // In production, send to error tracking service
        if (window.appConfig?.sentryDsn) {
            this.reportErrorToService(errorEvent.error);
        }
    }

    /**
     * @brief Handles unhandled promise rejections
     * @method handlePromiseRejection
     * @param {PromiseRejectionEvent} rejectionEvent - The promise rejection event
     */
    handlePromiseRejection(rejectionEvent) {
        console.error('Unhandled promise rejection:', rejectionEvent.reason);
        rejectionEvent.preventDefault();
    }

    /**
     * @brief Handles application initialization errors
     * @method handleInitializationError
     * @param {Error} error - The initialization error
     */
    handleInitializationError(error) {
        // Render a friendly error page
        const appContainer = document.getElementById('app');
        if (appContainer) {
            appContainer.innerHTML = `
                <div class="error-container">
                    <h1>Something went wrong</h1>
                    <p>We're having trouble loading the application. Please try refreshing the page.</p>
                    <button onclick="window.location.reload()" class="retry-button">
                        Retry
                    </button>
                </div>
            `;
        }
    }

    /**
     * @brief Reports errors to external monitoring service
     * @method reportErrorToService
     * @param {Error} error - The error to report
     */
    reportErrorToService(error) {
        // Integration point for error reporting services like Sentry
        // This would be implemented based on the specific service used
        console.warn('Error reporting service not configured:', error);
    }
}

// Application initialization when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    const app = new App();
    
    // Check for critical browser features
    if (!('Promise' in window) || !('fetch' in window)) {
        document.getElementById('app').innerHTML = `
            <div class="browser-support-error">
                <h1>Browser Update Required</h1>
                <p>Your browser does not support all required features. Please update to a modern browser.</p>
            </div>
        `;
        return;
    }

    await app.init();
});

// Export for testing and potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { App };
}