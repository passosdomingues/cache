/**
 * @file MainController.js
 * @author Rafael Passos Domingues
 * @version 3.0.0
 * @brief Main application controller implementing MVC orchestrator pattern.
 * @description Acts as the central orchestrator in the MVC pattern,
 * connecting models, views, and sub-controllers while managing initialization flow,
 * error handling, and inter-component communication.
 */

// View Imports
import NavigationView from '../views/NavigationView.js';
import HeroView from '../views/HeroView.js';
import SectionView from '../views/SectionView.js';
import FooterView from '../views/FooterView.js';

// Controller Imports
import NavigationController from './NavigationController.js';
import SectionController from './SectionController.js';

// Constants
/**
 * @constant {Object} VIEW_SELECTORS
 * @brief CSS selectors for DOM elements associated with views
 * @description Maps view names to their corresponding DOM selectors for dynamic element resolution
 */
const VIEW_SELECTORS = {
    navigation: '[data-view="navigation"]',
    hero: '[data-view="hero"]',
    mainContent: '#main-content',
    footer: '[data-view="footer"]'
};

/**
 * @constant {Object} ERROR_MESSAGES
 * @brief Standardized error messages for application error handling
 */
const ERROR_MESSAGES = {
    invalidModels: 'MainController requires a valid models object for initialization.',
    viewConnectionFailed: 'Failed to connect views to DOM elements.',
    controllerInitializationFailed: 'Failed to initialize sub-controllers.',
    renderFailure: 'Critical failure during application rendering.',
    eventHandlerSetupFailed: 'Failed to set up event handlers between components.'
};

/**
 * @class MainController
 * @brief Central application controller managing MVC component orchestration
 * @description Coordinates between models, views, and controllers to ensure
 * proper data flow, initialization sequence, and inter-component communication
 */
class MainController {
    /**
     * @brief Creates an instance of MainController
     * @constructor
     * @param {Object} models - Collection of main application model instances
     * @param {Object} models.user - User data model instance
     * @param {Object} models.content - Content data model instance
     * @throws {TypeError} When models parameter is invalid or missing required models
     */
    constructor(models) {
        this.validateModels(models);
        
        /**
         * @private
         * @type {Object}
         * @brief Collection of application data models
         */
        this.models = models;
        
        /**
         * @private
         * @type {Object}
         * @brief Collection of view instances keyed by view name
         */
        this.views = {};
        
        /**
         * @private
         * @type {Object}
         * @brief Collection of sub-controller instances keyed by controller name
         */
        this.controllers = {};
        
        /**
         * @private
         * @type {boolean}
         * @brief Tracks initialization state of the controller
         */
        this.isInitialized = false;
        
        /**
         * @private
         * @type {AbortController}
         * @brief Manages cleanup of event listeners for proper memory management
         */
        this.eventAbortController = new AbortController();
        
        // Bind methods to maintain context
        this.handleNavigationEvent = this.handleNavigationEvent.bind(this);
        this.handleHeroEvent = this.handleHeroEvent.bind(this);
        this.handleSectionEvent = this.handleSectionEvent.bind(this);
        this.handleGlobalError = this.handleGlobalError.bind(this);
        this.handleInitializationError = this.handleInitializationError.bind(this);
    }

    /**
     * @brief Validates the models object structure and required properties
     * @private
     * @param {Object} models - Models object to validate
     * @throws {TypeError} When models object is invalid or missing required models
     */
    validateModels(models) {
        if (typeof models !== 'object' || models === null) {
            throw new TypeError(ERROR_MESSAGES.invalidModels);
        }

        const requiredModels = ['user', 'content'];
        const missingModels = requiredModels.filter(modelName => 
            !(modelName in models)
        );

        if (missingModels.length > 0) {
            throw new TypeError(
                `MainController requires the following models: ${missingModels.join(', ')}`
            );
        }
    }

    /**
     * @brief Main application entry point
     * @public
     * @description Orchestrates the complete application initialization sequence including
     * DOM view connection, controller initialization, rendering, and event system setup
     * @returns {Promise<void>} Resolves when application is fully initialized
     * @throws {Error} When critical initialization steps fail
     */
    async initializeApplication() {
        try {
            await this.executeInitializationSequence();
            this.isInitialized = true;
            
            console.info('MainController: Application successfully initialized and ready.');
            
            // Dispatch custom event for application readiness
            this.dispatchApplicationReadyEvent();
            
        } catch (error) {
            await this.handleInitializationError(error);
            throw error;
        }
    }

