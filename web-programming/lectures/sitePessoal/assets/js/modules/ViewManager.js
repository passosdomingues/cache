/**
 * @file ViewManager.js
 * @author Rafael Passos Domingues
 * @version 3.0.0
 * @brief Advanced view management and rendering system for single-page applications.
 * @description Handles dynamic view loading, rendering, lifecycle management,
 * performance optimization, and error handling with comprehensive state tracking.
 */

/**
 * @constant {Object} VIEW_CONFIGURATION
 * @brief Configuration constants for view management behavior
 * @description Defines view loading strategies, performance settings, and behavior thresholds
 */
const VIEW_CONFIGURATION = {
    CRITICAL_VIEWS: ['navigation', 'hero', 'footer'],
    LAZY_LOADING: {
        rootMargin: '50px 0px',
        threshold: 0.1,
        preloadBuffer: 3 // Number of adjacent views to preload
    },
    PERFORMANCE: {
        viewTransitionDuration: 300,
        loadingTimeout: 10000, // 10 seconds
        cacheSize: 20,
        preloadDelay: 100
    },
    ERROR_HANDLING: {
        maxRetryAttempts: 2,
        retryDelay: 1000,
        fallbackView: 'error'
    }
};

/**
 * @constant {Object} VIEW_EVENTS
 * @brief Custom event types for view management system
 * @description Defines standardized event names for view lifecycle and state changes
 */
const VIEW_EVENTS = {
    VIEW_CHANGED: 'viewmanager:viewchanged',
    VIEW_LOADING_START: 'viewmanager:loadingstart',
    VIEW_LOADING_END: 'viewmanager:loadingend',
    VIEW_ERROR: 'viewmanager:error',
    VIEW_PRELOADED: 'viewmanager:preloaded',
    VIEW_CACHED: 'viewmanager:cached'
};

/**
 * @class ViewManager
 * @brief Advanced view lifecycle management and rendering system
 * @description Manages dynamic view loading, rendering, caching, and lifecycle events
 * with performance optimization, error handling, and accessibility features
 */
class ViewManager {
    /**
     * @brief Creates a ViewManager instance
     * @constructor
     * @param {Object} configuration - Configuration options for view management
     * @param {HTMLElement} configuration.viewContainer - DOM element for view content
     * @param {Object} configuration.loadingStrategies - View loading strategy configuration
     * @throws {Error} When required configuration is invalid or missing
     */
    constructor(configuration = {}) {
        this.validateConfiguration(configuration);

        /**
         * @private
         * @type {Map}
         * @brief Cache of loaded view modules for performance optimization
         */
        this.viewModuleCache = new Map();

        /**
         * @private
         * @type {string|null}
         * @brief Currently active view identifier
         */
        this.currentActiveView = null;

        /**
         * @private
         * @type {HTMLElement}
         * @brief DOM container element for view content rendering
         */
        this.viewContainer = configuration.viewContainer || document.getElementById('main-content');

        /**
         * @private
         * @type {Map}
         * @brief Tracks loading states of views with timestamps and metadata
         */
        this.viewLoadingStates = new Map();

        /**
         * @private
         * @type {IntersectionObserver|null}
         * @brief Observer for lazy loading views based on viewport visibility
         */
        this.lazyLoadingObserver = null;

        /**
         * @private
         * @type {AbortController}
         * @brief Manages cleanup of event listeners and async operations
         */
        this.operationAbortController = new AbortController();

        /**
         * @private
         * @type {Object}
         * @brief Performance metrics and analytics for view operations
         */
        this.performanceMetrics = {
            viewLoadTimes: new Map(),
            cacheHitRate: 0,
            totalViewsRendered: 0,
            errorCount: 0
        };

        /**
         * @private
         * @type {Object}
         * @brief Configuration settings merged with defaults
         */
        this.configuration = {
            ...VIEW_CONFIGURATION,
            ...configuration
        };

        this.initializeViewManager();
    }

