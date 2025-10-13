/**
 * @file ErrorReporter.js
 * @brief Comprehensive error tracking and reporting system
 * @description Captures, processes, and reports application errors with context
 */

class ErrorReporter {
    /**
     * @brief Creates a new ErrorReporter instance
     * @constructor
     * @param {Object} configuration - Error reporting configuration
     */
    constructor(configuration = {}) {
        /**
         * @private
         * @type {string}
         * @description Endpoint for error reporting
         */
        this.endpoint = configuration.endpoint || '/api/errors';

        /**
         * @private
         * @type {Array<Object>}
         * @description Error queue for batch processing
         */
        this.errorQueue = [];

        /**
         * @private
         * @type {boolean}
         * @description Tracks initialization status
         */
        this.isInitialized = false;

        /**
         * @private
         * @type {number}
         * @description Maximum queue size before flushing
         */
        this.maxQueueSize = configuration.maxQueueSize || 10;

        /**
         * @private
         * @type {Object}
         * @description Application context for error reporting
         */
        this.applicationContext = {
            version: configuration.version || '1.0.0',
            environment: configuration.environment || 'development',
            userAgent: navigator.userAgent,
            url: window.location.href,
            ...configuration.context
        };

        this.initialize = this.initialize.bind(this);
        this.captureError = this.captureError.bind(this);
    }

    /**
     * @brief Initializes error reporter and sets up global handlers
     * @method initialize
     * @returns {Promise<void>}
     */
    async initialize() {
        try {
            // Set up global error handlers
            this.setupGlobalErrorHandlers();
            
            // Set up unhandled promise rejection handler
            this.setupPromiseRejectionHandler();
            
            // Set up periodic queue flushing
            this.setupQueueFlushing();
            
            this.isInitialized = true;
            console.info('ErrorReporter initialized successfully');
        } catch (error) {
            console.error('ErrorReporter initialization failed:', error);
        }
    }

    /**
     * @brief Sets up global error event handlers
     * @method setupGlobalErrorHandlers
     * @private
     */
    setupGlobalErrorHandlers() {
        // Handle synchronous errors
        window.addEventListener('error', (event) => {
            const errorData = {
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error,
                type: 'synchronous_error',
                timestamp: Date.now()
            };
            
            this.captureError(errorData);
        });

        // Handle console errors
        this.interceptConsoleErrors();
    }

    /**
     * @brief Sets up unhandled promise rejection handler
     * @method setupPromiseRejectionHandler
     * @private
     */
    setupPromiseRejectionHandler() {
        window.addEventListener('unhandledrejection', (event) => {
            const errorData = {
                message: event.reason?.message || 'Unhandled promise rejection',
                stack: event.reason?.stack,
                type: 'unhandled_rejection',
                reason: event.reason,
                timestamp: Date.now()
            };
            
            this.captureError(errorData);
            
            // Prevent browser default handling
            event.preventDefault();
        });
    }

    /**
     * @brief Intercepts console errors for reporting
     * @method interceptConsoleErrors
     * @private
     */
    interceptConsoleErrors() {
        const originalConsoleError = console.error;
        
        console.error = (...args) => {
            const errorData = {
                message: args.map(arg => 
                    typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
                ).join(' '),
                type: 'console_error',
                timestamp: Date.now(),
                stack: new Error().stack
            };
            
            this.captureError(errorData);
            
            // Call original console.error
            originalConsoleError.apply(console, args);
        };
    }

    /**
     * @brief Sets up periodic error queue flushing
     * @method setupQueueFlushing
     * @private
     */
    setupQueueFlushing() {
        // Flush queue every 30 seconds
        setInterval(() => {
            if (this.errorQueue.length > 0) {
                this.flushErrorQueue();
            }
        }, 30000);
    }

    /**
     * @brief Captures error with context and adds to queue
     * @method captureError
     * @param {Error|Object|string} error - Error object, plain object, or string message
     * @param {Object} additionalContext - Additional context for the error
     * @returns {void}
     */
    captureError(error, additionalContext = {}) {
        try {
            const normalizedError = this.normalizeError(error);
            const enrichedError = this.enrichErrorWithContext(normalizedError, additionalContext);
            
            this.errorQueue.push(enrichedError);
            
            // Flush queue if maximum size reached
            if (this.errorQueue.length >= this.maxQueueSize) {
                this.flushErrorQueue();
            }
            
            // Dispatch error event for application handling
            this.dispatchErrorEvent(enrichedError);
            
        } catch (reportingError) {
            console.warn('Error reporting failed:', reportingError);
        }
    }

    /**
     * @brief Normalizes different error types to consistent format
     * @method normalizeError
     * @param {Error|Object|string} error - Error to normalize
     * @returns {Object} Normalized error object
     * @private
     */
    normalizeError(error) {
        if (typeof error === 'string') {
            return {
                message: error,
                stack: new Error(error).stack,
                type: 'custom_error'
            };
        }
        
        if (error instanceof Error) {
            return {
                message: error.message,
                stack: error.stack,
                name: error.name,
                type: 'error_instance'
            };
        }
        
        if (typeof error === 'object' && error !== null) {
            return {
                ...error,
                type: error.type || 'object_error'
            };
        }
        
        return {
            message: 'Unknown error type',
            originalError: error,
            type: 'unknown_error'
        };
    }

