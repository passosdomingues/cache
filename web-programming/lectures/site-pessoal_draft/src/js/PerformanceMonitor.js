/**
 * @file PerformanceMonitor.js
 * @brief Comprehensive application performance monitoring and metrics tracking
 * @description Monitors performance metrics, memory usage, and provides optimization insights
 */

class PerformanceMonitor {
    /**
     * @brief Creates a new PerformanceMonitor instance
     * @constructor
     * @param {Object} configuration - Performance monitoring configuration
     */
    constructor(configuration = {}) {
        /**
         * @private
         * @type {Object}
         * @description Performance metrics storage
         */
        this.metrics = {
            cpuUsage: [],
            memoryUsage: [],
            domNodes: [],
            eventListeners: [],
            layoutCount: 0,
            styleRecalculations: 0,
            ...configuration.initialMetrics
        };

        /**
         * @private
         * @type {number|null}
         * @description Monitoring interval reference
         */
        this.monitoringInterval = null;

        /**
         * @private
         * @type {boolean}
         * @description Tracks monitoring status
         */
        this.isMonitoring = false;

        /**
         * @private
         * @type {number}
         * @description Monitoring interval in milliseconds
         */
        this.monitoringFrequency = configuration.frequency || 5000;

        /**
         * @private
         * @type {PerformanceObserver|null}
         * @description Performance observer for long tasks
         */
        this.longTaskObserver = null;

        this.startMonitoring = this.startMonitoring.bind(this);
        this.collectPerformanceMetrics = this.collectPerformanceMetrics.bind(this);
    }

    /**
     * @brief Starts performance monitoring
     * @method startMonitoring
     * @returns {Promise<void>}
     */
    async startMonitoring() {
        if (this.isMonitoring) {
            console.warn('Performance monitoring is already active');
            return;
        }

        try {
            // Set up performance observers
            this.setupPerformanceObservers();
            
            // Start periodic metrics collection
            this.monitoringInterval = setInterval(() => {
                this.collectPerformanceMetrics();
            }, this.monitoringFrequency);
            
            // Collect initial metrics
            await this.collectPerformanceMetrics();
            
            this.isMonitoring = true;
            console.info('Performance monitoring started successfully');
        } catch (error) {
            console.error('Failed to start performance monitoring:', error);
        }
    }

    /**
     * @brief Sets up PerformanceObserver instances for specific metrics
     * @method setupPerformanceObservers
     * @private
     */
    setupPerformanceObservers() {
        // Observe long tasks (tasks longer than 50ms)
        if ('PerformanceObserver' in window) {
            try {
                this.longTaskObserver = new PerformanceObserver((list) => {
                    list.getEntries().forEach((entry) => {
                        console.warn('Long task detected:', entry);
                        this.reportPerformanceIssue('long_task', entry);
                    });
                });
                
                this.longTaskObserver.observe({ entryTypes: ['longtask'] });
            } catch (error) {
                console.warn('Long task observation not supported:', error);
            }
        }
    }

    /**
     * @brief Collects comprehensive performance metrics
     * @method collectPerformanceMetrics
     * @returns {Promise<void>}
     * @private
     */
    async collectPerformanceMetrics() {
        const currentMetrics = await this.gatherCurrentMetrics();
        
        // Store metrics with timestamp
        const timestampedMetrics = {
            ...currentMetrics,
            timestamp: Date.now()
        };
        
        // Update metrics storage
        Object.keys(this.metrics).forEach(metric => {
            if (Array.isArray(this.metrics[metric])) {
                this.metrics[metric].push(timestampedMetrics[metric]);
                
                // Keep only last 100 data points
                if (this.metrics[metric].length > 100) {
                    this.metrics[metric].shift();
                }
            } else {
                this.metrics[metric] = timestampedMetrics[metric];
            }
        });
        
        // Check for performance issues
        this.analyzePerformanceMetrics(timestampedMetrics);
    }

    /**
     * @brief Gathers current performance metrics from browser APIs
     * @method gatherCurrentMetrics
     * @returns {Promise<Object>} Current performance metrics
     * @private
     */
    async gatherCurrentMetrics() {
        const metrics = {};

        // Memory usage (if available)
        if (performance.memory) {
            metrics.memoryUsage = {
                used: performance.memory.usedJSHeapSize,
                total: performance.memory.totalJSHeapSize,
                limit: performance.memory.jsHeapSizeLimit
            };
        }

        // DOM metrics
        metrics.domNodes = document.getElementsByTagName('*').length;
        metrics.eventListeners = this.countEventListeners();
        
        // Navigation timing
        if (performance.timing) {
            const timing = performance.timing;
            metrics.loadTime = timing.loadEventEnd - timing.navigationStart;
            metrics.domReadyTime = timing.domContentLoadedEventEnd - timing.navigationStart;
        }

        // Resource timing
        metrics.resourceCount = performance.getEntriesByType('resource').length;

        return metrics;
    }

