import eventBus from '../core/EventBus.js';

/**
 * @brief Performance monitoring service
 * @description Tracks application performance metrics and user interactions
 */
export class PerformanceMonitor {
    constructor(dependencies = {}) {
        this.eventBus = dependencies.eventBus || eventBus;
        this.metrics = new Map();
        this.isInitialized = false;
        
        this.onFirstContentfulPaint = this.onFirstContentfulPaint.bind(this);
        this.onLargestContentfulPaint = this.onLargestContentfulPaint.bind(this);
    }

    /**
     * @brief Initialize performance monitor
     * @description Sets up performance observers and metrics tracking
     */
    async init() {
        if (this.isInitialized) return;

        try {
            this.setupPerformanceObservers();
            this.setupEventListeners();
            this.trackInitialLoad();
            
            this.isInitialized = true;
            console.info('PerformanceMonitor: Initialized successfully');
            
        } catch (error) {
            console.error('PerformanceMonitor: Initialization failed', error);
        }
    }

    /**
     * @brief Set up performance observers
     */
    setupPerformanceObservers() {
        // Observe Largest Contentful Paint
        if ('PerformanceObserver' in window) {
            try {
                // LCP Observer
                const lcpObserver = new PerformanceObserver((entryList) => {
                    const entries = entryList.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    this.metrics.set('lcp', lastEntry.startTime);
                    this.onLargestContentfulPaint(lastEntry);
                });
                lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });

                // FID Observer
                const fidObserver = new PerformanceObserver((entryList) => {
                    const entries = entryList.getEntries();
                    entries.forEach(entry => {
                        this.metrics.set('fid', entry.processingStart - entry.startTime);
                        this.eventBus.publish('performance:metric', {
                            name: 'fid',
                            value: entry.processingStart - entry.startTime,
                            entry
                        });
                    });
                });
                fidObserver.observe({ type: 'first-input', buffered: true });

                // CLS Observer
                const clsObserver = new PerformanceObserver((entryList) => {
                    let clsValue = 0;
                    const entries = entryList.getEntries();
                    entries.forEach(entry => {
                        if (!entry.hadRecentInput) {
                            clsValue += entry.value;
                        }
                    });
                    this.metrics.set('cls', clsValue);
                    this.eventBus.publish('performance:metric', {
                        name: 'cls',
                        value: clsValue
                    });
                });
                clsObserver.observe({ type: 'layout-shift', buffered: true });

            } catch (error) {
                console.warn('PerformanceMonitor: Performance Observer not supported', error);
            }
        }
    }

    /**
     * @brief Set up event listeners
     */
    setupEventListeners() {
        // Track navigation performance
        this.eventBus.subscribe('router:navigated', this.onNavigation.bind(this));
        
        // Track resource loading
        this.eventBus.subscribe('view:section:rendered', this.onSectionRendered.bind(this));
        
        // Track user interactions
        document.addEventListener('click', this.onUserInteraction.bind(this));
    }

    /**
     * @brief Track initial page load performance
     */
    trackInitialLoad() {
        if (window.performance) {
            const navigationTiming = performance.getEntriesByType('navigation')[0];
            if (navigationTiming) {
                this.metrics.set('loadTime', navigationTiming.loadEventEnd - navigationTiming.navigationStart);
                this.metrics.set('domContentLoaded', navigationTiming.domContentLoadedEventEnd - navigationTiming.navigationStart);
                
                this.eventBus.publish('performance:load', {
                    loadTime: this.metrics.get('loadTime'),
                    domContentLoaded: this.metrics.get('domContentLoaded'),
                    timing: navigationTiming
                });
            }

            // First Contentful Paint
            const paintEntries = performance.getEntriesByType('paint');
            paintEntries.forEach(entry => {
                if (entry.name === 'first-contentful-paint') {
                    this.metrics.set('fcp', entry.startTime);
                    this.onFirstContentfulPaint(entry);
                }
            });
        }
    }

    /**
     * @brief Handle First Contentful Paint
     * @param {PerformanceEntry} entry - Performance entry
     */
    onFirstContentfulPaint(entry) {
        this.eventBus.publish('performance:metric', {
            name: 'fcp',
            value: entry.startTime,
            entry
        });
        
        console.info(`PerformanceMonitor: First Contentful Paint at ${entry.startTime}ms`);
    }

    /**
     * @brief Handle Largest Contentful Paint
     * @param {PerformanceEntry} entry - Performance entry
     */
    onLargestContentfulPaint(entry) {
        this.eventBus.publish('performance:metric', {
            name: 'lcp',
            value: entry.startTime,
            entry
        });
        
        console.info(`PerformanceMonitor: Largest Contentful Paint at ${entry.startTime}ms`);
    }

    /**
     * @brief Handle navigation events
     * @param {Object} data - Navigation data
     */
    onNavigation(data) {
        const navigationStart = performance.now();
        this.metrics.set('lastNavigationStart', navigationStart);
        
        this.eventBus.publish('performance:navigation:start', {
            from: data.from,
            to: data.to,
            timestamp: navigationStart
        });
    }

    /**
     * @brief Handle section rendering
     * @param {Object} data - Section data
     */
    onSectionRendered(data) {
        const renderTime = performance.now();
        const navigationStart = this.metrics.get('lastNavigationStart');
        
        if (navigationStart) {
            const navigationDuration = renderTime - navigationStart;
            this.eventBus.publish('performance:navigation:complete', {
                sectionId: data.sectionId,
                duration: navigationDuration,
                timestamp: renderTime
            });
        }
    }

    /**
     * @brief Handle user interactions
     * @param {Event} event - User interaction event
     */
    onUserInteraction(event) {
        const interactionTime = performance.now();
        
        this.eventBus.publish('performance:interaction', {
            type: event.type,
            target: event.target.tagName,
            timestamp: interactionTime
        });
    }

    /**
     * @brief Get performance metrics
     * @returns {Object} Performance metrics object
     */
    getMetrics() {
        return Object.fromEntries(this.metrics);
    }

    /**
     * @brief Get specific metric value
     * @param {string} metricName - Name of the metric
     * @returns {number|undefined} Metric value
     */
    getMetric(metricName) {
        return this.metrics.get(metricName);
    }

    /**
     * @brief Measure function execution time
     * @param {Function} fn - Function to measure
     * @param {string} name - Measurement name
     * @returns {Promise<{result: *, duration: number}>} Execution result and duration
     */
    async measureExecution(fn, name = 'anonymous') {
        const startTime = performance.now();
        const result = await fn();
        const duration = performance.now() - startTime;
        
        this.eventBus.publish('performance:execution', {
            name,
            duration,
            timestamp: startTime
        });
        
        return { result, duration };
    }

    /**
     * @brief Report performance data to analytics
     * @param {Object} additionalData - Additional data to include
     */
    reportPerformance(additionalData = {}) {
        const performanceData = {
            ...this.getMetrics(),
            ...additionalData,
            userAgent: navigator.userAgent,
            connection: navigator.connection ? {
                effectiveType: navigator.connection.effectiveType,
                downlink: navigator.connection.downlink,
                rtt: navigator.connection.rtt
            } : null
        };
        
        this.eventBus.publish('performance:report', performanceData);
        
        // Could send to analytics service here
        console.info('PerformanceMonitor: Performance report', performanceData);
    }

    /**
     * @brief Check if performance meets thresholds
     * @param {Object} thresholds - Performance thresholds
     * @returns {Object} Threshold compliance results
     */
    checkThresholds(thresholds = {}) {
        const defaultThresholds = {
            fcp: 2000,    // 2 seconds
            lcp: 2500,    // 2.5 seconds
            fid: 100,     // 100ms
            cls: 0.1      // 0.1
        };
        
        const actualThresholds = { ...defaultThresholds, ...thresholds };
        const results = {};
        
        for (const [metric, threshold] of Object.entries(actualThresholds)) {
            const value = this.metrics.get(metric);
            results[metric] = {
                value,
                threshold,
                meets: value !== undefined ? value <= threshold : undefined
            };
        }
        
        return results;
    }

    /**
     * @brief Destroy performance monitor
     */
    destroy() {
        this.eventBus.clear('router:navigated');
        this.eventBus.clear('view:section:rendered');
        document.removeEventListener('click', this.onUserInteraction);
        
        this.metrics.clear();
        this.isInitialized = false;
        
        console.info('PerformanceMonitor: Destroyed');
    }
}