    /**
     * @brief Enriches error with application and environmental context
     * @method enrichErrorWithContext
     * @param {Object} error - Normalized error object
     * @param {Object} additionalContext - Additional context data
     * @returns {Object} Enriched error object
     * @private
     */
    enrichErrorWithContext(error, additionalContext) {
        // Gather performance metrics if available
        const performanceMetrics = this.gatherPerformanceContext();
        
        // Gather user context
        const userContext = this.gatherUserContext();
        
        return {
            ...error,
            context: {
                // Application context
                application: this.applicationContext,
                
                // Environmental context
                environment: {
                    url: window.location.href,
                    referrer: document.referrer,
                    viewport: {
                        width: window.innerWidth,
                        height: window.innerHeight
                    },
                    online: navigator.onLine,
                    language: navigator.language
                },
                
                // Performance context
                performance: performanceMetrics,
                
                // User context (anonymized)
                user: userContext,
                
                // Additional context provided by caller
                custom: additionalContext
            },
            
            // Metadata
            timestamp: Date.now(),
            id: this.generateErrorId(),
            version: '1.0'
        };
    }

    /**
     * @brief Gathers performance context for error reporting
     * @method gatherPerformanceContext
     * @returns {Object} Performance context data
     * @private
     */
    gatherPerformanceContext() {
        const metrics = {};
        
        if (performance.memory) {
            metrics.memory = {
                used: performance.memory.usedJSHeapSize,
                total: performance.memory.totalJSHeapSize,
                limit: performance.memory.jsHeapSizeLimit
            };
        }
        
        if (performance.timing) {
            metrics.timing = {
                loadTime: performance.timing.loadEventEnd - performance.timing.navigationStart
            };
        }
        
        metrics.domNodes = document.getElementsByTagName('*').length;
        metrics.eventListeners = this.estimateEventListenerCount();
        
        return metrics;
    }

    /**
     * @brief Gathers anonymized user context
     * @method gatherUserContext
     * @returns {Object} User context data
     * @private
     */
    gatherUserContext() {
        return {
            // Anonymized user identifier (hash of user agent + some random data)
            anonymousId: this.generateAnonymousId(),
            // User agent without personal information
            userAgent: navigator.userAgent,
            // Platform information
            platform: navigator.platform,
            // Cookie enabled
            cookiesEnabled: navigator.cookieEnabled,
            // Do not track setting
            doNotTrack: navigator.doNotTrack
        };
    }

    /**
     * @brief Estimates total event listener count
     * @method estimateEventListenerCount
     * @returns {number} Estimated event listener count
     * @private
     */
    estimateEventListenerCount() {
        // This is an approximation since we can't directly access the actual count
        return Math.floor(document.getElementsByTagName('*').length * 1.5);
    }

    /**
     * @brief Generates unique error identifier
     * @method generateErrorId
     * @returns {string} Unique error ID
     * @private
     */
    generateErrorId() {
        return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * @brief Generates anonymous user identifier
     * @method generateAnonymousId
     * @returns {string} Anonymous user ID
     * @private
     */
    generateAnonymousId() {
        const data = navigator.userAgent + navigator.language + navigator.platform;
        let hash = 0;
        
        for (let i = 0; i < data.length; i++) {
            const char = data.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        
        return Math.abs(hash).toString(36);
    }

    /**
     * @brief Flushes error queue to reporting endpoint
     * @method flushErrorQueue
     * @returns {Promise<void>}
     * @private
     */
    async flushErrorQueue() {
        if (this.errorQueue.length === 0) return;

        const errorsToSend = [...this.errorQueue];
        this.errorQueue = [];

        try {
            const response = await fetch(this.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    errors: errorsToSend,
                    batchSize: errorsToSend.length,
                    sentAt: new Date().toISOString()
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            console.info(`Successfully reported ${errorsToSend.length} errors`);
        } catch (error) {
            console.warn('Error reporting failed, re-queuing errors:', error);
            // Re-queue failed errors (with limits to prevent infinite growth)
            this.errorQueue = [...errorsToSend, ...this.errorQueue].slice(0, this.maxQueueSize * 2);
        }
    }

    /**
     * @brief Dispatches error event for application handling
     * @method dispatchErrorEvent
     * @param {Object} errorData - Enriched error data
     * @private
     */
    dispatchErrorEvent(errorData) {
        const errorEvent = new CustomEvent('error:reported', {
            detail: {
                error: errorData,
                severity: this.determineErrorSeverity(errorData),
                timestamp: Date.now()
            },
            bubbles: true
        });
        
        window.dispatchEvent(errorEvent);
    }

    /**
     * @brief Determines error severity based on error type and context
     * @method determineErrorSeverity
     * @param {Object} errorData - Error data
     * @returns {string} Error severity level
     * @private
     */
    determineErrorSeverity(errorData) {
        if (errorData.type === 'unhandled_rejection') return 'high';
        if (errorData.message?.includes('Script error')) return 'low'; // Cross-origin errors
        if (errorData.context?.performance?.memory?.used > 100000000) return 'medium'; // High memory usage
        
        return 'medium';
    }

    /**
     * @brief Manually flushes error queue (useful before page unload)
     * @method flush
     * @returns {Promise<void>}
     */
    async flush() {
        await this.flushErrorQueue();
    }

    /**
     * @brief Sets application context for error reporting
     * @method setApplicationContext
     * @param {Object} context - Application context data
     * @returns {void}
     */
    setApplicationContext(context) {
        this.applicationContext = { ...this.applicationContext, ...context };
    }

    /**
     * @brief Gets current error queue size
     * @method getQueueSize
     * @returns {number} Current error queue size
     */
    getQueueSize() {
        return this.errorQueue.length;
    }

    /**
     * @brief Cleans up error reporter resources
     * @method destroy
     * @returns {Promise<void>}
     */
    async destroy() {
        // Flush any remaining errors before destruction
        await this.flush();
        
        this.errorQueue = [];
        this.isInitialized = false;
        
        console.info('ErrorReporter destroyed successfully');
    }
}

export default ErrorReporter;