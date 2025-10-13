/**
 * @file App.js
 * @brief Main application initialization and view management
 * @description Orchestrates SPA functionality and coordinates between modules with enhanced
 *              error handling, performance monitoring, and accessibility features
 */

import MainController from './MainController.js';
import NavigationController from './NavigationController.js';
import SectionController from './SectionController.js';
import './main.css';

import ViewManager from './ViewManager.js';
import Router from './Router.js';
import ThemeManager from './ThemeManager.js';
import AccessibilityManager from './AccessibilityManager.js';
import PerformanceMonitor from './PerformanceMonitor.js';
import ErrorReporter from './ErrorReporter.js';

import ContentModel from './ContentModel.js';
import UserModel from './UserModel.js';

import NavigationView from './NavigationView.js';
import HeroView from './HeroView.js';
import FooterView from './FooterView.js';
import SectionView from './SectionView.js';

/**
 * @class App
 * @brief Central application controller and coordinator
 * @description Initializes all application subsystems, manages lifecycle events,
 *              and handles cross-module communication with robust error handling
 */
class App {
    /**
     * @brief Creates a new App instance
     * @constructor
     */
    constructor() {
        this.viewManager = null;
        this.router = null;
        this.themeManager = null;
        this.accessibilityManager = null;
        this.performanceMonitor = null;
        this.errorReporter = null;
        this.mainController = null;
        this.navigationController = null;
        this.sectionController = null;
        this.models = {};
        this.views = {};
        this.isInitialized = false;
        this.isHealthy = true;
        this.eventAbortController = new AbortController();

        // Proper binding
        this.initializeApplication = this.initializeApplication.bind(this);
        this.handleInitializationFailure = this.handleInitializationFailure.bind(this);
        this.handleViewChangeEvent = this.handleViewChangeEvent.bind(this);
        this.handleThemeChangeEvent = this.handleThemeChangeEvent.bind(this);
        this.handleAccessibilityChangeEvent = this.handleAccessibilityChangeEvent.bind(this);
        this.handleGlobalErrorEvent = this.handleGlobalErrorEvent.bind(this);
        this.handleUnhandledRejectionEvent = this.handleUnhandledRejectionEvent.bind(this);
        this.handleWindowLoadEvent = this.handleWindowLoadEvent.bind(this);
        this.handleVisibilityChangeEvent = this.handleVisibilityChangeEvent.bind(this);
        this.handleOnlineStatusEvent = this.handleOnlineStatusEvent.bind(this);
        this.handleOfflineStatusEvent = this.handleOfflineStatusEvent.bind(this);
        this.handleViewRenderError = this.handleViewRenderError.bind(this);
    }

    /**
     * @brief Initializes all application subsystems with dependency order
     * @method initializeApplication
     * @returns {Promise<void>}
     * @public
     */
    async initializeApplication() {
        if (this.isInitialized) {
            console.warn('Application already initialized');
            return;
        }

        try {
            // Initialize error reporter first to catch any initialization errors
            this.errorReporter = new ErrorReporter();
            await this.errorReporter.initialize().catch(error => {
                console.warn('Error reporter initialization failed, continuing without it:', error);
            });

            this.performanceMonitor = new PerformanceMonitor();
            await this.performanceMonitor.startMonitoring().catch(error => {
                console.warn('Performance monitor initialization failed, continuing without it:', error);
            });

            // Validate critical browser features before proceeding
            if (!this.checkBrowserCompatibility()) {
                this.handleBrowserIncompatibility();
                return;
            }

            // Initialize core managers in proper dependency order
            await this.initializeCoreManagers();
            
            // Set up application-wide event system
            this.setupGlobalEventListeners();
            
            // Initialize cross-manager communication
            this.setupInterManagerCommunication();

            this.hideLoadingOverlay();

            this.isInitialized = true;
            this.isHealthy = true;

            console.info('Application initialized successfully');
            
            // Notify other components that app is ready
            this.dispatchApplicationEvent('app:initialized', {
                timestamp: Date.now(),
                initializationDuration: performance.now()
            });

        } catch (initializationError) {
            console.error('Application initialization failed:', initializationError);
            await this.handleInitializationFailure(initializationError);
        }
    }

