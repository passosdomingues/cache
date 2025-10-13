/**
 * @file ViewManager.js
 * @author Rafael Passos Domingues
 * @version 3.0.0
 * @brief Advanced view management and rendering system for single-page applications.
 * @description Manages view registration, rendering, transitions, and caching
 *              with performance optimization and error handling.
 */

/**
 * @class ViewManager
 * @brief Central view management system for the application
 * @description Handles view registration, rendering, lifecycle management,
 *              and provides caching and transition capabilities
 */
class ViewManager {
    /**
     * @brief Creates a new ViewManager instance
     * @constructor
     * @param {Object} options - Configuration options
     * @param {HTMLElement} options.viewContainer - DOM element to render views into
     * @param {boolean} options.enableCaching - Whether to enable view caching
     */
    constructor(options = {}) {
        const {
            viewContainer = null,
            enableCaching = true
        } = options;

        /**
         * @private
         * @type {Map}
         * @brief Registry of available views
         */
        this.viewRegistry = new Map();

        /**
         * @private
         * @type {string|null}
         * @brief Currently active view name
         */
        this.currentActiveView = null;

        /**
         * @private
         * @type {HTMLElement|null}
         * @brief Container element where views are rendered
         */
        this.viewContainer = viewContainer;

        /**
         * @private
         * @type {boolean}
         * @brief Whether view caching is enabled
         */
        this.enableCaching = enableCaching;

        /**
         * @private
         * @type {Map}
         * @brief Cache for rendered view content
         */
        this.viewCache = new Map();

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

        console.debug('ViewManager: Instance created with options:', options);
    }

    /**
     * @brief Initializes the ViewManager
     * @public
     * @returns {Promise<void>} Resolves when initialization is complete
     */
    async initialize() {
        if (this.isInitialized) {
            console.warn('ViewManager: Already initialized.');
            return;
        }

        try {
            // Validate view container
            if (!this.viewContainer || !(this.viewContainer instanceof HTMLElement)) {
                throw new Error('ViewManager: Valid view container is required.');
            }

            // Set up event listeners
            this.setupEventListeners();

            this.isInitialized = true;
            console.info('ViewManager: Successfully initialized.');

        } catch (error) {
            console.error('ViewManager: Initialization failed:', error);
            throw error;
        }
    }

    /**
     * @brief Sets up event listeners for view management
     * @private
     */
    setupEventListeners() {
        const { signal } = this.eventAbortController;

        // Listen for view change requests
        document.addEventListener('router:viewchange', (event) => {
            this.handleViewChangeRequest(event.detail);
        }, { signal });

        // Listen for application state changes that might affect views
        document.addEventListener('maincontroller:viewChanged', (event) => {
            this.handleApplicationViewChange(event.detail);
        }, { signal });

        console.debug('ViewManager: Event listeners established.');
    }

    /**
     * @brief Handles view change requests from the router
     * @private
     * @param {Object} viewData - View change data
     */
    async handleViewChangeRequest(viewData) {
        const { viewName, viewData: data, routeParameters } = viewData;

        try {
            await this.renderView(viewName, {
                ...data,
                routeParameters
            });
        } catch (error) {
            console.error(`ViewManager: Failed to handle view change request for ${viewName}:`, error);
            this.handleRenderError(error, viewName, data);
        }
    }

    /**
     * @brief Handles application-level view changes
     * @private
     * @param {Object} viewData - Application view change data
     */
    handleApplicationViewChange(viewData) {
        const { currentView, previousView } = viewData;

        console.debug(`ViewManager: Application view changed from ${previousView} to ${currentView}`);

        // Update internal state
        this.currentActiveView = currentView;

        // Perform any view-specific transitions or cleanup
        this.handleViewTransition(previousView, currentView);
    }

    /**
     * @brief Handles transitions between views
     * @private
     * @param {string} previousView - Previous view name
     * @param {string} currentView - Current view name
     */
    handleViewTransition(previousView, currentView) {
        // Implementation for view transitions (fade, slide, etc.)
        if (previousView && currentView && previousView !== currentView) {
            console.debug(`ViewManager: Transitioning from ${previousView} to ${currentView}`);
            
            // Add transition classes for CSS animations
            if (this.viewContainer) {
                this.viewContainer.classList.add('view-transition');
                setTimeout(() => {
                    this.viewContainer.classList.remove('view-transition');
                }, 300);
            }
        }
    }

    /**
     * @brief Registers a view with the ViewManager
     * @public
     * @param {string} viewName - Unique identifier for the view
     * @param {Object} viewInstance - View instance with render method
     * @throws {Error} When viewName or viewInstance are invalid
     */
    registerView(viewName, viewInstance) {
        if (!viewName || typeof viewName !== 'string') {
            throw new Error('ViewManager: viewName must be a non-empty string.');
        }

        if (!viewInstance || typeof viewInstance !== 'object') {
            throw new Error('ViewManager: viewInstance must be a valid object.');
        }

        if (typeof viewInstance.render !== 'function') {
            throw new Error('ViewManager: viewInstance must have a render method.');
        }

        this.viewRegistry.set(viewName, viewInstance);
        console.debug(`ViewManager: View "${viewName}" registered successfully.`);
    }