    /**
     * @brief Executes the ordered sequence of initialization steps
     * @private
     * @returns {Promise<void>} Resolves when all initialization steps complete successfully
     */
    async executeInitializationSequence() {
        const initializationSteps = [
            { name: 'connectViewsToDOM', method: this.connectViewsToDOM.bind(this) },
            { name: 'initializeSubControllers', method: this.initializeSubControllers.bind(this) },
            { name: 'renderApplicationContent', method: this.renderApplicationContent.bind(this) },
            { name: 'setupEventHandlers', method: this.setupEventHandlers.bind(this) },
            { name: 'setupGlobalErrorHandling', method: this.setupGlobalErrorHandling.bind(this) }
        ];

        for (const step of initializationSteps) {
            try {
                await step.method();
                console.debug(`MainController: Successfully completed initialization step: ${step.name}`);
            } catch (stepError) {
                console.error(`MainController: Failed initialization step ${step.name}:`, stepError);
                throw new Error(`Initialization step ${step.name} failed: ${stepError.message}`);
            }
        }
    }

    /**
     * @brief Connects view instances to their corresponding DOM elements
     * @private
     * @returns {Promise<void>} Resolves when all views are successfully connected
     * @throws {Error} When critical DOM elements are not found
     */
    async connectViewsToDOM() {
        try {
            const viewConnectionPromises = Object.entries(VIEW_SELECTORS).map(
                async ([viewName, selector]) => {
                    const domElement = document.querySelector(selector);
                    
                    if (!domElement) {
                        console.warn(`MainController: DOM element not found for selector: ${selector}`);
                        return;
                    }

                    await this.instantiateView(viewName, domElement);
                }
            );

            await Promise.allSettled(viewConnectionPromises);
            
            console.info('MainController: View-to-DOM connection completed.');
            
        } catch (error) {
            console.error(ERROR_MESSAGES.viewConnectionFailed, error);
            throw new Error(ERROR_MESSAGES.viewConnectionFailed);
        }
    }

    /**
     * @brief Dynamically instantiates a view and adds it to the views collection
     * @private
     * @param {string} viewName - Name identifier for the view
     * @param {HTMLElement} domElement - DOM element to which the view will be bound
     * @returns {Promise<void>} Resolves when view is successfully instantiated
     */
    async instantiateView(viewName, domElement) {
        const viewClasses = {
            navigation: NavigationView,
            hero: HeroView,
            section: SectionView,
            footer: FooterView
        };

        const ViewClass = viewClasses[viewName];
        if (!ViewClass) {
            console.warn(`MainController: No view class found for: ${viewName}`);
            return;
        }

        try {
            this.views[viewName] = new ViewClass(domElement);
            console.debug(`MainController: Successfully instantiated view: ${viewName}`);
        } catch (viewError) {
            console.error(`MainController: Failed to instantiate view ${viewName}:`, viewError);
            throw viewError;
        }
    }

    /**
     * @brief Initializes all sub-controllers with their required dependencies
     * @private
     * @returns {Promise<void>} Resolves when all controllers are initialized
     * @throws {Error} When critical controller initialization fails
     */
    async initializeSubControllers() {
        try {
            this.controllers.navigation = new NavigationController();
            
            // Section controller requires both models and section view
            this.controllers.section = new SectionController(
                this.models,
                this.views.section
            );

            // Initialize controllers that have async initialization
            const initializationPromises = Object.values(this.controllers).map(
                controller => {
                    if (controller.initialize && typeof controller.initialize === 'function') {
                        return controller.initialize();
                    }
                    return Promise.resolve();
                }
            );

            await Promise.all(initializationPromises);
            
            console.info('MainController: All sub-controllers initialized successfully.');
            
        } catch (error) {
            console.error(ERROR_MESSAGES.controllerInitializationFailed, error);
            throw new Error(ERROR_MESSAGES.controllerInitializationFailed);
        }
    }