    /**
     * @brief Checks for required browser features and APIs
     * @method checkBrowserCompatibility
     * @returns {boolean} True if browser meets minimum requirements
     * @private
     */
    checkBrowserCompatibility() {
        const requiredFeatures = {
            promises: typeof Promise !== 'undefined',
            fetch: typeof fetch !== 'undefined',
            intersectionObserver: typeof IntersectionObserver !== 'undefined',
            customElements: typeof customElements !== 'undefined',
            cssVariables: window.CSS && CSS.supports && CSS.supports('--test', '0'),
            es6: typeof Map !== 'undefined' && typeof Set !== 'undefined'
        };

        const missingFeatures = Object.entries(requiredFeatures)
            .filter(([, isSupported]) => !isSupported)
            .map(([feature]) => feature);

        if (missingFeatures.length > 0) {
            console.warn('Missing browser features:', missingFeatures);
            return false;
        }

        return true;
    }

    /**
     * @brief Gets names of missing browser features for error reporting
     * @method getMissingBrowserFeatures
     * @returns {Array} Array of missing feature names
     * @private
     */
    getMissingBrowserFeatures() {
        const requiredFeatures = {
            promises: typeof Promise !== 'undefined',
            fetch: typeof fetch !== 'undefined',
            intersectionObserver: typeof IntersectionObserver !== 'undefined',
            customElements: typeof customElements !== 'undefined',
            cssVariables: window.CSS && CSS.supports && CSS.supports('--test', '0'),
            es6: typeof Map !== 'undefined' && typeof Set !== 'undefined'
        };

        return Object.entries(requiredFeatures)
            .filter(([, isSupported]) => !isSupported)
            .map(([feature]) => feature);
    }

    /**
     * @brief Handles browser incompatibility gracefully
     * @method handleBrowserIncompatibility
     * @private
     */
    handleBrowserIncompatibility() {
        const applicationContainer = document.getElementById('app');
        if (!applicationContainer) return;

        applicationContainer.innerHTML = `
            <div class="browser-compatibility-error" role="alert" aria-live="polite">
                <div class="error-container">
                    <h1 class="error-title">Browser Update Recommended</h1>
                    <p class="error-description">
                        Your current browser doesn't support all the features required 
                        for this application. Please update to a modern browser for 
                        the best experience.
                    </p>
                    <div class="browser-recommendations">
                        <p>Recommended browsers:</p>
                        <ul class="browser-list">
                            <li>Google Chrome (latest)</li>
                            <li>Mozilla Firefox (latest)</li>
                            <li>Microsoft Edge (latest)</li>
                            <li>Safari (latest)</li>
                        </ul>
                    </div>
                    <button class="retry-button" onclick="window.location.reload()">
                        Retry Application Load
                    </button>
                </div>
            </div>
        `;

        this.dispatchApplicationEvent('app:browserIncompatible', {
            missingFeatures: this.getMissingBrowserFeatures(),
            userAgent: navigator.userAgent
        });
    }

    /**
     * @brief Initializes core application managers with proper error handling and dependency injection
     * @method initializeCoreManagers
     * @returns {Promise<void>}
     * @private
     */
    async initializeCoreManagers() {
        try {
            console.info('App: Starting core managers initialization...');

            // Execute initialization steps in proper sequence
            await this.initializeDataModels();
            await this.initializeInfrastructureManagers();
            await this.initializeViewLayer();
            await this.initializeRouter();
            await this.initializeControllers();
            
            // After all controllers are initialized, pass them to MainController
            if (this.mainController && typeof this.mainController.setControllers === 'function') {
                this.mainController.setControllers({
                    navigation: this.navigationController,
                    section: this.sectionController
                });
            }

            await this.renderInitialContent();
            
            // Verify overall initialization status
            await this.verifyInitializationStatus();

            console.info('App: All core managers initialized successfully!');

        } catch (error) {
            console.error('App: Core managers initialization failed:', error);
            await this.handleInitializationFailure(error);
            throw error;
        }
    }

    /**
     * @brief Initializes data models (foundation layer)
     * @private
     * @returns {Promise<void>}
     */
    async initializeDataModels() {
        console.info('App: Initializing data models...');
        
        try {
            this.models = {
                content: new ContentModel(),
                user: new UserModel()
            };

            // Initialize models with fallback
            await Promise.allSettled([
                this.models.content.initialize?.() || Promise.resolve(),
                this.models.user.initialize?.() || Promise.resolve()
            ]);

            console.info('App: Data models initialization completed.');
            
        } catch (error) {
            console.error('App: Data models initialization failed, continuing with fallback:', error);
            // Don't throw error here - allow app to continue with fallback data
        }
    }

