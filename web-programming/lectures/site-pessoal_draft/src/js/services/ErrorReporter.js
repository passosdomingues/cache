import eventBus from '../core/EventBus.js';

/**
 * @brief Error reporting and handling service
 * @description Captures, processes, and reports application errors
 */
export class ErrorReporter {
    constructor(dependencies = {}) {
        this.eventBus = dependencies.eventBus || eventBus;
        this.errors = [];
        this.isInitialized = false;
        
        this.handleError = this.handleError.bind(this);
        this.handleUnhandledRejection = this.handleUnhandledRejection.bind(this);
    }

    /**
     * @brief Initialize error reporter
     * @description Sets up global error handlers and event listeners
     */
    async init() {
        if (this.isInitialized) return;

        try {
            this.setupGlobalHandlers();
            this.setupEventListeners();
            
            this.isInitialized = true;
            console.info('ErrorReporter: Initialized successfully');
            
        } catch (error) {
            console.error('ErrorReporter: Initialization failed', error);
        }
    }

    /**
     * @brief Set up global error handlers
     */
    setupGlobalHandlers() {
        // Global error handler
        window.addEventListener('error', this.handleError);
        
        // Unhandled promise rejection handler
        window.addEventListener('unhandledrejection', this.handleUnhandledRejection);
        
        // Console error interceptor (optional)
        this.interceptConsoleErrors();
    }

    /**
     * @brief Set up event listeners for custom errors
     */
    setupEventListeners() {
        this.eventBus.subscribe('app:error', this.onAppError.bind(this));
        this.eventBus.subscribe('render:error', this.onRenderError.bind(this));
        this.eventBus.subscribe('section:error', this.onSectionError.bind(this));
    }

    /**
     * @brief Handle global errors
     * @param {ErrorEvent} event - Error event
     */
    handleError(event) {
        const errorData = {
            type: 'global.error',
            message: event.message,
            filename: event.filename,
            lineno: event.lineno,
            colno: event.colno,
            error: event.error,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href
        };
        
        this.captureError(errorData);
        event.preventDefault(); // Prevent browser's default error handling
    }

    /**
     * @brief Handle unhandled promise rejections
     * @param {PromiseRejectionEvent} event - Promise rejection event
     */
    handleUnhandledRejection(event) {
        const errorData = {
            type: 'unhandled.rejection',
            reason: event.reason,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href
        };
        
        this.captureError(errorData);
        event.preventDefault(); // Prevent browser's default handling
    }

    /**
     * @brief Handle application errors
     * @param {Object} data - Error data
     */
    onAppError(data) {
        const errorData = {
            type: 'app.error',
            error: data.error || data,
            context: data.context,
            timestamp: new Date().toISOString(),
            url: window.location.href
        };
        
        this.captureError(errorData);
    }

    /**
     * @brief Handle render errors
     * @param {Object} data - Error data
     */
    onRenderError(data) {
        const errorData = {
            type: 'render.error',
            sectionId: data.sectionId,
            error: data.error,
            timestamp: new Date().toISOString(),
            url: window.location.href
        };
        
        this.captureError(errorData);
    }

    /**
     * @brief Handle section errors
     * @param {Object} data - Error data
     */
    onSectionError(data) {
        const errorData = {
            type: 'section.error',
            sectionId: data.sectionId,
            error: data.error,
            timestamp: new Date().toISOString(),
            url: window.location.href
        };
        
        this.captureError(errorData);
    }

    /**
     * @brief Capture and process error
     * @param {Object} errorData - Error data object
     */
    captureError(errorData) {
        // Add stack trace if available
        if (errorData.error && errorData.error.stack) {
            errorData.stack = errorData.error.stack;
        }
        
        // Add unique error ID
        errorData.id = this.generateErrorId();
        
        // Store error
        this.errors.push(errorData);
        
        // Limit errors storage
        if (this.errors.length > 100) {
            this.errors = this.errors.slice(-50);
        }
        
        // Notify subscribers
        this.eventBus.publish('error:captured', errorData);
        
        // Show user-friendly error message if needed
        this.handleUserNotification(errorData);
        
        console.error('ErrorReporter: Captured error', errorData);
    }