    /**
     * @brief Renders a specific view with provided data
     * @public
     * @param {string} viewName - Name of the view to render
     * @param {Object} data - Data to pass to the view for rendering
     * @returns {Promise<void>} Resolves when the view is rendered
     * @throws {Error} When view is not found or rendering fails
     */
    async renderView(viewName, data = {}) {
        if (!this.isInitialized) {
            throw new Error('ViewManager: Must be initialized before rendering views.');
        }

        if (!viewName || typeof viewName !== 'string') {
            throw new Error('ViewManager: viewName must be a non-empty string.');
        }

        const viewInstance = this.viewRegistry.get(viewName);
        if (!viewInstance) {
            throw new Error(`ViewManager: View "${viewName}" not found in registry.`);
        }

        try {
            console.debug(`ViewManager: Rendering view "${viewName}" with data:`, data);

            // Check cache if enabled
            const cacheKey = this.generateCacheKey(viewName, data);
            if (this.enableCaching && this.viewCache.has(cacheKey)) {
                console.debug(`ViewManager: Using cached content for view "${viewName}"`);
                const cachedContent = this.viewCache.get(cacheKey);
                this.updateViewContainer(cachedContent);
            } else {
                // Render the view
                const renderedContent = await viewInstance.render(data);
                
                // Cache the result if caching is enabled
                if (this.enableCaching && renderedContent) {
                    this.viewCache.set(cacheKey, renderedContent);
                }

                // Update the view container
                this.updateViewContainer(renderedContent);
            }

            // Update current active view
            this.currentActiveView = viewName;

            // Dispatch view rendered event
            this.dispatchViewEvent('viewRendered', {
                viewName,
                data,
                timestamp: Date.now()
            });

            console.debug(`ViewManager: View "${viewName}" rendered successfully.`);

        } catch (error) {
            console.error(`ViewManager: Failed to render view "${viewName}":`, error);
            this.dispatchViewEvent('viewRenderError', {
                viewName,
                error: error.message,
                data
            });
            throw error;
        }
    }

    /**
     * @brief Generates a cache key for view data
     * @private
     * @param {string} viewName - Name of the view
     * @param {Object} data - View data
     * @returns {string} Cache key
     */
    generateCacheKey(viewName, data) {
        const dataString = JSON.stringify(data);
        return `${viewName}-${Buffer.from(dataString).toString('base64')}`;
    }

    /**
     * @brief Updates the view container with rendered content
     * @private
     * @param {string} content - HTML content to render
     */
    updateViewContainer(content) {
        if (!this.viewContainer) {
            console.warn('ViewManager: No view container available for rendering.');
            return;
        }

        if (typeof content === 'string') {
            this.viewContainer.innerHTML = content;
        } else {
            console.warn('ViewManager: Render method should return HTML string.');
            this.viewContainer.innerHTML = '<div class="view-error">Invalid view content</div>';
        }
    }

    /**
     * @brief Renders all registered views (for preloading or initialization)
     * @public
     * @returns {Promise<void>} Resolves when all views are rendered
     */
    async renderAllViews() {
        if (!this.isInitialized) {
            throw new Error('ViewManager: Must be initialized before rendering views.');
        }

        console.info("ViewManager: Rendering all registered views.");

        const renderPromises = [];
        
        for (const [viewName, viewInstance] of this.viewRegistry) {
            renderPromises.push(
                this.renderView(viewName).catch(error => {
                    console.error(`ViewManager: Failed to render view "${viewName}":`, error);
                })
            );
        }

        await Promise.allSettled(renderPromises);
        console.info("ViewManager: All views rendering attempted.");
    }

    /**
     * @brief Handles view rendering errors
     * @private
     * @param {Error} error - The rendering error
     * @param {string} viewName - Name of the view that failed
     * @param {Object} data - Data used for rendering
     */
    handleRenderError(error, viewName, data) {
        console.error(`ViewManager: Render error for view "${viewName}":`, error);

        // Show error fallback in view container
        if (this.viewContainer) {
            this.viewContainer.innerHTML = `
                <div class="view-error-state">
                    <h3>View Loading Error</h3>
                    <p>Failed to load the "${viewName}" view. Please try again.</p>
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

        // Dispatch error event
        this.dispatchViewEvent('viewRenderError', {
            viewName,
            error: error.message,
            data,
            timestamp: Date.now()
        });
    }

    /**
     * @brief Dispatches view-related events
     * @private
     * @param {string} eventType - Type of view event
     * @param {Object} eventData - Additional event data
     */
    dispatchViewEvent(eventType, eventData = {}) {
        const viewEvent = new CustomEvent(`viewmanager:${eventType}`, {
            detail: {
                source: 'ViewManager',
                ...eventData
            },
            bubbles: true,
            cancelable: true
        });

        document.dispatchEvent(viewEvent);
    }

    /**
     * @brief Gets the current active view
     * @public
     * @returns {string|null} Current active view name
     */
    getCurrentView() {
        return this.currentActiveView;
    }

    /**
     * @brief Gets all registered view names
     * @public
     * @returns {Array} Array of registered view names
     */
    getRegisteredViews() {
        return Array.from(this.viewRegistry.keys());
    }

    /**
     * @brief Clears the view cache
     * @public
     * @returns {number} Number of items cleared from cache
     */
    clearCache() {
        const cacheSize = this.viewCache.size;
        this.viewCache.clear();
        console.debug(`ViewManager: Cleared ${cacheSize} items from view cache.`);
        return cacheSize;
    }

    /**
     * @brief Reduces performance impact when tab is not visible
     * @public
     */
    reducePerformanceWhenHidden() {
        // Clear cache to free memory
        this.clearCache();
        
        // Disable expensive operations
        this.enableCaching = false;
        
        console.debug('ViewManager: Performance reduced for hidden tab.');
    }

    /**
     * @brief Cleans up resources and event listeners
     * @public
     */
    destroy() {
        // Abort all event listeners
        this.eventAbortController.abort();

        // Clear registries and caches
        this.viewRegistry.clear();
        this.viewCache.clear();

        // Reset state
        this.currentActiveView = null;
        this.isInitialized = false;

        console.info('ViewManager: Destroyed and resources cleaned up.');
    }
}

export default ViewManager;