    /**
     * @brief Initializes infrastructure managers (support services layer)
     * @private
     * @returns {Promise<void>}
     */
    async initializeInfrastructureManagers() {
        console.info('App: Initializing infrastructure managers...');

        // Re-initialize if not already done in main initializeApplication
        if (!this.errorReporter) {
            this.errorReporter = new ErrorReporter();
        }
        if (!this.performanceMonitor) {
            this.performanceMonitor = new PerformanceMonitor();
        }
        
        this.accessibilityManager = new AccessibilityManager();
        this.themeManager = new ThemeManager();

        // Initialize infrastructure managers in parallel with fallbacks
        await Promise.allSettled([
            this.errorReporter.initialize?.() || Promise.resolve(),
            this.accessibilityManager.initialize?.() || Promise.resolve(),
            this.themeManager.initialize?.() || Promise.resolve()
        ]);
    }

    /**
     * @brief Initializes view layer components
     * @private
     * @returns {Promise<void>}
     */
    async initializeViewLayer() {
        console.info('App: Initializing view layer...');

        const mainContentElement = document.getElementById('main-content');
        if (!mainContentElement) {
            throw new Error('App: Main content element #main-content not found.');
        }

        this.viewManager = new ViewManager({
            viewContainer: mainContentElement,
            enableCaching: true
        });

        // Initialize ViewManager if it has an initialize method
        if (typeof this.viewManager.initialize === 'function') {
            try {
                await this.viewManager.initialize();
            } catch (error) {
                console.error('App: ViewManager initialization failed:', error);
                throw error;
            }
        }

        // Instantiate views with proper error handling
        try {
            this.views = {
                navigation: new NavigationView(document.getElementById('main-nav')),
                hero: new HeroView(document.getElementById('hero-section')),
                footer: new FooterView(document.getElementById('main-footer')),
                section: new SectionView(mainContentElement)
            };
        } catch (error) {
            console.error('App: View instantiation failed:', error);
            throw new Error(`Failed to instantiate views: ${error.message}`);
        }
    }

    /**
     * @brief Initializes routing system
     * @private
     * @returns {Promise<void>}
     */
    async initializeRouter() {
        console.info('App: Initializing router...');

        this.router = new Router();
        
        if (typeof this.router.initialize === 'function') {
            await this.router.initialize();
        }
    }

    /**
     * @brief Initializes all application controllers
     * @private
     * @returns {Promise<void>}
     */
    async initializeControllers() {
        console.info('App: Initializing application controllers...');

        // Initialize controllers with proper error handling
        try {
            // NavigationController
            this.navigationController = new NavigationController(this.views.navigation, this.router);
            if (typeof this.navigationController.initialize === 'function') {
                await this.navigationController.initialize();
            }

            // SectionController
            this.sectionController = new SectionController(this.models.content, this.views.section);
            if (typeof this.sectionController.initialize === 'function') {
                await this.sectionController.initialize();
            }

            // MainController
            this.mainController = new MainController(this.models, this.viewManager, {
                navigation: this.navigationController,
                section: this.sectionController
            });
            
            if (typeof this.mainController.initializeApplication === 'function') {
                await this.mainController.initializeApplication();
            }

            // Verify controller initialization state
            if (this.mainController && typeof this.mainController.getInitializationState === 'function' && 
                !this.mainController.getInitializationState()) {
                throw new Error('MainController failed to initialize properly');
            }

        } catch (error) {
            console.error('App: Controller initialization failed:', error);
            throw error;
        }
    }

    /**
     * @brief Renders initial application content
     * @private
     * @returns {Promise<void>}
     */
    async renderInitialContent() {
        console.info('App: Rendering initial application content...');

        if (this.mainController && typeof this.mainController.renderInitialContent === 'function') {
            try {
                await this.mainController.renderInitialContent();
                console.info('App: Initial content rendered successfully.');
            } catch (error) {
                console.error('App: Initial content rendering failed:', error);
                this.showContentLoadingError(error);
            }
        } else {
            const errorMessage = 'App: MainController not properly initialized, cannot render initial content.';
            console.error(errorMessage);
            this.showContentLoadingError(new Error(errorMessage));
        }
    }

