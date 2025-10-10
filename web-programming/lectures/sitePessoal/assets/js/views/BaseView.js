/**
 * @file BaseView.js
 * @author Rafael Passos Domingues
 * @version 3.0.0
 * @brief Abstract base class for all view components in the application.
 * @description Provides generic structure for template rendering, event management,
 * observer pattern implementation, and lifecycle management with performance optimizations
 * and comprehensive error handling.
 */

/**
 * @constant {Object} TEMPLATE_CONFIGURATION
 * @brief Configuration constants for template rendering and interpolation
 * @description Defines template syntax, rendering options, and interpolation patterns
 */
const TEMPLATE_CONFIGURATION = {
    INTERPOLATION_PATTERN: /\{\{([\w\.]+)\}\}/g,
    NESTED_PROPERTY_DELIMITER: '.',
    EMPTY_VALUE_REPLACEMENT: '',
    SANITIZATION_ENABLED: true,
    MAX_TEMPLATE_LENGTH: 1000000 // 1MB limit for safety
};

/**
 * @constant {Object} EVENT_CONFIGURATION
 * @brief Configuration constants for event management system
 * @description Defines event options, validation rules, and performance settings
 */
const EVENT_CONFIGURATION = {
    DEFAULT_EVENT_OPTIONS: { passive: true },
    MAX_EVENT_LISTENERS: 100,
    EVENT_TYPES: {
        DOM: ['click', 'input', 'submit', 'change', 'focus', 'blur', 'keydown', 'keyup'],
        CUSTOM: ['view:rendered', 'view:destroyed', 'view:error', 'data:updated']
    }
};

/**
 * @constant {Object} ERROR_MESSAGES
 * @brief Standardized error messages for view operations
 * @description Provides consistent error messages for validation and error handling
 */
const ERROR_MESSAGES = {
    INVALID_ELEMENT: 'BaseView requires a valid HTMLElement instance as container.',
    INVALID_OBSERVER: 'Observer must be a valid function.',
    INVALID_EVENT_HANDLER: 'Event handler must be a valid function.',
    INVALID_TEMPLATE: 'Template must be a non-empty string.',
    TEMPLATE_TOO_LARGE: 'Template exceeds maximum allowed size.'
};

/**
 * @class BaseView
 * @brief Abstract base class for all view components with comprehensive lifecycle management
 * @description Provides template rendering, event management, observer pattern implementation,
 * and lifecycle management with performance optimizations and error handling
 */
class BaseView {
    /**
     * @brief Creates a new BaseView instance
     * @constructor
     * @param {HTMLElement} containerElement - DOM element that serves as the view container
     * @param {string} template - HTML template string with {{key}} placeholders for interpolation
     * @param {Object} options - Configuration options for the view instance
     * @param {boolean} options.autoRender - Whether to auto-render on construction
     * @param {boolean} options.enableSanitization - Whether to enable HTML sanitization
     * @throws {TypeError} When containerElement is not a valid HTMLElement
     */
    constructor(containerElement, template = '', options = {}) {
        this.validateConstructorParameters(containerElement, template);

        const {
            autoRender = false,
            enableSanitization = TEMPLATE_CONFIGURATION.SANITIZATION_ENABLED
        } = options;

        /**
         * @protected
         * @type {HTMLElement}
         * @brief DOM container element for the view content
         */
        this.containerElement = containerElement;

        /**
         * @protected
         * @type {string}
         * @brief HTML template structure with interpolation placeholders
         */
        this.template = template;

        /**
         * @protected
         * @type {Object}
         * @brief Configuration options for view behavior
         */
        this.viewConfiguration = {
            autoRender,
            enableSanitization,
            maxEventListeners: EVENT_CONFIGURATION.MAX_EVENT_LISTENERS
        };

        /**
         * @private
         * @type {Function[]}
         * @brief Collection of observer callback functions for state changes
         */
        this.observerCallbacks = [];

        /**
         * @private
         * @type {Array}
         * @brief Registered DOM event listeners for proper cleanup
         */
        this.registeredEventListeners = [];

        /**
         * @private
         * @type {AbortController}
         * @brief Manages cleanup of event listeners and async operations
         */
        this.eventAbortController = new AbortController();

        /**
         * @private
         * @type {boolean}
         * @brief Tracks whether the view has been destroyed
         */
        this.isDestroyed = false;

        /**
         * @private
         * @type {Object}
         * @brief Performance metrics for view operations
         */
        this.performanceMetrics = {
            renderCount: 0,
            lastRenderTime: 0,
            eventListenerCount: 0
        };

        // Initialize view if auto-render is enabled
        if (autoRender && template) {
            this.render().catch(console.error);
        }

        console.debug('BaseView: View instance created with container:', containerElement);
    }