    /**
     * @brief Validates constructor configuration parameters
     * @private
     * @param {Object} configuration - Configuration object to validate
     * @throws {Error} When configuration is invalid or view container is missing
     */
    validateConfiguration(configuration) {
        if (configuration.viewContainer && !(configuration.viewContainer instanceof HTMLElement)) {
            throw new Error('ViewManager: viewContainer must be a valid HTMLElement');
        }

        if (!configuration.viewContainer && !document.getElementById('main-content')) {
            throw new Error('ViewManager: viewContainer not provided and main-content element not found');
        }
    }

    /**
     * @brief Initializes the view manager system
     * @private
     */
    initializeViewManager() {
        console.info('ViewManager: Initializing view management system...');
        
        // Set up accessibility attributes for view container
        this.setupViewContainerAccessibility();
    }

    /**
     * @brief Sets up accessibility attributes for the view container
     * @private
     */
    setupViewContainerAccessibility() {
        if (this.viewContainer) {
            this.viewContainer.setAttribute('role', 'main');
            this.viewContainer.setAttribute('aria-live', 'polite');
            this.viewContainer.setAttribute('aria-atomic', 'true');
        }
    }

    /**
     * @brief Initializes the view manager with critical systems
     * @public
     * @returns {Promise<void>} Resolves when view manager is fully initialized
     */
    async initialize() {
        try {
            const initializationTasks = [
                this.preloadCriticalViews(),
                this.setupLazyLoadingObserver(),
                this.setupGlobalErrorHandling()
            ];

            await Promise.allSettled(initializationTasks);
            
            console.info('ViewManager: Successfully initialized view management system.');
            
        } catch (error) {
            console.error('ViewManager: Failed to initialize:', error);
            throw error;
        }
    }

    /**
     * @brief Preloads critical views for optimal initial page load performance
     * @private
     * @returns {Promise<void>} Resolves when critical views are preloaded
     */
    async preloadCriticalViews() {
        const criticalViewPromises = this.configuration.CRITICAL_VIEWS.map(viewName =>
            this.preloadViewModule(viewName)
        );

        const results = await Promise.allSettled(criticalViewPromises);
        
        results.forEach((result, index) => {
            const viewName = this.configuration.CRITICAL_VIEWS[index];
            if (result.status === 'fulfilled') {
                console.debug(`ViewManager: Successfully preloaded critical view: ${viewName}`);
            } else {
                console.warn(`ViewManager: Failed to preload critical view ${viewName}:`, result.reason);
            }
        });
    }