    /**
     * @brief Renders all main application sections with appropriate data
     * @private
     * @returns {Promise<void>} Resolves when all views are successfully rendered
     * @throws {Error} When required data is unavailable or rendering fails
     */
    async renderApplicationContent() {
        try {
            const userData = await this.models.user.getUserData();
            const sectionsData = await this.models.content.getSections();

            if (!userData || !sectionsData) {
                throw new Error('Incomplete data for application rendering');
            }

            await this.renderAllViews(userData, sectionsData);
            console.info('MainController: All application views rendered successfully.');
            
        } catch (error) {
            console.error(ERROR_MESSAGES.renderFailure, error);
            throw new Error(ERROR_MESSAGES.renderFailure);
        }
    }

    /**
     * @brief Coordinates the rendering of all individual views
     * @private
     * @param {Object} userData - Complete user data object
     * @param {Array} sectionsData - Array of section data objects
     * @returns {Promise<void>} Resolves when all views are rendered
     */
    async renderAllViews(userData, sectionsData) {
        const renderOperations = [];

        if (this.views.navigation) {
            renderOperations.push(
                this.views.navigation.render({
                    name: userData.name,
                    sections: sectionsData
                })
            );
        }

        if (this.views.hero) {
            renderOperations.push(this.views.hero.render(userData));
        }

        if (this.views.footer) {
            renderOperations.push(this.views.footer.render(userData));
        }

        if (this.views.section) {
            renderOperations.push(
                this.views.section.renderSections(sectionsData)
            );
        }

        await Promise.allSettled(renderOperations);
    }

    /**
     * @brief Establishes event-based communication between views and controllers
     * @private
     * @returns {Promise<void>} Resolves when all event handlers are set up
     * @throws {Error} When event handler setup fails
     */
    async setupEventHandlers() {
        try {
            const eventSignal = this.eventAbortController.signal;

            this.setupNavigationEventHandlers(eventSignal);
            this.setupHeroEventHandlers(eventSignal);
            this.setupSectionEventHandlers(eventSignal);

            console.info('MainController: Event-based communication system established.');
            
        } catch (error) {
            console.error(ERROR_MESSAGES.eventHandlerSetupFailed, error);
            throw new Error(ERROR_MESSAGES.eventHandlerSetupFailed);
        }
    }

    /**
     * @brief Sets up event handlers for navigation-related view events
     * @private
     * @param {AbortSignal} abortSignal - Signal for cleaning up event listeners
     */
    setupNavigationEventHandlers(abortSignal) {
        if (!this.views.navigation) return;

        this.views.navigation.addObserver(this.handleNavigationEvent, { signal: abortSignal });
    }

    /**
     * @brief Handles navigation events from the navigation view
     * @private
     * @param {string} eventType - Type of navigation event
     * @param {Object} eventData - Data associated with the navigation event
     */
    handleNavigationEvent(eventType, eventData) {
        switch (eventType) {
            case 'navigateToSection':
                if (this.controllers.navigation && this.controllers.navigation.navigateToSection) {
                    this.controllers.navigation.navigateToSection(eventData.sectionId);
                }
                break;
            case 'menuToggle':
                if (this.controllers.navigation && this.controllers.navigation.toggleMobileMenu) {
                    this.controllers.navigation.toggleMobileMenu(eventData.isOpen);
                }
                break;
            default:
                console.warn(`MainController: Unhandled navigation event: ${eventType}`);
        }
    }

    /**
     * @brief Sets up event handlers for hero section view events
     * @private
     * @param {AbortSignal} abortSignal - Signal for cleaning up event listeners
     */
    setupHeroEventHandlers(abortSignal) {
        if (!this.views.hero) return;

        this.views.hero.addObserver(this.handleHeroEvent, { signal: abortSignal });
    }

    /**
     * @brief Handles events from the hero view
     * @private
     * @param {string} eventType - Type of hero event
     * @param {Object} eventData - Data associated with the hero event
     */
    handleHeroEvent(eventType, eventData) {
        switch (eventType) {
            case 'scrollToSection':
                if (this.controllers.navigation && this.controllers.navigation.navigateToSection) {
                    this.controllers.navigation.navigateToSection(eventData.sectionId);
                }
                break;
            case 'ctaButtonClick':
                this.handleCallToAction(eventData.actionType);
                break;
            default:
                console.warn(`MainController: Unhandled hero event: ${eventType}`);
        }
    }