    /**
     * @brief Validates constructor parameters for safety and correctness
     * @private
     * @param {HTMLElement} containerElement - Container element to validate
     * @param {string} template - Template string to validate
     * @throws {TypeError} When parameters are invalid
     */
    validateConstructorParameters(containerElement, template) {
        if (!containerElement || !(containerElement instanceof HTMLElement)) {
            throw new TypeError(ERROR_MESSAGES.INVALID_ELEMENT);
        }

        if (template && typeof template !== 'string') {
            throw new TypeError(ERROR_MESSAGES.INVALID_TEMPLATE);
        }

        if (template && template.length > TEMPLATE_CONFIGURATION.MAX_TEMPLATE_LENGTH) {
            throw new Error(ERROR_MESSAGES.TEMPLATE_TOO_LARGE);
        }
    }

    /**
     * @brief Renders the template into the container with data interpolation
     * @public
     * @param {Object} renderData - Data object for template interpolation
     * @param {Object} options - Rendering options
     * @param {boolean} options.forceRerender - Whether to force re-render if data unchanged
     * @returns {Promise<void>} Resolves when rendering is complete
     */
    async render(renderData = {}, options = {}) {
        if (this.isDestroyed) {
            console.warn('BaseView: Cannot render destroyed view.');
            return;
        }

        const { forceRerender = false } = options;

        try {
            const renderStartTime = performance.now();

            // Validate container availability
            if (!this.containerElement || !this.containerElement.isConnected) {
                throw new Error('BaseView: Container element is not available or disconnected from DOM.');
            }

            // Validate template availability
            if (!this.template) {
                console.warn('BaseView: No template defined for rendering.');
                return;
            }

            // Compile template with data interpolation
            const compiledTemplate = this.compileTemplate(renderData);

            // Update DOM with compiled template
            await this.updateContainerContent(compiledTemplate);

            // Update performance metrics
            this.updateRenderMetrics(renderStartTime);

            // Notify observers of successful render
            this.notifyObservers('view:rendered', {
                renderData,
                renderDuration: performance.now() - renderStartTime,
                containerId: this.containerElement.id || 'unknown'
            });

            console.debug(`BaseView: Successfully rendered view in ${performance.now() - renderStartTime}ms`);

        } catch (error) {
            console.error('BaseView: Render operation failed:', error);
            
            // Notify observers of render error
            this.notifyObservers('view:error', {
                error: error.message,
                operation: 'render',
                renderData
            });

            throw error;
        }
    }

    /**
     * @brief Compiles template by interpolating data values into placeholders
     * @protected
     * @param {Object} interpolationData - Data object for template interpolation
     * @returns {string} Compiled HTML template with interpolated values
     */
    compileTemplate(interpolationData = {}) {
        if (!this.template) {
            return '';
        }

        const compiledTemplate = this.template.replace(
            TEMPLATE_CONFIGURATION.INTERPOLATION_PATTERN,
            (match, propertyPath) => {
                try {
                    const propertyValue = this.getNestedPropertyValue(interpolationData, propertyPath);
                    return this.sanitizeTemplateValue(propertyValue);
                } catch (error) {
                    console.warn(`BaseView: Error interpolating property ${propertyPath}:`, error);
                    return TEMPLATE_CONFIGURATION.EMPTY_VALUE_REPLACEMENT;
                }
            }
        );

        return compiledTemplate;
    }

    /**
     * @brief Retrieves nested property values from data object using dot notation
     * @protected
     * @param {Object} dataObject - Source data object
     * @param {string} propertyPath - Dot-notated path to the property
     * @returns {*} Property value or undefined if not found
     */
    getNestedPropertyValue(dataObject, propertyPath) {
        if (!dataObject || typeof dataObject !== 'object') {
            return undefined;
        }

        return propertyPath
            .split(TEMPLATE_CONFIGURATION.NESTED_PROPERTY_DELIMITER)
            .reduce((currentObject, propertyName) => {
                if (currentObject && typeof currentObject === 'object' && propertyName in currentObject) {
                    return currentObject[propertyName];
                }
                return undefined;
            }, dataObject);
    }