    /**
     * @brief Sets up intersection observer for lazy loading non-critical views
     * @private
     * @returns {Promise<void>} Resolves when lazy loading observer is configured
     */
    async setupLazyLoadingObserver() {
        const observerOptions = {
            root: null,
            rootMargin: this.configuration.LAZY_LOADING.rootMargin,
            threshold: this.configuration.LAZY_LOADING.threshold
        };

        this.lazyLoadingObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const viewName = entry.target.dataset.view;
                    if (viewName) {
                        this.handleViewBecameVisible(viewName, entry);
                    }
                }
            });
        }, observerOptions);

        console.debug('ViewManager: Lazy loading observer initialized.');
    }

    /**
     * @brief Sets up global error handling for view operations
     * @private
     */
    setupGlobalErrorHandling() {
        const signal = this.operationAbortController.signal;

        window.addEventListener('error', (event) => {
            this.handleGlobalError(event);
        }, { signal });

        window.addEventListener('unhandledrejection', (event) => {
            this.handleUnhandledRejection(event);
        }, { signal });
    }

    /**
     * @brief Handles global JavaScript errors
     * @private
     * @param {ErrorEvent} errorEvent - Global error event
     */
    handleGlobalError = (errorEvent) => {
        console.error('ViewManager: Global error captured:', errorEvent.error);
        this.performanceMetrics.errorCount++;
    };

    /**
     * @brief Handles unhandled promise rejections
     * @private
     * @param {PromiseRejectionEvent} rejectionEvent - Unhandled rejection event
     */
    handleUnhandledRejection = (rejectionEvent) => {
        console.error('ViewManager: Unhandled promise rejection:', rejectionEvent.reason);
        this.performanceMetrics.errorCount++;
        rejectionEvent.preventDefault();
    };

    /**
     * @brief Renders a specific view with provided data and lifecycle management
     * @public
     * @param {string} targetViewName - The name of the view to render
     * @param {Object} viewData - Data to pass to the view for rendering
     * @param {Object} options - Rendering options and configuration
     * @returns {Promise<void>} Resolves when view is successfully rendered
     * @throws {Error} When view rendering fails after retry attempts
     */
    async renderView(targetViewName, viewData = {}, options = {}) {
        const {
            enableCaching = true,
            showLoadingState = true,
            transition = true,
            retryOnFailure = true
        } = options;

        // Validate view name
        if (!this.isValidViewName(targetViewName)) {
            throw new Error(`ViewManager: Invalid view name: ${targetViewName}`);
        }

        // Skip if view is already active
        if (this.currentActiveView === targetViewName && !options.forceReload) {
            console.debug(`ViewManager: View ${targetViewName} is already active, skipping render.`);
            return;
        }

        const renderStartTime = performance.now();

        try {
            // Start view rendering process
            await this.executeViewRendering(
                targetViewName, 
                viewData, 
                { enableCaching, showLoadingState, transition }
            );

            // Track performance metrics
            const renderDuration = performance.now() - renderStartTime;
            this.trackViewRenderPerformance(targetViewName, renderDuration);

            console.info(`ViewManager: Successfully rendered view: ${targetViewName}`);

        } catch (error) {
            // Handle rendering errors with retry logic
            if (retryOnFailure) {
                return await this.handleViewRenderRetry(
                    targetViewName, 
                    viewData, 
                    error, 
                    options
                );
            }

            throw error;
        }
    }

    /**
     * @brief Executes the complete view rendering process
     * @private
     * @param {string} targetViewName - The name of the view to render
     * @param {Object} viewData - Data to pass to the view
     * @param {Object} options - Rendering options
     * @returns {Promise<void>} Resolves when rendering completes
     */
    async executeViewRendering(targetViewName, viewData, options) {
        const { enableCaching, showLoadingState, transition } = options;

        // Show loading state
        if (showLoadingState) {
            this.showViewLoadingState(targetViewName);
        }

        // Load view module
        const viewModule = await this.loadViewModule(targetViewName, { enableCaching });

        // Render view content
        const renderedContent = await this.renderViewContent(viewModule, viewData, targetViewName);

        // Update DOM with new content
        await this.updateViewContainer(renderedContent, targetViewName, { transition });

        // Initialize view-specific functionality
        await this.initializeViewModule(viewModule, viewData, targetViewName);

        // Update internal state
        this.updateViewManagerState(targetViewName);

        // Hide loading state
        if (showLoadingState) {
            this.hideViewLoadingState(targetViewName);
        }

        // Dispatch view change event
        this.dispatchViewChangeEvent(targetViewName, viewData);
    }

    /**
     * @brief Validates view name format and safety
     * @private
     * @param {string} viewName - View name to validate
     * @returns {boolean} True if view name is valid and safe
     */
    isValidViewName(viewName) {
        if (typeof viewName !== 'string' || viewName.trim() === '') {
            return false;
        }

        // Prevent directory traversal and ensure safe file names
        const safeViewNamePattern = /^[a-zA-Z0-9-_]+$/;
        return safeViewNamePattern.test(viewName);
    }

    /**
     * @brief Handles view rendering retry logic on failure
     * @private
     * @param {string} targetViewName - The view name that failed to render
     * @param {Object} viewData - View data for rendering
     * @param {Error} originalError - The original rendering error
     * @param {Object} options - Original rendering options
     * @returns {Promise<void>} Resolves when retry succeeds or fails
     */
    async handleViewRenderRetry(targetViewName, viewData, originalError, options) {
        const maxRetries = this.configuration.ERROR_HANDLING.maxRetryAttempts;
        let lastError = originalError;

        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                console.warn(`ViewManager: Retry attempt ${attempt} for view ${targetViewName}`);
                
                // Clear cache for this view to force fresh load
                this.viewModuleCache.delete(targetViewName);
                
                // Add delay between retries
                if (attempt > 1) {
                    await this.delay(this.configuration.ERROR_HANDLING.retryDelay * attempt);
                }

                await this.executeViewRendering(
                    targetViewName, 
                    viewData, 
                    { ...options, showLoadingState: false }
                );

                console.info(`ViewManager: Successfully rendered view ${targetViewName} on retry attempt ${attempt}`);
                return;

            } catch (retryError) {
                lastError = retryError;
                console.error(`ViewManager: Retry attempt ${attempt} failed for view ${targetViewName}:`, retryError);
            }
        }

        // All retries failed, render error view
        await this.renderErrorView(lastError, targetViewName);
        throw lastError;
    }

    /**
     * @brief Loads a view module with caching and error handling
     * @private
     * @param {string} viewName - The name of the view module to load
     * @param {Object} options - Loading options
     * @returns {Promise<Object>} The loaded view module
     * @throws {Error} When view module cannot be loaded
     */
    async loadViewModule(viewName, options = {}) {
        const { enableCaching = true } = options;

        // Check cache first
        if (enableCaching && this.viewModuleCache.has(viewName)) {
            const cachedModule = this.viewModuleCache.get(viewName);
            this.performanceMetrics.cacheHitRate = 
                (this.performanceMetrics.cacheHitRate * 0.9) + 0.1; // Weighted average
            return cachedModule;
        }

        try {
            const loadStartTime = performance.now();
            
            // Dynamic import with error handling
            const module = await import(`../views/${viewName}.js`);
            
            const loadDuration = performance.now() - loadStartTime;
            console.debug(`ViewManager: Loaded view module ${viewName} in ${loadDuration.toFixed(2)}ms`);

            // Cache the module if enabled
            if (enableCaching) {
                this.cacheViewModule(viewName, module);
            }

            return module;

        } catch (error) {
            console.error(`ViewManager: Failed to load view module ${viewName}:`, error);
            throw new Error(`View module '${viewName}' could not be loaded: ${error.message}`);
        }
    }

    /**
     * @brief Caches a view module with size management
     * @private
     * @param {string} viewName - The name of the view to cache
     * @param {Object} viewModule - The view module to cache
     */
    cacheViewModule(viewName, viewModule) {
        // Manage cache size
        if (this.viewModuleCache.size >= this.configuration.PERFORMANCE.cacheSize) {
            const firstKey = this.viewModuleCache.keys().next().value;
            this.viewModuleCache.delete(firstKey);
        }

        this.viewModuleCache.set(viewName, viewModule);
        
        // Dispatch caching event
        this.dispatchViewEvent(VIEW_EVENTS.VIEW_CACHED, {
            viewName,
            cacheSize: this.viewModuleCache.size,
            timestamp: Date.now()
        });
    }

    /**
     * @brief Renders view content using the view module's render method
     * @private
     * @param {Object} viewModule - The loaded view module
     * @param {Object} viewData - Data to pass to the render method
     * @param {string} viewName - The name of the view being rendered
     * @returns {Promise<string>} Rendered HTML content
     * @throws {Error} When render method fails or returns invalid content
     */
    async renderViewContent(viewModule, viewData, viewName) {
        if (typeof viewModule.render !== 'function') {
            throw new Error(`View module ${viewName} does not export a render function`);
        }

        try {
            const renderedContent = await viewModule.render(viewData);
            
            if (typeof renderedContent !== 'string') {
                throw new Error(`View ${viewName} render method did not return a string`);
            }

            return renderedContent;

        } catch (renderError) {
            console.error(`ViewManager: View ${viewName} render method failed:`, renderError);
            throw new Error(`Failed to render view ${viewName}: ${renderError.message}`);
        }
    }

    /**
     * @brief Updates the view container with new content
     * @private
     * @param {string} content - The HTML content to render
     * @param {string} viewName - The name of the view being rendered
     * @param {Object} options - Update options
     * @returns {Promise<void>} Resolves when DOM update is complete
     */
    async updateViewContainer(content, viewName, options = {}) {
        const { transition = true } = options;

        if (!this.viewContainer) {
            throw new Error('ViewManager: View container element not available');
        }

        // Prepare container for update
        this.prepareViewContainerForUpdate(viewName, transition);

        // Update content
        this.viewContainer.innerHTML = content;
        this.viewContainer.setAttribute('data-current-view', viewName);

        // Apply post-update actions
        await this.finalizeViewContainerUpdate(viewName, transition);

        console.debug(`ViewManager: Updated view container for: ${viewName}`);
    }

    /**
     * @brief Prepares view container for content update
     * @private
     * @param {string} viewName - The name of the view being rendered
     * @param {boolean} transition - Whether to apply transition effects
     */
    prepareViewContainerForUpdate(viewName, transition) {
        if (transition) {
            this.viewContainer.classList.add('view-transition--out');
        }

        // Set accessibility attributes
        this.viewContainer.setAttribute('aria-busy', 'true');
        this.viewContainer.setAttribute('data-previous-view', this.currentActiveView || 'none');
    }

    /**
     * @brief Finalizes view container after content update
     * @private
     * @param {string} viewName - The name of the view being rendered
     * @param {boolean} transition - Whether transition effects were applied
     * @returns {Promise<void>} Resolves when finalization is complete
     */
    async finalizeViewContainerUpdate(viewName, transition) {
        if (transition) {
            // Remove outgoing transition class
            this.viewContainer.classList.remove('view-transition--out');
            
            // Add incoming transition class
            this.viewContainer.classList.add('view-transition--in');
            
            // Wait for transition to complete
            await this.delay(this.configuration.PERFORMANCE.viewTransitionDuration);
            
            // Remove incoming transition class
            this.viewContainer.classList.remove('view-transition--in');
        }

        // Update accessibility attributes
        this.viewContainer.setAttribute('aria-busy', 'false');
        this.viewContainer.removeAttribute('data-previous-view');

        // Manage focus for accessibility
        this.focusViewContent();
    }

    /**
     * @brief Initializes view module functionality if available
     * @private
     * @param {Object} viewModule - The loaded view module
     * @param {Object} viewData - Data to pass to the init method
     * @param {string} viewName - The name of the view being initialized
     * @returns {Promise<void>} Resolves when initialization completes
     */
    async initializeViewModule(viewModule, viewData, viewName) {
        if (typeof viewModule.init === 'function') {
            try {
                await viewModule.init(viewData);
                console.debug(`ViewManager: Initialized view module: ${viewName}`);
            } catch (initError) {
                console.warn(`ViewManager: View ${viewName} init method failed:`, initError);
                // Don't throw error - initialization failure shouldn't break rendering
            }
        }
    }

    /**
     * @brief Manages focus for accessibility after view changes
     * @private
     */
    focusViewContent() {
        if (!this.viewContainer) return;

        // Focus the main content area for screen readers
        this.viewContainer.focus({ preventScroll: true });

        // Find and focus the main heading for better navigation
        const mainHeading = this.viewContainer.querySelector('h1, [role="heading"][aria-level="1"]');
        if (mainHeading) {
            if (!mainHeading.hasAttribute('tabindex')) {
                mainHeading.setAttribute('tabindex', '-1');
            }
            mainHeading.focus({ preventScroll: true });
        }
    }

    /**
     * @brief Shows loading state for a view
     * @private
     * @param {string} viewName - The name of the view being loaded
     */
    showViewLoadingState(viewName) {
        this.viewLoadingStates.set(viewName, {
            startTime: Date.now(),
            isLoading: true
        });

        this.viewContainer.setAttribute('aria-busy', 'true');

        // Create and append loading indicator
        const loadingIndicator = this.createLoadingIndicator(viewName);
        this.viewContainer.appendChild(loadingIndicator);

        // Dispatch loading start event
        this.dispatchViewEvent(VIEW_EVENTS.VIEW_LOADING_START, {
            viewName,
            timestamp: Date.now()
        });
    }

    /**
     * @brief Hides loading state for a view
     * @private
     * @param {string} viewName - The name of the view that finished loading
     */
    hideViewLoadingState(viewName) {
        const loadingState = this.viewLoadingStates.get(viewName);
        if (loadingState) {
            loadingState.isLoading = false;
            loadingState.endTime = Date.now();
            loadingState.duration = loadingState.endTime - loadingState.startTime;
        }

        this.viewContainer.setAttribute('aria-busy', 'false');

        // Remove loading indicator
        const loadingIndicator = this.viewContainer.querySelector('.view-loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.remove();
        }

        // Dispatch loading end event
        this.dispatchViewEvent(VIEW_EVENTS.VIEW_LOADING_END, {
            viewName,
            timestamp: Date.now(),
            duration: loadingState?.duration || 0
        });
    }

    /**
     * @brief Creates a loading indicator element
     * @private
     * @param {string} viewName - The name of the view being loaded
     * @returns {HTMLElement} The loading indicator element
     */
    createLoadingIndicator(viewName) {
        const indicator = document.createElement('div');
        indicator.className = 'view-loading-indicator';
        indicator.setAttribute('role', 'status');
        indicator.setAttribute('aria-label', `Loading ${viewName} content`);
        indicator.setAttribute('data-view', viewName);
        
        indicator.innerHTML = `
            <div class="view-loading-spinner" aria-hidden="true">
                <div class="spinner-circle"></div>
                <div class="spinner-circle"></div>
                <div class="spinner-circle"></div>
            </div>
            <span class="view-loading-text">Loading ${viewName}...</span>
            <span class="visually-hidden">Content is being loaded, please wait.</span>
        `;

        return indicator;
    }

    /**
     * @brief Updates internal view manager state after successful render
     * @private
     * @param {string} viewName - The newly active view name
     */
    updateViewManagerState(viewName) {
        const previousView = this.currentActiveView;
        this.currentActiveView = viewName;
        this.performanceMetrics.totalViewsRendered++;

        console.debug(`ViewManager: State updated - Previous: ${previousView}, Current: ${viewName}`);
    }

    /**
     * @brief Dispatches view change event for external consumers
     * @private
     * @param {string} viewName - The name of the new active view
     * @param {Object} viewData - Data associated with the view change
     */
    dispatchViewChangeEvent(viewName, viewData) {
        this.dispatchViewEvent(VIEW_EVENTS.VIEW_CHANGED, {
            viewName,
            viewData,
            previousView: this.currentActiveView,
            timestamp: Date.now(),
            totalViewsRendered: this.performanceMetrics.totalViewsRendered
        });
    }

    /**
     * @brief Dispatches a custom view-related event
     * @private
     * @param {string} eventType - Type of view event
     * @param {Object} eventDetail - Additional event data
     */
    dispatchViewEvent(eventType, eventDetail) {
        const viewEvent = new CustomEvent(eventType, {
            detail: {
                source: 'ViewManager',
                ...eventDetail
            },
            bubbles: true,
            cancelable: true
        });

        window.dispatchEvent(viewEvent);
    }

    /**
     * @brief Handles view becoming visible for lazy loading
     * @private
     * @param {string} viewName - The view name that became visible
     * @param {IntersectionObserverEntry} entry - Intersection observer entry
     */
    handleViewBecameVisible(viewName, entry) {
        console.debug(`ViewManager: View ${viewName} became visible, preloading...`);
        this.preloadViewModule(viewName);
        
        // Stop observing once loaded
        this.lazyLoadingObserver?.unobserve(entry.target);
    }

    /**
     * @brief Preloads a view module for better performance
     * @public
     * @param {string} viewName - The name of the view to preload
     * @returns {Promise<void>} Resolves when view is preloaded
     */
    async preloadViewModule(viewName) {
        if (this.viewModuleCache.has(viewName)) {
            return; // Already loaded
        }

        try {
            await this.loadViewModule(viewName, { enableCaching: true });
            
            this.dispatchViewEvent(VIEW_EVENTS.VIEW_PRELOADED, {
                viewName,
                timestamp: Date.now()
            });

            console.debug(`ViewManager: Preloaded view: ${viewName}`);

        } catch (error) {
            console.warn(`ViewManager: Failed to preload view ${viewName}:`, error);
        }
    }

    /**
     * @brief Renders error view when view loading fails
     * @private
     * @param {Error} error - The error that occurred
     * @param {string} failedViewName - The name of the view that failed
     * @returns {Promise<void>} Resolves when error view is rendered
     */
    async renderErrorView(error, failedViewName) {
        console.error(`ViewManager: Rendering error view for failed view: ${failedViewName}`, error);

        try {
            const errorViewName = this.configuration.ERROR_HANDLING.fallbackView;
            const errorViewModule = await this.loadViewModule(errorViewName, { enableCaching: true });
            
            const errorContent = await errorViewModule.render({
                error: error.message,
                errorCode: error.code || 'VIEW_RENDER_ERROR',
                failedView: failedViewName,
                timestamp: new Date().toISOString()
            });

            await this.updateViewContainer(errorContent, 'error', { transition: false });

            this.dispatchViewEvent(VIEW_EVENTS.VIEW_ERROR, {
                failedViewName,
                error: error.message,
                timestamp: Date.now()
            });

        } catch (fallbackError) {
            // Ultimate fallback - render basic error message
            console.error('ViewManager: Error view also failed, using ultimate fallback:', fallbackError);
            this.viewContainer.innerHTML = `
                <div class="view-error-fallback">
                    <h2>Application Error</h2>
                    <p>Unable to load the requested content. Please try refreshing the page.</p>
                    <p>Technical details: ${error.message}</p>
                </div>
            `;
        }
    }

    /**
     * @brief Tracks view rendering performance metrics
     * @private
     * @param {string} viewName - The name of the rendered view
     * @param {number} duration - Render duration in milliseconds
     */
    trackViewRenderPerformance(viewName, duration) {
        this.performanceMetrics.viewLoadTimes.set(viewName, duration);
        
        // Keep only recent performance data
        if (this.performanceMetrics.viewLoadTimes.size > 50) {
            const firstKey = this.performanceMetrics.viewLoadTimes.keys().next().value;
            this.performanceMetrics.viewLoadTimes.delete(firstKey);
        }
    }

    /**
     * @brief Utility function for asynchronous delays
     * @private
     * @param {number} milliseconds - Delay duration in milliseconds
     * @returns {Promise<void>} Resolves after specified delay
     */
    delay(milliseconds) {
        return new Promise(resolve => setTimeout(resolve, milliseconds));
    }

    /**
     * @brief Gets the currently active view name
     * @public
     * @returns {string|null} The currently active view name
     */
    getCurrentView() {
        return this.currentActiveView;
    }

    /**
     * @brief Checks if a view is currently loading
     * @public
     * @param {string} viewName - The view name to check
     * @returns {boolean} True if the view is currently loading
     */
    isViewLoading(viewName) {
        const loadingState = this.viewLoadingStates.get(viewName);
        return loadingState ? loadingState.isLoading : false;
    }

    /**
     * @brief Gets performance metrics and statistics
     * @public
     * @returns {Object} Performance metrics object
     */
    getPerformanceMetrics() {
        return {
            ...this.performanceMetrics,
            cacheSize: this.viewModuleCache.size,
            loadingStates: Array.from(this.viewLoadingStates.entries()),
            currentView: this.currentActiveView
        };
    }

    /**
     * @brief Clears view module cache
     * @public
     * @returns {number} Number of items cleared from cache
     */
    clearCache() {
        const cacheSize = this.viewModuleCache.size;
        this.viewModuleCache.clear();
        console.info(`ViewManager: Cleared ${cacheSize} items from view cache.`);
        return cacheSize;
    }

    /**
     * @brief Cleans up resources when ViewManager is destroyed
     * @public
     */
    destroy() {
        // Abort all ongoing operations
        this.operationAbortController.abort();

        // Disconnect intersection observer
        if (this.lazyLoadingObserver) {
            this.lazyLoadingObserver.disconnect();
            this.lazyLoadingObserver = null;
        }

        // Clear all collections
        this.viewModuleCache.clear();
        this.viewLoadingStates.clear();

        // Reset state
        this.currentActiveView = null;

        console.info('ViewManager: View manager destroyed and resources cleaned up.');
    }
}

export default ViewManager;