    /**
     * @brief Sets up event handlers for section view events
     * @private
     * @param {AbortSignal} abortSignal - Signal for cleaning up event listeners
     */
    setupSectionEventHandlers(abortSignal) {
        if (!this.views.section) return;

        this.views.section.addObserver(this.handleSectionEvent, { signal: abortSignal });
    }

    /**
     * @brief Handles events from section views
     * @private
     * @param {string} eventType - Type of section event
     * @param {Object} eventData - Data associated with the section event
     */
    handleSectionEvent(eventType, eventData) {
        switch (eventType) {
            case 'sectionVisible':
                if (this.controllers.navigation && this.controllers.navigation.highlightSection) {
                    this.controllers.navigation.highlightSection(eventData.sectionId);
                }
                break;
            case 'sectionInteraction':
                this.handleSectionInteraction(eventData);
                break;
            default:
                console.warn(`MainController: Unhandled section event: ${eventType}`);
        }
    }

    /**
     * @brief Handles call-to-action events from interactive elements
     * @private
     * @param {string} actionType - Type of CTA action to perform
     */
    handleCallToAction(actionType) {
        const actionHandlers = {
            contact: () => {
                if (this.controllers.navigation && this.controllers.navigation.navigateToSection) {
                    this.controllers.navigation.navigateToSection('contact');
                }
            },
            projects: () => {
                if (this.controllers.navigation && this.controllers.navigation.navigateToSection) {
                    this.controllers.navigation.navigateToSection('projects');
                }
            },
            download: () => this.handleDownloadAction()
        };

        const handler = actionHandlers[actionType];
        if (handler) {
            handler();
        } else {
            console.warn(`MainController: Unhandled CTA action: ${actionType}`);
        }
    }

    /**
     * @brief Handles download-related actions
     * @private
     */
    handleDownloadAction() {
        // Implementation for download handling
        console.debug('MainController: Handling download action');
    }

    /**
     * @brief Handles various section interactions
     * @private
     * @param {Object} interactionData - Data about the section interaction
     */
    handleSectionInteraction(interactionData) {
        // Handle various section interactions like form submissions, button clicks, etc.
        console.debug('MainController: Handling section interaction', interactionData);
    }

    /**
     * @brief Sets up global error handling for the application
     * @private
     */
    setupGlobalErrorHandling() {
        window.addEventListener('error', this.handleGlobalError);
        window.addEventListener('unhandledrejection', this.handleGlobalError);
    }

    /**
     * @brief Global error handler for uncaught exceptions and promise rejections
     * @private
     * @param {ErrorEvent|PromiseRejectionEvent} errorEvent - The error event
     */
    handleGlobalError(errorEvent) {
        console.error('MainController: Global error captured:', errorEvent);
        
        // In a production environment, send to error reporting service
        this.reportErrorToMonitoringService(errorEvent);
        
        // Show user-friendly error message for critical errors
        if (this.shouldShowUserError(errorEvent)) {
            this.showUserFriendlyError();
        }
    }

    /**
     * @brief Reports errors to external monitoring service
     * @private
     * @param {ErrorEvent|PromiseRejectionEvent} errorEvent - Error event to report
     */
    reportErrorToMonitoringService(errorEvent) {
        // Integration point for services like Sentry, LogRocket, etc.
        const errorData = {
            timestamp: new Date().toISOString(),
            error: errorEvent.error || errorEvent.reason,
            message: errorEvent.message,
            stack: errorEvent.error ? errorEvent.error.stack : undefined
        };
        
        console.debug('MainController: Reporting error to monitoring service:', errorData);
    }

    /**
     * @brief Determines if an error should be shown to the user
     * @private
     * @param {ErrorEvent|PromiseRejectionEvent} errorEvent - Error event to evaluate
     * @returns {boolean} True if error should be shown to user
     */
    shouldShowUserError(errorEvent) {
        // Only show user-facing errors for critical application failures
        const criticalErrors = [
            'TypeError',
            'ReferenceError',
            'SyntaxError'
        ];
        
        const error = errorEvent.error || errorEvent.reason;
        return criticalErrors.some(errorType => {
            if (error && (error.name === errorType || error.constructor.name === errorType)) {
                return true;
            }
            return false;
        });
    }

