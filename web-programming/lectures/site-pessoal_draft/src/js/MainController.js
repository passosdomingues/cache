/**
 * @file MainController.js
 * @author Rafael Passos Domingues
 * @version 3.0.0
 * @brief Main application controller implementing MVC orchestrator pattern.
 * @description Orchestrates all sub-controllers, manages application flow,
 *              and coordinates between models, views, and controllers.
 */

/**
 * @constant {Object} ERROR_MESSAGES
 * @brief Standardized error messages for MainController operations
 */
const ERROR_MESSAGES = {
    invalidModels: 'MainController requires a valid models object for initialization.',
    invalidViewManager: 'MainController requires a valid ViewManager instance.',
    invalidControllers: 'MainController requires a valid controllers object for initialization.',
    controllerInitializationFailed: 'Failed to initialize sub-controllers.',
    methodNotImplemented: 'Method not implemented in MainController.'
};

/**
 * @class MainController
 * @brief Main application controller that orchestrates all sub-controllers
 * @description Manages application flow, coordinates between MVC components,
 *              and handles high-level application logic and state management
 */
class MainController {
    /**
     * @brief Creates an instance of MainController
     * @constructor
     * @param {Object} models - Collection of application model instances
     * @param {Object} viewManager - View manager instance
     * @param {Object} controllers - Collection of sub-controller instances
     * @throws {Error} When required dependencies are not provided
     */
    constructor(models, viewManager, controllers) {
        if (!models || typeof models !== 'object') {
            throw new Error(ERROR_MESSAGES.invalidModels);
        }
        if (!viewManager) {
            throw new Error(ERROR_MESSAGES.invalidViewManager);
        }
        if (!controllers || typeof controllers !== 'object') {
            throw new Error(ERROR_MESSAGES.invalidControllers);
        }
        
        /**
         * @private
         * @type {Object}
         * @brief Collection of application data models
         */
        this.models = models;

        /**
         * @private
         * @type {Object}
         * @brief View manager instance
         */
        this.viewManager = viewManager;

        /**
         * @private
         * @type {Object}
         * @brief Collection of sub-controller instances
         */
        this.controllers = controllers;

        /**
         * @private
         * @type {boolean}
         * @brief Tracks initialization state
         */
        this.isInitialized = false;

        /**
         * @private
         * @type {AbortController}
         * @brief Manages cleanup of event listeners
         */
        this.eventAbortController = new AbortController();

        /**
         * @private
         * @type {Object}
         * @brief Application state management
         */
        this.applicationState = {
            currentView: 'home',
            previousView: null,
            isNavigationActive: false,
            hasRenderedInitialContent: false
        };

        console.debug('MainController: Instance created with models, viewManager, and controllers.');
    }

    /**
     * @brief Initializes the main controller and all sub-controllers
     * @public
     * @returns {Promise<void>} Resolves when initialization is complete
     */
    async initialize() {
        if (this.isInitialized) {
            console.warn('MainController: Already initialized.');
            return;
        }

        try {
            console.info('MainController: Starting initialization...');

            // Initialize sub-controllers in proper sequence
            await this.initializeSubControllers();

            // Set up main controller event listeners
            this.setupEventListeners();

            // Update initialization state
            this.isInitialized = true;

            console.info('MainController: Initialization complete.');

        } catch (error) {
            console.error('MainController: Initialization failed:', error);
            throw new Error(ERROR_MESSAGES.controllerInitializationFailed);
        }
    }

    /**
     * @brief Alternative initialization method called by App.js
     * @public
     * @returns {Promise<void>} Resolves when initialization is complete
     */
    async initializeApplication() {
        return this.initialize();
    }

    /**
     * @brief Initializes all sub-controllers with proper error handling
     * @private
     * @returns {Promise<void>} Resolves when all sub-controllers are initialized
     */
    async initializeSubControllers() {
        const initializationPromises = [];

        // Initialize NavigationController if available
        if (this.controllers.navigation && typeof this.controllers.navigation.initialize === 'function') {
            initializationPromises.push(
                this.controllers.navigation.initialize().catch(error => {
                    console.error('MainController: NavigationController initialization failed:', error);
                })
            );
        }

        // Initialize SectionController if available
        if (this.controllers.section && typeof this.controllers.section.initialize === 'function') {
            initializationPromises.push(
                this.controllers.section.initialize().catch(error => {
                    console.error('MainController: SectionController initialization failed:', error);
                })
            );
        }

        // Wait for all sub-controllers to initialize
        await Promise.allSettled(initializationPromises);

        console.debug('MainController: All sub-controllers initialization attempted.');
    }