    /**
     * @brief Verifies the initialization status of all critical components
     * @private
     * @returns {Promise<void>}
     */
    async verifyInitializationStatus() {
        console.info('App: Verifying initialization status...');
        const initializationStatus = {};

        // Check models
        initializationStatus.ContentModel = this.models.content?.isInitialized ? 'SUCCESS' : 'FAILED';
        initializationStatus.UserModel = this.models.user?.isInitialized ? 'SUCCESS' : 'FAILED';

        // Check infrastructure managers
        initializationStatus.ErrorReporter = this.errorReporter?.isInitialized ? 'SUCCESS' : 'FAILED';
        initializationStatus.AccessibilityManager = this.accessibilityManager?.isInitialized ? 'SUCCESS' : 'FAILED';
        initializationStatus.ThemeManager = this.themeManager?.isInitialized ? 'SUCCESS' : 'FAILED';

        // Check view layer
        initializationStatus.ViewManager = this.viewManager?.isInitialized ? 'SUCCESS' : 'FAILED';

        // Check router
        initializationStatus.Router = this.router?.isInitialized ? 'SUCCESS' : 'FAILED';

        // Check controllers - use safe method calls
        initializationStatus.MainController = 
            (this.mainController && typeof this.mainController.getInitializationState === 'function' && 
             this.mainController.getInitializationState()) ? 'SUCCESS' : 'FAILED';
        
        initializationStatus.NavigationController = this.navigationController?.isInitialized ? 'SUCCESS' : 'FAILED';
        
        initializationStatus.SectionController = 
            (this.sectionController && typeof this.sectionController.getInitializationState === 'function' && 
             this.sectionController.getInitializationState()) ? 'SUCCESS' : 'FAILED';

        console.debug('App: Initialization status:', initializationStatus);

        // Identify failed components
        const failedManagers = Object.entries(initializationStatus)
            .filter(([_, status]) => status === 'FAILED')
            .map(([manager]) => manager);

        if (failedManagers.length > 0) {
            const errorMessage = `Application initialization partially failed. Failed components: ${failedManagers.join(', ')}`;
            console.warn('App:', errorMessage);
            
            // Check for critical failures
            const criticalComponents = ['MainController', 'ViewManager', 'SectionController'];
            const criticalFailures = failedManagers.filter(manager => 
                criticalComponents.includes(manager)
            );

            if (criticalFailures.length > 0) {
                throw new Error(`Critical initialization failure: ${criticalFailures.join(', ')}`);
            } else {
                console.warn('App: Non-critical initialization failures, application continuing in degraded mode.');
            }
        }
    }

    /**
     * @brief Handles initialization failures comprehensively
     * @private
     * @param {Error} error - The initialization error
     * @returns {Promise<void>}
     */
    async handleInitializationFailure(error) {
        console.error('App: Handling initialization failure:', error);
        
        if (this.errorReporter) {
            this.errorReporter.captureError(error, {
                type: 'initialization',
                severity: 'critical',
                timestamp: Date.now()
            });
        }

        await this.renderCriticalErrorFallback(error);
    }