    /**
     * @brief Displays user-friendly error message
     * @private
     */
    showUserFriendlyError() {
        const errorContainer = document.createElement('div');
        errorContainer.className = 'global-error-container';
        errorContainer.innerHTML = `
            <div class="error-message">
                <h3>Something went wrong</h3>
                <p>We're experiencing technical difficulties. Please try refreshing the page.</p>
                <button onclick="window.location.reload()" class="error-retry-button">
                    Retry
                </button>
            </div>
        `;
        
        document.body.prepend(errorContainer);
    }

    /**
     * @brief Dispatches application ready event for external consumers
     * @private
     */
    dispatchApplicationReadyEvent() {
        const appReadyEvent = new CustomEvent('application:ready', {
            detail: {
                timestamp: Date.now(),
                version: '3.0.0',
                controllers: Object.keys(this.controllers),
                views: Object.keys(this.views)
            }
        });
        
        window.dispatchEvent(appReadyEvent);
    }

    /**
     * @brief Handles initialization errors with graceful degradation
     * @private
     * @param {Error} error - The initialization error
     * @returns {Promise<void>} Resolves after error handling completes
     */
    async handleInitializationError(error) {
        console.error('MainController: Critical initialization error:', error);
        
        // Attempt graceful degradation
        await this.attemptGracefulDegradation();
        
        // Show error state to user
        this.showInitializationErrorState(error);
        
        // Report to monitoring
        this.reportErrorToMonitoringService({ error: error });
    }

    /**
     * @brief Attempts graceful degradation when initialization fails
     * @private
     * @returns {Promise<void>} Resolves when degradation attempt completes
     */
    async attemptGracefulDegradation() {
        try {
            // Try to render at least basic content
            const basicContent = this.models.content && this.models.content.getBasicContent ? 
                await this.models.content.getBasicContent() : null;
                
            if (basicContent) {
                document.body.innerHTML = `
                    <div class="degraded-mode">
                        <h1>Rafael Passos Domingues</h1>
                        <p>${basicContent.introduction || 'Welcome to my portfolio'}</p>
                        <nav>
                            <a href="#contact">Contact</a>
                            <a href="#projects">Projects</a>
                        </nav>
                    </div>
                `;
            }
        } catch (degradationError) {
            console.error('MainController: Graceful degradation failed:', degradationError);
        }
    }

    /**
     * @brief Shows initialization error state to user
     * @private
     * @param {Error} error - The initialization error
     */
    showInitializationErrorState(error) {
        document.body.innerHTML = `
            <div class="initialization-error">
                <h1>Application Loading Issue</h1>
                <p>We're having trouble loading the application. Please try again later.</p>
                <button onclick="window.location.reload()" class="reload-button">
                    Reload Application
                </button>
                <details class="error-details">
                    <summary>Technical Details</summary>
                    <pre>${error.message}</pre>
                </details>
            </div>
        `;
    }

    /**
     * @brief Cleans up resources and event listeners
     * @public
     * @description Properly tears down the controller to prevent memory leaks
     */
    destroy() {
        // Abort all event listeners
        this.eventAbortController.abort();
        
        // Clean up controllers
        Object.values(this.controllers).forEach(controller => {
            if (typeof controller.destroy === 'function') {
                controller.destroy();
            }
        });
        
        // Clean up views
        Object.values(this.views).forEach(view => {
            if (typeof view.destroy === 'function') {
                view.destroy();
            }
        });
        
        // Remove global error handlers
        window.removeEventListener('error', this.handleGlobalError);
        window.removeEventListener('unhandledrejection', this.handleGlobalError);
        
        this.isInitialized = false;
        console.info('MainController: Controller destroyed and resources cleaned up.');
    }

    /**
     * @brief Gets the current initialization state of the controller
     * @public
     * @returns {boolean} True if controller is fully initialized
     */
    getInitializationState() {
        return this.isInitialized;
    }

    /**
     * @brief Gets a reference to a specific sub-controller
     * @public
     * @param {string} controllerName - Name of the controller to retrieve
     * @returns {Object|null} The controller instance or null if not found
     */
    getController(controllerName) {
        return this.controllers[controllerName] || null;
    }

    /**
     * @brief Gets a reference to a specific view
     * @public
     * @param {string} viewName - Name of the view to retrieve
     * @returns {Object|null} The view instance or null if not found
     */
    getView(viewName) {
        return this.views[viewName] || null;
    }
}

export default MainController;