    /**
     * @brief Sets up event listeners for application-wide events
     * @private
     */
    setupEventListeners() {
        const { signal } = this.eventAbortController;

        // Listen for navigation events
        document.addEventListener('navigation:sectionChanged', (event) => {
            this.handleSectionChange(event.detail);
        }, { signal });

        // Listen for view change events
        document.addEventListener('router:viewchange', (event) => {
            this.handleViewChange(event.detail);
        }, { signal });

        console.debug('MainController: Event listeners established.');
    }

    /**
     * @brief Handles section change events from navigation
     * @private
     * @param {Object} sectionData - Section change data
     */
    handleSectionChange(sectionData) {
        const { sectionId, previousSectionId } = sectionData;
        
        console.debug(`MainController: Section changed from ${previousSectionId} to ${sectionId}`);

        // Update application state
        this.applicationState.previousView = this.applicationState.currentView;
        this.applicationState.currentView = sectionId;

        // Notify SectionController about section change
        if (this.controllers.section && typeof this.controllers.section.handleSectionChange === 'function') {
            this.controllers.section.handleSectionChange(sectionData);
        }

        // Dispatch application state change event
        this.dispatchStateChangeEvent('sectionChanged', sectionData);
    }

    /**
     * @brief Handles view change events from router
     * @private
     * @param {Object} viewData - View change data
     */
    handleViewChange(viewData) {
        const { viewName, viewData: data, routeParameters } = viewData;

        console.debug(`MainController: View changed to ${viewName}`);

        // Update application state
        this.applicationState.previousView = this.applicationState.currentView;
        this.applicationState.currentView = viewName;

        // Handle different view types
        this.processViewChange(viewName, data, routeParameters);

        // Dispatch application state change event
        this.dispatchStateChangeEvent('viewChanged', viewData);
    }

    /**
     * @brief Processes view changes and coordinates rendering
     * @private
     * @param {string} viewName - Name of the view to render
     * @param {Object} viewData - Data for the view
     * @param {Object} routeParameters - Route parameters
     */
    async processViewChange(viewName, viewData, routeParameters) {
        try {
            // Use ViewManager to render the requested view
            if (this.viewManager && typeof this.viewManager.renderView === 'function') {
                await this.viewManager.renderView(viewName, {
                    ...viewData,
                    routeParameters
                });
            } else {
                console.warn('MainController: ViewManager not available for rendering.');
            }

        } catch (error) {
            console.error(`MainController: Failed to process view change for ${viewName}:`, error);
            this.handleViewRenderError(error, viewName, viewData);
        }
    }

    /**
     * @brief Handles route changes from the router
     * @public
     * @param {Object} routeData - Route change data
     * @returns {Promise<void>} Resolves when route change is processed
     */
    async handleRouteChange(routeData) {
        if (!routeData) {
            console.warn('MainController: Invalid route data provided.');
            return;
        }

        const { viewName, viewData, routeParameters } = routeData;

        try {
            await this.processViewChange(viewName, viewData, routeParameters);
        } catch (error) {
            console.error(`MainController: Failed to handle route change for ${viewName}:`, error);
            throw error;
        }
    }

    /**
     * @brief Renders initial application content
     * @public
     * @returns {Promise<void>} Resolves when initial content is rendered
     */
    async renderInitialContent() {
        if (this.applicationState.hasRenderedInitialContent) {
            console.warn('MainController: Initial content already rendered.');
            return;
        }

        try {
            console.info('MainController: Rendering initial application content...');

            // Get initial sections data from content model
            let sectionsData = [];
            if (this.models.content && typeof this.models.content.getSections === 'function') {
                sectionsData = await this.models.content.getSections();
            } else {
                // Fallback sections data
                sectionsData = [
                    { id: 'about', title: 'About Me', type: 'about' },
                    { id: 'projects', title: 'Projects', type: 'projects' },
                    { id: 'research', title: 'Research', type: 'research' },
                    { id: 'contact', title: 'Contact', type: 'contact' }
                ];
            }

            // Use SectionController to render sections
            if (this.controllers.section && typeof this.controllers.section.renderSections === 'function') {
                await this.controllers.section.renderSections(sectionsData);
            } else {
                console.warn('MainController: SectionController not available for rendering sections.');
            }

            // Update state
            this.applicationState.hasRenderedInitialContent = true;

            console.info('MainController: Initial content rendered successfully.');

        } catch (error) {
            console.error('MainController: Failed to render initial content:', error);
            throw error;
        }
    }