    /**
     * @brief Estimates current event listener count
     * @method countEventListeners
     * @returns {number} Estimated event listener count
     * @private
     */
    countEventListeners() {
        let count = 0;
        const elements = document.getElementsByTagName('*');
        
        for (let element of elements) {
            // This is an approximation since we can't directly access listener count
            if (element._listeners) {
                count += element._listeners;
            }
        }
        
        return count;
    }

    /**
     * @brief Analyzes collected metrics for performance issues
     * @method analyzePerformanceMetrics
     * @param {Object} currentMetrics - Current performance metrics
     * @private
     */
    analyzePerformanceMetrics(currentMetrics) {
        // Check for memory leaks
        if (this.detectMemoryLeak()) {
            this.reportPerformanceIssue('memory_leak', currentMetrics);
        }

        // Check for excessive DOM size
        if (currentMetrics.domNodes > 10000) {
            this.reportPerformanceIssue('excessive_dom_nodes', currentMetrics);
        }

        // Check for long load times
        if (currentMetrics.loadTime > 3000) {
            this.reportPerformanceIssue('slow_load_time', currentMetrics);
        }
    }

    /**
     * @brief Detects potential memory leaks
     * @method detectMemoryLeak
     * @returns {boolean} True if memory leak detected
     * @private
     */
    detectMemoryLeak() {
        if (this.metrics.memoryUsage.length < 10) return false;

        const recentMetrics = this.metrics.memoryUsage.slice(-5);
        const increasingTrend = recentMetrics.every((metric, index) => {
            if (index === 0) return true;
            return metric.used > recentMetrics[index - 1].used;
        });

        return increasingTrend;
    }

    /**
     * @brief Reports performance issues
     * @method reportPerformanceIssue
     * @param {string} issueType - Type of performance issue
     * @param {Object} metrics - Related performance metrics
     * @private
     */
    reportPerformanceIssue(issueType, metrics) {
        const performanceEvent = new CustomEvent('performance:issue', {
            detail: {
                issueType,
                metrics,
                timestamp: Date.now(),
                suggestions: this.getPerformanceSuggestions(issueType)
            },
            bubbles: true
        });
        
        window.dispatchEvent(performanceEvent);
        console.warn(`Performance issue detected: ${issueType}`, metrics);
    }

    /**
     * @brief Gets performance improvement suggestions
     * @method getPerformanceSuggestions
     * @param {string} issueType - Type of performance issue
     * @returns {Array<string>} Performance improvement suggestions
     * @private
     */
    getPerformanceSuggestions(issueType) {
        const suggestions = {
            memory_leak: [
                'Check for circular references',
                'Remove unused event listeners',
                'Clear intervals and timeouts',
                'Use weak references where appropriate'
            ],
            excessive_dom_nodes: [
                'Implement virtual scrolling for long lists',
                'Use pagination or infinite scrolling',
                'Remove hidden DOM elements',
                'Implement code splitting'
            ],
            slow_load_time: [
                'Optimize bundle size with tree shaking',
                'Implement lazy loading',
                'Use CDN for static assets',
                'Enable compression'
            ],
            long_task: [
                'Break up long-running JavaScript',
                'Use web workers for heavy computation',
                'Optimize expensive loops',
                'Implement requestAnimationFrame for animations'
            ]
        };

        return suggestions[issueType] || ['Investigate performance bottlenecks'];
    }

    /**
     * @brief Gets current performance metrics
     * @method getMetrics
     * @returns {Object} Current performance metrics
     */
    getMetrics() {
        return { ...this.metrics };
    }

    /**
     * @brief Gets performance summary for reporting
     * @method getPerformanceSummary
     * @returns {Object} Performance summary
     */
    getPerformanceSummary() {
        const latestMetrics = this.metrics.memoryUsage[this.metrics.memoryUsage.length - 1] || {};
        
        return {
            domNodeCount: this.metrics.domNodes[this.metrics.domNodes.length - 1] || 0,
            eventListenerCount: this.metrics.eventListeners[this.metrics.eventListeners.length - 1] || 0,
            memoryUsage: latestMetrics.used || 0,
            loadTime: this.metrics.loadTime || 0,
            isHealthy: !this.detectMemoryLeak() && 
                      (this.metrics.domNodes[this.metrics.domNodes.length - 1] || 0) < 5000
        };
    }

    /**
     * @brief Stops performance monitoring
     * @method stopMonitoring
     * @returns {void}
     */
    stopMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }

        if (this.longTaskObserver) {
            this.longTaskObserver.disconnect();
            this.longTaskObserver = null;
        }

        this.isMonitoring = false;
        console.info('Performance monitoring stopped');
    }

    /**
     * @brief Cleans up performance monitor resources
     * @method destroy
     * @returns {void}
     */
    destroy() {
        this.stopMonitoring();
        this.metrics = {};
        console.info('PerformanceMonitor destroyed successfully');
    }
}

export default PerformanceMonitor;