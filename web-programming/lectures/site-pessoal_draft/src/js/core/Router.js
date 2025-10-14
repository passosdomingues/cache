import { eventBus } from './EventBus.js';

/**
 * @brief Client-side router for SPA navigation
 * @description Handles route changes and history management
 */
export class Router {
    constructor(config = {}) {
        this.config = config;
        this.routes = new Map();
        this.currentRoute = null;
        this.eventBus = eventBus;
        
        this.handlePopState = this.handlePopState.bind(this);
        this.handleLinkClick = this.handleLinkClick.bind(this);
    }

    /**
     * @brief Initialize the router
     * @description Sets up event listeners and initial route
     */
    init() {
        this.setupEventListeners();
        this.navigate(window.location.pathname, { replace: true, silent: true });
        
        console.info('Router: Router initialized');
    }

    /**
     * @brief Set up router event listeners
     */
    setupEventListeners() {
        window.addEventListener('popstate', this.handlePopState);
        document.addEventListener('click', this.handleLinkClick);
    }

    /**
     * @brief Handle browser back/forward navigation
     * @param {PopStateEvent} event - Pop state event
     */
    handlePopState(event) {
        this.navigate(window.location.pathname, { silent: true });
    }

    /**
     * @brief Handle link clicks for SPA navigation
     * @param {MouseEvent} event - Click event
     */
    handleLinkClick(event) {
        const link = event.target.closest('a[href]');
        if (!link) return;

        const href = link.getAttribute('href');
        
        // Only handle internal links
        if (href && href.startsWith('/') && !href.startsWith('//')) {
            event.preventDefault();
            this.navigate(href);
        }
    }

    /**
     * @brief Add a route
     * @param {string} path - Route path
     * @param {Object} config - Route configuration
     */
    addRoute(path, config) {
        this.routes.set(path, config);
    }

    /**
     * @brief Navigate to a route
     * @param {string} path - Path to navigate to
     * @param {Object} options - Navigation options
     */
    navigate(path, options = {}) {
        const { replace = false, silent = false } = options;
        
        // Find matching route
        const route = this.findMatchingRoute(path);
        
        if (route) {
            this.executeRoute(route, path, silent);
            
            // Update browser history
            if (!silent) {
                if (replace) {
                    window.history.replaceState({}, '', path);
                } else {
                    window.history.pushState({}, '', path);
                }
            }
        } else {
            console.warn(`Router: No route found for path: ${path}`);
            this.eventBus.publish('router:404', { path });
        }
    }

    /**
     * @brief Find matching route for path
     * @param {string} path - Path to match
     * @returns {Object|null} Matching route configuration
     */
    findMatchingRoute(path) {
        for (const [routePath, config] of this.routes) {
            if (this.pathMatches(routePath, path)) {
                return config;
            }
        }
        return null;
    }

    /**
     * @brief Check if path matches route pattern
     * @param {string} routePath - Route pattern
     * @param {string} path - Actual path
     * @returns {boolean} Whether path matches
     */
    pathMatches(routePath, path) {
        // Simple exact match for now - can be extended for dynamic routes
        return routePath === path;
    }

    /**
     * @brief Execute route handlers
     * @param {Object} route - Route configuration
     * @param {string} path - Actual path
     * @param {boolean} silent - Whether to suppress events
     */
    executeRoute(route, path, silent = false) {
        const previousRoute = this.currentRoute;
        this.currentRoute = { path, config: route };

        if (!silent) {
            this.eventBus.publish('router:beforeNavigate', { 
                from: previousRoute, 
                to: this.currentRoute 
            });
        }

        // Execute route handler
        if (typeof route.handler === 'function') {
            route.handler(this.currentRoute);
        }

        if (!silent) {
            this.eventBus.publish('router:navigated', { 
                from: previousRoute, 
                to: this.currentRoute 
            });
        }

        console.info(`Router: Navigated to ${path}`);
    }

    /**
     * @brief Get current route information
     * @returns {Object|null} Current route
     */
    getCurrentRoute() {
        return this.currentRoute;
    }

    /**
     * @brief Destroy router and clean up
     */
    destroy() {
        window.removeEventListener('popstate', this.handlePopState);
        document.removeEventListener('click', this.handleLinkClick);
        this.routes.clear();
        
        console.info('Router: Router destroyed');
    }
}