    /**
     * @brief Generate unique error ID
     * @returns {string} Unique error identifier
     */
    generateErrorId() {
        return `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * @brief Handle user notification for errors
     * @param {Object} errorData - Error data
     */
    handleUserNotification(errorData) {
        // Only show notification for certain error types
        const showNotification = [
            'render.error',
            'section.error',
            'app.error'
        ].includes(errorData.type);
        
        if (showNotification) {
            this.eventBus.publish('error:notification', {
                title: 'Application Error',
                message: 'Something went wrong. Please try refreshing the page.',
                errorId: errorData.id,
                severity: 'error'
            });
        }
    }

    /**
     * @brief Intercept console errors (optional)
     */
    interceptConsoleErrors() {
        const originalConsoleError = console.error;
        
        console.error = (...args) => {
            const errorData = {
                type: 'console.error',
                messages: args,
                timestamp: new Date().toISOString(),
                url: window.location.href
            };
            
            this.captureError(errorData);
            originalConsoleError.apply(console, args);
        };
    }

    /**
     * @brief Get all captured errors
     * @returns {Array} Array of error objects
     */
    getErrors() {
        return [...this.errors];
    }

    /**
     * @brief Get errors by type
     * @param {string} type - Error type to filter by
     * @returns {Array} Filtered errors
     */
    getErrorsByType(type) {
        return this.errors.filter(error => error.type === type);
    }

    /**
     * @brief Clear all errors
     */
    clearErrors() {
        this.errors = [];
        this.eventBus.publish('error:cleared');
    }

    /**
     * @brief Report errors to external service
     * @param {string} serviceUrl - External service URL
     * @param {Object} options - Reporting options
     */
    async reportToService(serviceUrl, options = {}) {
        const errorsToReport = options.errors || this.errors;
        
        if (errorsToReport.length === 0) return;
        
        try {
            const reportData = {
                errors: errorsToReport,
                appVersion: options.appVersion || '1.0.0',
                environment: options.environment || 'production',
                timestamp: new Date().toISOString()
            };
            
            const response = await fetch(serviceUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(reportData)
            });
            
            if (response.ok) {
                this.eventBus.publish('error:report:success', {
                    count: errorsToReport.length,
                    service: serviceUrl
                });
                
                // Clear reported errors if configured
                if (options.clearAfterReport) {
                    this.clearErrors();
                }
            } else {
                throw new Error(`Reporting failed with status: ${response.status}`);
            }
            
        } catch (error) {
            console.error('ErrorReporter: Failed to report errors', error);
            this.eventBus.publish('error:report:failed', { error });
        }
    }

    /**
     * @brief Create custom error boundary
     * @param {Function} component - Component function
     * @param {Object} options - Error boundary options
     * @returns {Function} Wrapped component with error boundary
     */
    withErrorBoundary(component, options = {}) {
        return async (...args) => {
            try {
                return await component(...args);
            } catch (error) {
                const errorData = {
                    type: 'error.boundary',
                    component: component.name || 'anonymous',
                    error: error,
                    timestamp: new Date().toISOString(),
                    url: window.location.href
                };
                
                this.captureError(errorData);
                
                if (options.fallback) {
                    return options.fallback(error, errorData);
                }
                
                throw error;
            }
        };
    }

    /**
     * @brief Destroy error reporter
     */
    destroy() {
        window.removeEventListener('error', this.handleError);
        window.removeEventListener('unhandledrejection', this.handleUnhandledRejection);
        
        this.eventBus.clear('app:error');
        this.eventBus.clear('render:error');
        this.eventBus.clear('section:error');
        
        // Restore original console.error if intercepted
        if (console.error.__original) {
            console.error = console.error.__original;
        }
        
        this.errors = [];
        this.isInitialized = false;
        
        console.info('ErrorReporter: Destroyed');
    }
}