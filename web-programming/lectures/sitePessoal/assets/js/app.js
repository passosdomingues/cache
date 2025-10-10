/**
 * @file App.js
 * @brief Main application initialization and view management
 * @description Orchestrates SPA functionality and coordinates between modules with enhanced
 *              error handling, performance monitoring, and accessibility features
 */

import { ViewManager } from './modules/ViewManager.js';
import { Router } from './modules/Router.js';
import { ThemeManager } from './modules/ThemeManager.js';
import { AccessibilityManager } from './modules/AccessibilityManager.js';
import { PerformanceMonitor } from './modules/PerformanceMonitor.js';
import { ErrorReporter } from './modules/ErrorReporter.js';

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
        /**
         * @private
         * @type {ViewManager|null}
         * @description Manages view rendering and transitions
         */
        this.viewManager = null;

        /**
         * @private
         * @type {Router|null}
         * @description Handles client-side routing and navigation
         */
        this.router = null;

        /**
         * @private
         * @type {ThemeManager|null}
         * @description Manages theme switching and persistence
         */
        this.themeManager = null;

        /**
         * @private
         * @type {AccessibilityManager|null}
         * @description Enhances accessibility features and screen reader support
         */
        this.accessibilityManager = null;

        /**
         * @private
         * @type {PerformanceMonitor|null}
         * @description Tracks application performance metrics
         */
        this.performanceMonitor = null;

        /**
         * @private
         * @type {ErrorReporter|null}
         * @description Handles error tracking and reporting
         */
        this.errorReporter = null;

        /**
         * @private
         * @type {boolean}
         * @description Tracks initialization status
         */
        this.isInitialized = false;

        /**
         * @private
         * @type {boolean}
         * @description Tracks if the application is in a healthy state
         */
        this.isHealthy = true;

        /**
         * @private
         * @type {AbortController}
         * @description Controls cleanup of event listeners
         */
        this.eventAbortController = new AbortController();

        this.initializeApplication = this.initializeApplication.bind(this);
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
            this.performanceMonitor = new PerformanceMonitor();
            await this.performanceMonitor.startMonitoring();

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
     * @brief Gets list of missing browser features for analytics
     * @method getMissingBrowserFeatures
     * @returns {Array<string>} List of missing features
     * @private
     */
    getMissingBrowserFeatures() {
        const featureTests = {
            promises: () => typeof Promise === 'undefined',
            fetch: () => typeof fetch === 'undefined',
            intersectionObserver: () => typeof IntersectionObserver === 'undefined',
            cssVariables: () => !(window.CSS && CSS.supports && CSS.supports('--test', '0'))
        };

        return Object.entries(featureTests)
            .filter(([, test]) => test())
            .map(([feature]) => feature);
    }

    /**
     * @brief Initializes core application managers with proper error handling
     * @method initializeCoreManagers
     * @returns {Promise<void>}
     * @private
     */
    async initializeCoreManagers() {
        const initializationPromises = [];

        // Initialize error reporting first to catch initialization errors
        this.errorReporter = new ErrorReporter();
        initializationPromises.push(this.errorReporter.initialize());

        // Initialize accessibility manager early for screen reader support
        this.accessibilityManager = new AccessibilityManager();
        initializationPromises.push(this.accessibilityManager.initialize());

        // Initialize theme manager for consistent theming
        this.themeManager = new ThemeManager();
        initializationPromises.push(this.themeManager.initialize());

        // Initialize view manager for content rendering
        this.viewManager = new ViewManager();
        initializationPromises.push(this.viewManager.initialize());

        // Initialize router for navigation management
        this.router = new Router();
        initializationPromises.push(this.router.initialize());

        // Execute all initializations with timeout protection
        await Promise.allSettled(initializationPromises.map(promise => 
            Promise.race([
                promise,
                new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('Initialization timeout')), 10000)
                )
            ])
        ));

        // Check for any initialization failures
        const failedManagers = [];
        if (!this.accessibilityManager.isInitialized) failedManagers.push('AccessibilityManager');
        if (!this.themeManager.isInitialized) failedManagers.push('ThemeManager');
        if (!this.viewManager.isInitialized) failedManagers.push('ViewManager');
        if (!this.router.isInitialized) failedManagers.push('Router');

        if (failedManagers.length > 0) {
            throw new Error(`Failed to initialize: ${failedManagers.join(', ')}`);
        }
    }

    /**
     * @brief Sets up global event listeners for application lifecycle
     * @method setupGlobalEventListeners
     * @private
     */
    setupGlobalEventListeners() {
        const { signal } = this.eventAbortController;

        // Handle view changes from router
        window.addEventListener('router:viewchange', this.handleViewChangeEvent.bind(this), { signal });

        // Handle theme changes
        window.addEventListener('theme:changed', this.handleThemeChangeEvent.bind(this), { signal });

        // Handle accessibility changes
        window.addEventListener('accessibility:changed', this.handleAccessibilityChangeEvent.bind(this), { signal });

        // Global error handling
        window.addEventListener('error', this.handleGlobalErrorEvent.bind(this), { signal });
        window.addEventListener('unhandledrejection', this.handleUnhandledRejectionEvent.bind(this), { signal });

        // Performance and visibility monitoring
        window.addEventListener('load', this.handleWindowLoadEvent.bind(this), { signal });
        document.addEventListener('visibilitychange', this.handleVisibilityChangeEvent.bind(this), { signal });

        // Online/offline status monitoring
        window.addEventListener('online', this.handleOnlineStatusEvent.bind(this), { signal });
        window.addEventListener('offline', this.handleOfflineStatusEvent.bind(this), { signal });
    }

    /**
     * @brief Sets up communication channels between different managers
     * @method setupInterManagerCommunication
     * @private
     */
    setupInterManagerCommunication() {
        // Router to ViewManager communication
        this.router.onRouteChange((routeData) => {
            this.viewManager.renderView(routeData.viewName, routeData.viewData)
                .catch(error => this.handleViewRenderError(error, routeData));
        });

        // ThemeManager to ViewManager communication
        this.themeManager.onThemeChange((themeData) => {
            this.viewManager.updateTheme(themeData);
        });

        // AccessibilityManager to ViewManager communication
        this.accessibilityManager.onAccessibilityChange((accessibilitySettings) => {
            this.viewManager.updateAccessibility(accessibilitySettings);
        });
    }

    /**
     * @brief Handles view change events from the router
     * @method handleViewChangeEvent
     * @param {CustomEvent} event - View change event with route details
     * @private
     */
    handleViewChangeEvent = async (event) => {
        const { viewName, viewData, routeParameters } = event.detail;
        
        try {
            this.performanceMonitor?.mark(`view-change-start-${viewName}`);
            
            await this.viewManager.renderView(viewName, viewData);
            
            this.performanceMonitor?.mark(`view-change-end-${viewName}`);
            this.performanceMonitor?.measure(
                `view-render-${viewName}`,
                `view-change-start-${viewName}`,
                `view-change-end-${viewName}`
            );

            // Update accessibility announcements
            this.accessibilityManager.announceViewChange(viewName);
            
            // Track analytics for view changes
            this.trackViewAnalytics(viewName, routeParameters);

        } catch (viewRenderError) {
            console.error(`Error rendering view ${viewName}:`, viewRenderError);
            await this.handleViewRenderError(viewRenderError, { viewName, viewData });
        }
    };

    /**
     * @brief Handles theme change events
     * @method handleThemeChangeEvent
     * @param {CustomEvent} event - Theme change event
     * @private
     */
    handleThemeChangeEvent = (event) => {
        const themeData = event.detail;
        
        // Update document theme attribute for CSS theming
        document.documentElement.setAttribute('data-theme', themeData.themeName);
        document.documentElement.style.setProperty('color-scheme', themeData.colorScheme);

        // Persist theme preference
        this.persistUserPreference('theme', themeData);
    };

    /**
     * @brief Handles accessibility preference changes
     * @method handleAccessibilityChangeEvent
     * @param {CustomEvent} event - Accessibility change event
     * @private
     */
    handleAccessibilityChangeEvent = (event) => {
        const accessibilitySettings = event.detail;
        
        // Update document with accessibility attributes
        Object.entries(accessibilitySettings).forEach(([key, value]) => {
            if (value) {
                document.documentElement.setAttribute(`data-a11y-${key}`, value);
            } else {
                document.documentElement.removeAttribute(`data-a11y-${key}`);
            }
        });

        this.persistUserPreference('accessibility', accessibilitySettings);
    };

    /**
     * @brief Handles global JavaScript errors
     * @method handleGlobalErrorEvent
     * @param {ErrorEvent} errorEvent - Global error event
     * @private
     */
    handleGlobalErrorEvent = (errorEvent) => {
        const errorContext = {
            filename: errorEvent.filename,
            lineno: errorEvent.lineno,
            colno: errorEvent.colno,
            userAgent: navigator.userAgent,
            timestamp: Date.now()
        };

        console.error('Global error occurred:', errorEvent.error, errorContext);
        this.errorReporter?.captureError(errorEvent.error, errorContext);
    };

    /**
     * @brief Handles unhandled promise rejections
     * @method handleUnhandledRejectionEvent
     * @param {PromiseRejectionEvent} rejectionEvent - Promise rejection event
     * @private
     */
    handleUnhandledRejectionEvent = (rejectionEvent) => {
        console.error('Unhandled promise rejection:', rejectionEvent.reason);
        
        this.errorReporter?.captureError(rejectionEvent.reason, {
            type: 'unhandledRejection',
            timestamp: Date.now()
        });

        // Prevent browser default handling
        rejectionEvent.preventDefault();
    };

    /**
     * @brief Handles window load completion
     * @method handleWindowLoadEvent
     * @private
     */
    handleWindowLoadEvent = () => {
        this.performanceMonitor?.mark('window-loaded');
        this.dispatchApplicationEvent('app:windowLoaded', {
            loadTime: performance.now()
        });
    };

    /**
     * @brief Handles page visibility changes
     * @method handleVisibilityChangeEvent
     * @private
     */
    handleVisibilityChangeEvent = () => {
        const isVisible = !document.hidden;
        this.dispatchApplicationEvent('app:visibilityChange', {
            isVisible,
            timestamp: Date.now()
        });

        // Optimize performance when tab is not visible
        if (!isVisible) {
            this.viewManager?.reducePerformanceWhenHidden();
        }
    };

    /**
     * @brief Handles online status restoration
     * @method handleOnlineStatusEvent
     * @private
     */
    handleOnlineStatusEvent = () => {
        this.dispatchApplicationEvent('app:online');
        this.isHealthy = true;
        
        // Retry any failed network operations
        this.retryFailedOperations();
    };

    /**
     * @brief Handles offline status detection
     * @method handleOfflineStatusEvent
     * @private
     */
    handleOfflineStatusEvent = () => {
        this.dispatchApplicationEvent('app:offline');
        this.isHealthy = false;
        
        // Show offline indicator
        this.showOfflineIndicator();
    };

    /**
     * @brief Handles view rendering errors with fallback strategies
     * @method handleViewRenderError
     * @param {Error} error - Rendering error
     * @param {Object} routeData - Original route data for recovery
     * @returns {Promise<void>}
     * @private
     */
    handleViewRenderError = async (error, routeData) => {
        this.errorReporter?.captureError(error, {
            type: 'viewRender',
            viewName: routeData.viewName,
            routeData: routeData
        });

        // Attempt to render error view
        try {
            await this.viewManager.renderErrorView({
                error,
                viewName: routeData.viewName,
                suggestion: 'Please try navigating to a different section.'
            });
        } catch (fallbackError) {
            console.error('Even error view failed:', fallbackError);
            this.renderCriticalErrorFallback(error);
        }
    };

    /**
     * @brief Handles complete application initialization failure
     * @method handleInitializationFailure
     * @param {Error} error - Initialization error
     * @returns {Promise<void>}
     * @private
     */
    handleInitializationFailure = async (error) => {
        this.errorReporter?.captureError(error, {
            type: 'initialization',
            severity: 'critical',
            timestamp: Date.now()
        });

        await this.renderCriticalErrorFallback(error);
    };

    /**
     * @brief Renders critical error fallback when all else fails
     * @method renderCriticalErrorFallback
     * @param {Error} error - The critical error
     * @private
     */
    renderCriticalErrorFallback = (error) => {
        const applicationContainer = document.getElementById('app');
        if (!applicationContainer) return;

        applicationContainer.innerHTML = `
            <div class="critical-error-container" role="alert" aria-live="assertive">
                <div class="error-content">
                    <h1 class="error-title">Application Error</h1>
                    <p class="error-description">
                        We're experiencing technical difficulties. Our team has been notified.
                    </p>
                    <div class="error-actions">
                        <button class="retry-button" onclick="window.location.reload()">
                            Reload Application
                        </button>
                        <button class="support-button" onclick="window.open('/support', '_blank')">
                            Contact Support
                        </button>
                    </div>
                    <details class="error-details">
                        <summary>Technical Details</summary>
                        <pre>${error.message}</pre>
                    </details>
                </div>
            </div>
        `;
    };

    /**
     * @brief Persists user preferences to storage
     * @method persistUserPreference
     * @param {string} preferenceType - Type of preference (theme, accessibility, etc.)
     * @param {Object} preferenceData - Preference data to store
     * @private
     */
    persistUserPreference = (preferenceType, preferenceData) => {
        try {
            const storageKey = `user-preferences-${preferenceType}`;
            localStorage.setItem(storageKey, JSON.stringify(preferenceData));
        } catch (storageError) {
            console.warn('Failed to persist user preference:', storageError);
        }
    };

    /**
     * @brief Tracks view analytics for user behavior monitoring
     * @method trackViewAnalytics
     * @param {string} viewName - Name of the view being tracked
     * @param {Object} routeParameters - Route parameters for context
     * @private
     */
    trackViewAnalytics = (viewName, routeParameters) => {
        this.dispatchApplicationEvent('app:viewTracked', {
            viewName,
            routeParameters,
            timestamp: Date.now()
        });
    };

    /**
     * @brief Shows offline indicator to user
     * @method showOfflineIndicator
     * @private
     */
    showOfflineIndicator = () => {
        // Implementation for showing offline UI
        const existingIndicator = document.getElementById('offline-indicator');
        if (existingIndicator) return;

        const indicator = document.createElement('div');
        indicator.id = 'offline-indicator';
        indicator.className = 'offline-indicator';
        indicator.setAttribute('role', 'status');
        indicator.setAttribute('aria-live', 'polite');
        indicator.textContent = 'You are currently offline. Some features may be unavailable.';
        
        document.body.prepend(indicator);
    };

    /**
     * @brief Retries failed operations when coming back online
     * @method retryFailedOperations
     * @private
     */
    retryFailedOperations = () => {
        // Remove offline indicator
        const offlineIndicator = document.getElementById('offline-indicator');
        if (offlineIndicator) {
            offlineIndicator.remove();
        }

        // Retry any queued operations
        this.dispatchApplicationEvent('app:retryOperations');
    };

    /**
     * @brief Dispatches custom application events
     * @method dispatchApplicationEvent
     * @param {string} eventName - Name of the event to dispatch
     * @param {Object} eventDetail - Event detail data
     * @private
     */
    dispatchApplicationEvent = (eventName, eventDetail = {}) => {
        const applicationEvent = new CustomEvent(eventName, {
            detail: {
                ...eventDetail,
                appInstance: this,
                timestamp: eventDetail.timestamp || Date.now()
            },
            bubbles: true
        });

        window.dispatchEvent(applicationEvent);
    };

    /**
     * @brief Cleans up application resources and event listeners
     * @method destroy
     * @returns {void}
     * @public
     */
    destroy() {
        // Abort all event listeners
        this.eventAbortController.abort();

        // Clean up managers
        this.viewManager?.destroy();
        this.router?.destroy();
        this.themeManager?.destroy();
        this.accessibilityManager?.destroy();
        this.performanceMonitor?.stopMonitoring();
        this.errorReporter?.destroy();

        this.isInitialized = false;
        this.isHealthy = false;

        console.info('Application destroyed successfully');
    }
}

// Application bootstrap with enhanced error handling
document.addEventListener('DOMContentLoaded', async () => {
    const applicationInstance = new App();
    
    // Make app instance globally available for debugging and emergency access
    if (process.env.NODE_ENV === 'development') {
        window.app = applicationInstance;
    }

    try {
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
            </div>
        `;
    }
});

// Export for testing and potential module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { App };
}