    /**
     * @brief Helper method to show content loading errors to users
     * @private
     * @param {Error} error - The error that occurred during content loading
     */
    showContentLoadingError(error) {
        console.error('App: Content loading error:', error);
        
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            mainContent.innerHTML = `
                <div class="content-error-state">
                    <h3>Content Loading Issue</h3>
                    <p>Some content could not be loaded. Please refresh the page or try again later.</p>
                    <button onclick="window.location.reload()" class="btn btn--primary">
                        Reload Page
                    </button>
                    <details class="error-details">
                        <summary>Technical Details</summary>
                        <pre>${error.message}</pre>
                    </details>
                </div>
            `;
        }
    }

    /**
     * @brief Renders a critical error fallback page
     * @private
     * @param {Error} error - The critical error that occurred
     */
    async renderCriticalErrorFallback(error) {
        // Clear any existing content
        document.body.innerHTML = '';
        
        document.body.innerHTML = `
            <div class="critical-error-page" style="padding: 2rem; text-align: center; font-family: system-ui;">
                <h1>Application Error</h1>
                <p>A critical error occurred during application startup. We apologize for the inconvenience.</p>
                <button onclick="window.location.reload()" style="padding: 0.5rem 1rem; margin: 1rem;">
                    Reload Application
                </button>
                <details style="margin-top: 1rem;">
                    <summary>Technical Details</summary>
                    <pre style="text-align: left; background: #f5f5f5; padding: 1rem; overflow: auto;">${error.message}</pre>
                </details>
            </div>
        `;
    }

    /**
     * @brief Persists user preferences to local storage
     * @method persistUserPreference
     * @param {string} key - Key for the preference
     * @param {any} value - Value to store
     * @private
     */
    persistUserPreference(key, value) {
        try {
            localStorage.setItem(`app-pref-${key}`, JSON.stringify(value));
        } catch (e) {
            console.warn(`App: Failed to persist preference ${key}:`, e);
        }
    }

    /**
     * @brief Retrieves user preferences from local storage
     * @method retrieveUserPreference
     * @param {string} key - Key for the preference
     * @param {any} defaultValue - Default value if preference not found
     * @returns {any}
     * @private
     */
    retrieveUserPreference(key, defaultValue) {
        try {
            const stored = localStorage.getItem(`app-pref-${key}`);
            return stored ? JSON.parse(stored) : defaultValue;
        } catch (e) {
            console.warn(`App: Failed to retrieve preference ${key}:`, e);
            return defaultValue;
        }
    }

    /**
     * @brief Shows an offline indicator to the user
     * @private
     */
    showOfflineIndicator = () => {
        const existingIndicator = document.getElementById('offline-indicator');
        if (existingIndicator) return;

        const indicator = document.createElement('div');
        indicator.id = 'offline-indicator';
        indicator.className = 'offline-indicator';
        indicator.innerHTML = `
            <p>You are currently offline. Some features may not be available.</p>
        `;
        document.body.appendChild(indicator);
    };

    /**
     * @brief Retries failed network operations (e.g., after going online)
     * @method retryFailedOperations
     * @private
     */
    retryFailedOperations = () => {
        console.info('App: Retrying failed operations...');
        // Implement retry logic for network requests here
        // e.g., re-fetch content that failed to load when offline
    };

    /**
     * @brief Dispatches a custom application-wide event
     * @method dispatchApplicationEvent
     * @param {string} eventType - Type of application event
     * @param {Object} eventDetail - Additional event data
     * @private
     */
    dispatchApplicationEvent(eventType, eventDetail = {}) {
        const appEvent = new CustomEvent(eventType, {
            detail: {
                source: 'App',
                ...eventDetail
            },
            bubbles: true,
            cancelable: true
        });
        window.dispatchEvent(appEvent);
    }

    /**
     * @brief Hides the initial loading overlay
     * @private
     */
    hideLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.opacity = '0';
            overlay.addEventListener('transitionend', () => overlay.remove());
        }
    }

    /**
     * @brief Tracks analytics for view changes
     * @method trackViewAnalytics
     * @param {string} viewName - Name of the view
     * @param {Object} routeParameters - Route parameters
     * @private
     */
    trackViewAnalytics(viewName, routeParameters) {
        // Implementation for analytics tracking
        console.debug(`App: Tracking analytics for view ${viewName}`, routeParameters);
    }

    /**
     * @brief Cleans up resources and event listeners when the app is destroyed
     * @public
     */
    destroy() {
        this.eventAbortController.abort();
        
        // Safe destruction calls
        this.viewManager?.destroy?.();
        this.router?.destroy?.();
        this.themeManager?.destroy?.();
        this.accessibilityManager?.destroy?.();
        this.performanceMonitor?.destroy?.();
        this.errorReporter?.destroy?.();
        this.mainController?.destroy?.();
        this.navigationController?.destroy?.();
        this.sectionController?.destroy?.();

        // Clear models and views
        this.models = {};
        this.views = {};

        this.isInitialized = false;
        this.isHealthy = false;
        console.info('App: Application destroyed and resources cleaned up.');
    }
}

// Enhanced application bootstrap with better error handling
document.addEventListener('DOMContentLoaded', async () => {
    // Show loading state immediately
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'block';
    }

    let applicationInstance;
    
    try {
        applicationInstance = new App();
        
        // Make app instance globally available for debugging
        if (typeof process !== 'undefined' && process.env && process.env.NODE_ENV === 'development') {
            window.app = applicationInstance;
        } else if (typeof window !== 'undefined') {
            // For browser environment without process.env
            window.app = applicationInstance;
        }

        await applicationInstance.initializeApplication();
        
    } catch (bootstrapError) {
        console.error('Application bootstrap failed:', bootstrapError);
        
        // Final fallback for complete bootstrap failure
        document.body.innerHTML = `
            <div style="padding: 2rem; text-align: center; font-family: system-ui;">
                <h1>Application Failed to Load</h1>
                <p>Please refresh the page or try again later.</p>
                <button onclick="window.location.reload()" style="padding: 0.5rem 1rem;">
                    Reload Page
                </button>
                <details style="margin-top: 1rem;">
                    <summary>Technical Details</summary>
                    <pre style="text-align: left; background: #f5f5f5; padding: 1rem; overflow: auto;">${bootstrapError.message}</pre>
                </details>
            </div>
        `;
    }
});

// Export for testing and potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { App };
}