    /**
     * @brief Handles view rendering errors
     * @private
     * @param {Error} error - The rendering error
     * @param {string} viewName - Name of the view that failed to render
     * @param {Object} viewData - Data used for rendering
     */
    handleViewRenderError(error, viewName, viewData) {
        console.error(`MainController: View render error for ${viewName}:`, error);

        // Dispatch error event
        this.dispatchStateChangeEvent('viewRenderError', {
            viewName,
            error: error.message,
            viewData
        });

        // Show fallback content or error message
        this.showErrorFallback(viewName, error);
    }

    /**
     * @brief Shows error fallback content
     * @private
     * @param {string} viewName - Name of the view that failed
     * @param {Error} error - The error that occurred
     */
    showErrorFallback(viewName, error) {
        const mainContent = document.getElementById('main-content');
        if (!mainContent) return;

        const errorHTML = `
            <div class="view-error-fallback">
                <h2>Unable to Load ${viewName.charAt(0).toUpperCase() + viewName.slice(1)}</h2>
                <p>We encountered an issue while loading this section. Please try refreshing the page.</p>
                <button onclick="window.location.reload()" class="btn btn--primary">
                    Reload Page
                </button>
                <details class="error-details">
                    <summary>Technical Details</summary>
                    <pre>${error.message}</pre>
                </details>
            </div>
        `;

        // Find or create error container
        let errorContainer = mainContent.querySelector('.view-error-fallback');
        if (!errorContainer) {
            errorContainer = document.createElement('div');
            mainContent.appendChild(errorContainer);
        }
        errorContainer.innerHTML = errorHTML;
    }

    /**
     * @brief Dispatches application state change events
     * @private
     * @param {string} eventType - Type of state change
     * @param {Object} eventData - Additional event data
     */
    dispatchStateChangeEvent(eventType, eventData = {}) {
        const stateEvent = new CustomEvent(`maincontroller:${eventType}`, {
            detail: {
                timestamp: Date.now(),
                currentState: { ...this.applicationState },
                ...eventData
            },
            bubbles: true,
            cancelable: true
        });

        document.dispatchEvent(stateEvent);
    }

    /**
     * @brief Sets sub-controllers after initialization
     * @public
     * @param {Object} controllers - Collection of sub-controller instances
     */
    setControllers(controllers) {
        if (!controllers || typeof controllers !== 'object') {
            throw new Error(ERROR_MESSAGES.invalidControllers);
        }

        this.controllers = {
            ...this.controllers,
            ...controllers
        };

        console.debug('MainController: Controllers updated.', Object.keys(this.controllers));
    }

    /**
     * @brief Gets the initialization state of the controller
     * @public
     * @returns {boolean} True if the controller is initialized
     */
    getInitializationState() {
        return this.isInitialized;
    }

    /**
     * @brief Gets current application state
     * @public
     * @returns {Object} Current application state object
     */
    getApplicationState() {
        return { ...this.applicationState };
    }

    /**
     * @brief Updates application configuration
     * @public
     * @param {Object} newConfig - New configuration options
     */
    updateConfiguration(newConfig) {
        // Implementation for configuration updates
        console.debug('MainController: Configuration updated.', newConfig);
    }

    /**
     * @brief Cleans up resources and event listeners
     * @public
     */
    destroy() {
        // Abort all event listeners
        this.eventAbortController.abort();

        // Destroy sub-controllers
        if (this.controllers.navigation && typeof this.controllers.navigation.destroy === 'function') {
            this.controllers.navigation.destroy();
        }
        if (this.controllers.section && typeof this.controllers.section.destroy === 'function') {
            this.controllers.section.destroy();
        }

        // Reset state
        this.isInitialized = false;
        this.applicationState = {
            currentView: 'home',
            previousView: null,
            isNavigationActive: false,
            hasRenderedInitialContent: false
        };

        console.info('MainController: Controller destroyed and resources cleaned up.');
    }
}

export default MainController;