    /**
     * @brief Sanitizes template values to prevent XSS and ensure safe rendering
     * @protected
     * @param {*} rawValue - Raw value to be sanitized
     * @returns {string} Sanitized string value safe for HTML rendering
     */
    sanitizeTemplateValue(rawValue) {
        if (rawValue === undefined || rawValue === null) {
            return TEMPLATE_CONFIGURATION.EMPTY_VALUE_REPLACEMENT;
        }

        // Convert to string
        const stringValue = String(rawValue);

        // Apply sanitization if enabled
        if (this.viewConfiguration.enableSanitization) {
            return this.escapeHtml(stringValue);
        }

        return stringValue;
    }

    /**
     * @brief Escapes HTML special characters to prevent XSS attacks
     * @protected
     * @param {string} unsafeText - Unsafe text containing HTML special characters
     * @returns {string} HTML-escaped text safe for rendering
     */
    escapeHtml(unsafeText) {
        const escapeMap = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };

        return unsafeText.replace(/[&<>"']/g, character => escapeMap[character] || character);
    }

    /**
     * @brief Updates container element with compiled template content
     * @protected
     * @param {string} compiledContent - Compiled HTML content to render
     * @returns {Promise<void>} Resolves when DOM update is complete
     */
    async updateContainerContent(compiledContent) {
        if (!this.containerElement) {
            throw new Error('BaseView: Container element not available for content update.');
        }

        // Use requestAnimationFrame for smooth DOM updates
        await new Promise(resolve => {
            requestAnimationFrame(() => {
                this.containerElement.innerHTML = compiledContent;
                resolve();
            });
        });
    }

    /**
     * @brief Updates render performance metrics
     * @private
     * @param {number} renderStartTime - Performance timestamp when render started
     */
    updateRenderMetrics(renderStartTime) {
        this.performanceMetrics.renderCount++;
        this.performanceMetrics.lastRenderTime = performance.now() - renderStartTime;
    }

    /**
     * @brief Registers an observer callback for view state changes
     * @public
     * @param {Function} observerCallback - Callback function to receive notifications
     * @param {Object} options - Observer registration options
     * @param {AbortSignal} options.signal - Abort signal for automatic observer removal
     * @throws {TypeError} When observerCallback is not a valid function
     */
    addObserver(observerCallback, options = {}) {
        if (typeof observerCallback !== 'function') {
            throw new TypeError(ERROR_MESSAGES.INVALID_OBSERVER);
        }

        // Check listener limit
        if (this.observerCallbacks.length >= this.viewConfiguration.maxEventListeners) {
            console.warn('BaseView: Maximum observer limit reached, removing oldest observer.');
            this.observerCallbacks.shift();
        }

        this.observerCallbacks.push(observerCallback);

        // Set up automatic removal when signal is aborted
        if (options.signal) {
            options.signal.addEventListener('abort', () => {
                this.removeObserver(observerCallback);
            });
        }

        console.debug('BaseView: Observer added successfully.');
    }

    /**
     * @brief Removes a specific observer callback
     * @public
     * @param {Function} observerCallback - Observer callback function to remove
     */
    removeObserver(observerCallback) {
        const observerIndex = this.observerCallbacks.indexOf(observerCallback);
        if (observerIndex > -1) {
            this.observerCallbacks.splice(observerIndex, 1);
            console.debug('BaseView: Observer removed successfully.');
        }
    }

    /**
     * @brief Notifies all registered observers of view events
     * @protected
     * @param {string} eventType - Type of event that occurred
     * @param {Object} eventData - Additional data associated with the event
     */
    notifyObservers(eventType, eventData = {}) {
        if (this.observerCallbacks.length === 0) {
            return;
        }

        const notificationPayload = {
            eventType,
            source: this.constructor.name,
            timestamp: Date.now(),
            ...eventData
        };

        this.observerCallbacks.forEach((observerCallback, index) => {
            try {
                observerCallback(eventType, notificationPayload);
            } catch (error) {
                console.error(`BaseView: Observer at index ${index} failed:`, error);
            }
        });
    }

    /**
     * @brief Adds event listener to elements within the view container
     * @public
     * @param {string} eventType - Type of DOM event to listen for
     * @param {string} elementSelector - CSS selector for target elements
     * @param {Function} eventHandler - Callback function to execute on event
     * @param {Object} options - Event listener options
     * @param {boolean} options.once - Whether listener should only fire once
     * @param {boolean} options.passive - Whether listener is passive
     * @param {AbortSignal} options.signal - Abort signal for automatic removal
     * @throws {TypeError} When parameters are invalid
     */
    addEventListener(eventType, elementSelector, eventHandler, options = {}) {
        this.validateEventListenerParameters(eventType, elementSelector, eventHandler);

        if (this.isDestroyed) {
            console.warn('BaseView: Cannot add event listener to destroyed view.');
            return;
        }

        const {
            once = false,
            passive = true,
            signal = this.eventAbortController.signal
        } = options;

        const targetElements = this.containerElement.querySelectorAll(elementSelector);

        if (targetElements.length === 0) {
            console.warn(`BaseView: No elements found for selector: ${elementSelector}`);
            return;
        }

        targetElements.forEach(element => {
            const wrappedHandler = this.createWrappedEventHandler(eventHandler, element, eventType);

            const eventListenerOptions = {
                once,
                passive,
                signal
            };

            element.addEventListener(eventType, wrappedHandler, eventListenerOptions);

            this.registeredEventListeners.push({
                element,
                eventType,
                handler: wrappedHandler,
                originalHandler: eventHandler,
                selector: elementSelector
            });

            this.performanceMetrics.eventListenerCount++;
        });

        console.debug(`BaseView: Added ${targetElements.length} event listeners for ${eventType} on ${elementSelector}`);
    }

    /**
     * @brief Validates event listener parameters for safety
     * @private
     * @param {string} eventType - Event type to validate
     * @param {string} elementSelector - CSS selector to validate
     * @param {Function} eventHandler - Event handler function to validate
     * @throws {TypeError} When parameters are invalid
     */
    validateEventListenerParameters(eventType, elementSelector, eventHandler) {
        if (typeof eventType !== 'string' || eventType.trim() === '') {
            throw new TypeError('Event type must be a non-empty string.');
        }

        if (typeof elementSelector !== 'string' || elementSelector.trim() === '') {
            throw new TypeError('Element selector must be a non-empty string.');
        }

        if (typeof eventHandler !== 'function') {
            throw new TypeError(ERROR_MESSAGES.INVALID_EVENT_HANDLER);
        }
    }

    /**
     * @brief Creates a wrapped event handler with error handling and context
     * @private
     * @param {Function} originalHandler - Original event handler function
     * @param {HTMLElement} targetElement - Element that triggered the event
     * @param {string} eventType - Type of event being handled
     * @returns {Function} Wrapped event handler with enhanced functionality
     */
    createWrappedEventHandler(originalHandler, targetElement, eventType) {
        return (event) => {
            try {
                // Create enhanced event context
                const eventContext = {
                    event,
                    targetElement,
                    view: this,
                    stopPropagation: () => event.stopPropagation(),
                    preventDefault: () => event.preventDefault()
                };

                // Execute original handler with context
                const result = originalHandler.call(this, event, eventContext);

                // Handle async handlers
                if (result instanceof Promise) {
                    result.catch(error => {
                        console.error(`BaseView: Async event handler failed for ${eventType}:`, error);
                        this.notifyObservers('view:error', {
                            error: error.message,
                            operation: 'event-handler',
                            eventType,
                            targetElement: targetElement.tagName
                        });
                    });
                }

            } catch (error) {
                console.error(`BaseView: Event handler failed for ${eventType}:`, error);
                this.notifyObservers('view:error', {
                    error: error.message,
                    operation: 'event-handler',
                    eventType,
                    targetElement: targetElement.tagName
                });
            }
        };
    }

    /**
     * @brief Removes specific event listeners based on criteria
     * @public
     * @param {string} eventType - Type of event to remove (optional)
     * @param {string} elementSelector - CSS selector for elements (optional)
     * @param {Function} eventHandler - Specific handler function to remove (optional)
     * @returns {number} Number of event listeners removed
     */
    removeEventListeners(eventType = null, elementSelector = null, eventHandler = null) {
        const listenersToRemove = this.registeredEventListeners.filter(listener => {
            const matchesType = !eventType || listener.eventType === eventType;
            const matchesSelector = !elementSelector || listener.selector === elementSelector;
            const matchesHandler = !eventHandler || listener.originalHandler === eventHandler;

            return matchesType && matchesSelector && matchesHandler;
        });

        listenersToRemove.forEach(listener => {
            listener.element.removeEventListener(listener.eventType, listener.handler);
            
            const listenerIndex = this.registeredEventListeners.indexOf(listener);
            if (listenerIndex > -1) {
                this.registeredEventListeners.splice(listenerIndex, 1);
                this.performanceMetrics.eventListenerCount--;
            }
        });

        console.debug(`BaseView: Removed ${listenersToRemove.length} event listeners.`);
        return listenersToRemove.length;
    }

    /**
     * @brief Removes all event listeners registered by this view
     * @public
     * @returns {number} Number of event listeners removed
     */
    removeAllEventListeners() {
        const removedCount = this.removeEventListeners();
        console.info(`BaseView: Removed all ${removedCount} event listeners.`);
        return removedCount;
    }

    /**
     * @brief Updates the view template
     * @public
     * @param {string} newTemplate - New template string to set
     * @param {boolean} autoRender - Whether to automatically re-render with new template
     * @returns {Promise<void>} Resolves when template is updated (and rendered if requested)
     */
    async updateTemplate(newTemplate, autoRender = false) {
        if (this.isDestroyed) {
            console.warn('BaseView: Cannot update template of destroyed view.');
            return;
        }

        if (typeof newTemplate !== 'string') {
            throw new TypeError(ERROR_MESSAGES.INVALID_TEMPLATE);
        }

        if (newTemplate.length > TEMPLATE_CONFIGURATION.MAX_TEMPLATE_LENGTH) {
            throw new Error(ERROR_MESSAGES.TEMPLATE_TOO_LARGE);
        }

        this.template = newTemplate;

        if (autoRender) {
            await this.render();
        }

        console.debug('BaseView: Template updated successfully.');
    }

    /**
     * @brief Gets the current view configuration
     * @public
     * @returns {Object} Current view configuration object
     */
    getConfiguration() {
        return { ...this.viewConfiguration };
    }

    /**
     * @brief Updates view configuration options
     * @public
     * @param {Object} newConfiguration - New configuration options to merge
     */
    updateConfiguration(newConfiguration) {
        this.viewConfiguration = {
            ...this.viewConfiguration,
            ...newConfiguration
        };
        console.debug('BaseView: Configuration updated:', this.viewConfiguration);
    }

    /**
     * @brief Gets performance metrics for the view
     * @public
     * @returns {Object} Performance metrics object
     */
    getPerformanceMetrics() {
        return {
            ...this.performanceMetrics,
            observerCount: this.observerCallbacks.length,
            isDestroyed: this.isDestroyed
        };
    }

    /**
     * @brief Checks if the view has been destroyed
     * @public
     * @returns {boolean} True if the view has been destroyed
     */
    isViewDestroyed() {
        return this.isDestroyed;
    }

    /**
     * @brief Destroys the view and cleans up all resources
     * @public
     * @description Properly cleans up event listeners, observers, and references to prevent memory leaks
     */
    destroy() {
        if (this.isDestroyed) {
            return;
        }

        console.info('BaseView: Destroying view and cleaning up resources...');

        // Abort all event listeners
        this.eventAbortController.abort();

        // Remove all DOM event listeners
        this.removeAllEventListeners();

        // Clear observer callbacks
        this.observerCallbacks = [];

        // Clear container content
        if (this.containerElement) {
            this.containerElement.innerHTML = '';
        }

        // Clear template
        this.template = '';

        // Mark as destroyed
        this.isDestroyed = true;

        // Notify observers of destruction
        this.notifyObservers('view:destroyed', {
            containerId: this.containerElement?.id || 'unknown',
            finalRenderCount: this.performanceMetrics.renderCount
        });

        console.info('BaseView: View destroyed successfully.');
    }
}

export default BaseView;