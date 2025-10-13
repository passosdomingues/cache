/**
 * @file NavigationView.js
 * @author Rafael Passos Domingues
 * @version 3.0.0
 * @brief Navigation view component handling main navigation rendering and interactive behavior.
 * @description Provides responsive navigation with mobile menu, keyboard accessibility,
 * scroll behavior, and dynamic state management with performance optimizations.
 */

/**
 * @constant {Object} NAVIGATION_CONFIG
 * @brief Configuration data for navigation structure and behavior
 * @description Defines navigation items, icons, accessibility labels, and routing paths
 */
const NAVIGATION_CONFIG = [
    {
        path: '/',
        label: 'Home',
        icon: 'home',
        ariaLabel: 'Go to home page',
        priority: 1,
        isPrimary: true
    },
    {
        path: '/about',
        label: 'About',
        icon: 'user',
        ariaLabel: 'Learn more about my background and experience',
        priority: 2,
        isPrimary: true
    },
    {
        path: '/projects',
        label: 'Projects',
        icon: 'code',
        ariaLabel: 'View my technical projects and development work',
        priority: 3,
        isPrimary: true
    },
    {
        path: '/research',
        label: 'Research',
        icon: 'microscope',
        ariaLabel: 'Explore my scientific research and publications',
        priority: 4,
        isPrimary: true
    },
    {
        path: '/contact',
        label: 'Contact',
        icon: 'envelope',
        ariaLabel: 'Get in touch with me for opportunities and collaboration',
        priority: 5,
        isPrimary: true
    }
];

/**
 * @constant {Object} NAVIGATION_CONSTANTS
 * @brief Constants for navigation behavior and configuration
 * @description Defines thresholds, delays, and configuration values for navigation interactions
 */
const NAVIGATION_CONSTANTS = {
    SCROLL_THRESHOLD: 100,
    SCROLL_HIDE_DELTA: 5,
    SCROLL_SHOW_DELTA: -5,
    MOBILE_MENU_BREAKPOINT: 768,
    SCROLL_THROTTLE_DELAY: 16, // ~60fps
    FOCUS_MANAGEMENT_DELAY: 150,
    ESCAPE_KEY: 'Escape',
    ARROW_KEYS: ['ArrowRight', 'ArrowLeft', 'ArrowUp', 'ArrowDown'],
    NAVIGATION_KEYS: ['Home', 'End']
};

/**
 * @class NavigationView
 * @brief Navigation view component managing rendering and interactivity
 * @description Handles responsive navigation with mobile menu, keyboard navigation,
 * scroll behavior, and accessibility features with performance optimizations
 */
class NavigationView {
    /**
     * @brief Creates an instance of NavigationView
     * @constructor
     * @param {HTMLElement} containerElement - The DOM element to render navigation into
     */
    constructor(containerElement) {
        if (!containerElement || !(containerElement instanceof HTMLElement)) {
            throw new Error('NavigationView requires a valid HTMLElement container');
        }

        /**
         * @private
         * @type {HTMLElement}
         * @brief Container element where navigation is rendered
         */
        this.containerElement = containerElement;

        /**
         * @private
         * @type {Object}
         * @brief Current state of the navigation component
         */
        this.navigationState = {
            currentPath: '/',
            isMobileMenuOpen: false,
            isNavigationVisible: true,
            lastScrollPosition: 0,
            hasScrolled: false
        };

        /**
         * @private
         * @type {AbortController}
         * @brief Manages cleanup of event listeners
         */
        this.eventAbortController = new AbortController();

        /**
         * @private
         * @type {Function[]}
         * @brief Collection of observer callbacks for state changes
         */
        this.observers = [];

        /**
         * @private
         * @type {boolean}
         * @brief Tracks if navigation has been initialized
         */
        this.isInitialized = false;

        // Bind methods to maintain context
        this.toggleMobileMenuState = this.toggleMobileMenuState.bind(this);
        this.closeMobileMenu = this.closeMobileMenu.bind(this);
        this.handleWindowResize = this.handleWindowResize.bind(this);
        this.handleNavigationKeydown = this.handleNavigationKeydown.bind(this);
        this.updateNavigationScrollState = this.updateNavigationScrollState.bind(this);
        this.handleNavigationClick = this.handleNavigationClick.bind(this);
        this.triggerFlashback = this.triggerFlashback.bind(this);

        console.debug('NavigationView: Instance created with container:', containerElement);
    }

    /**
     * @brief Renders the navigation component with current state
     * @public
     * @param {Object} renderData - Data for rendering the navigation
     * @param {string} renderData.currentPath - Currently active path
     * @param {boolean} renderData.isMobileMenuOpen - Mobile menu visibility state
     * @returns {string} HTML string representation of the navigation component
     */
    render(renderData = {}) {
        const { currentPath = '/', isMobileMenuOpen = false } = renderData;
        
        // Update internal state
        this.navigationState.currentPath = currentPath;
        this.navigationState.isMobileMenuOpen = isMobileMenuOpen;

        const navigationHtml = this.generateNavigationHtml(currentPath, isMobileMenuOpen);
        return navigationHtml;
    }

    /**
     * @brief Generates complete navigation HTML structure
     * @private
     * @param {string} currentPath - Currently active path for highlighting
     * @param {boolean} isMobileMenuOpen - Mobile menu visibility state
     * @returns {string} Complete navigation HTML string
     */
    generateNavigationHtml(currentPath, isMobileMenuOpen) {
        return `
            <nav class="main-navigation" role="navigation" aria-label="Main navigation">
                <div class="navigation-container">
                    ${this.generateBrandSection()}
                    ${this.generateDesktopNavigation(currentPath)}
                    ${this.generateMobileNavigationToggle(isMobileMenuOpen)}
                    ${this.generateFlashbackButton()}
                    ${this.generateMobileNavigationMenu(currentPath, isMobileMenuOpen)}
                </div>
            </nav>
        `;
    }

    /**
     * @brief Generates brand/logo section HTML
     * @private
     * @returns {string} Brand section HTML string
     */
    generateBrandSection() {
        return `
            <div class="navigation-brand">
                <a href="/" class="brand-link" aria-label="Rafael Passos Domingues - Home">
                    <span class="brand-text">Rafael Passos Domingues</span>
                    <span class="brand-subtitle">Physicist & Computer Scientist</span>
                </a>
            </div>
        `;
    }

    /**
     * @brief Generates desktop navigation menu HTML
     * @private
     * @param {string} currentPath - Currently active path for highlighting
     * @returns {string} Desktop navigation menu HTML string
     */
    generateDesktopNavigation(currentPath) {
        return `
            <ul class="navigation-menu navigation-menu--desktop" role="menubar">
                ${NAVIGATION_CONFIG.map(navItem => 
                    this.generateNavigationItem(navItem, currentPath)
                ).join('')}
            </ul>
        `;
    }

    /**
     * @brief Generates mobile navigation toggle button HTML
     * @private
     * @param {boolean} isMobileMenuOpen - Mobile menu visibility state
     * @returns {string} Mobile navigation toggle HTML string
     */
    generateMobileNavigationToggle(isMobileMenuOpen) {
        return `
            <button 
                class="mobile-navigation-toggle"
                aria-label="Toggle mobile navigation menu"
                aria-expanded="${isMobileMenuOpen}"
                aria-controls="mobile-navigation-menu"
                aria-haspopup="true"
            >
                <span class="hamburger-line hamburger-line--top"></span>
                <span class="hamburger-line hamburger-line--middle"></span>
                <span class="hamburger-line hamburger-line--bottom"></span>
                <span class="visually-hidden">Mobile menu</span>
            </button>
        `;
    }

    /**
     * @brief Generates mobile navigation menu HTML
     * @private
     * @param {string} currentPath - Currently active path for highlighting
     * @param {boolean} isMobileMenuOpen - Mobile menu visibility state
     * @returns {string} Mobile navigation menu HTML string
     */
    generateMobileNavigationMenu(currentPath, isMobileMenuOpen) {
        return `
            <div 
                id="mobile-navigation-menu" 
                class="mobile-navigation-menu ${isMobileMenuOpen ? 'mobile-navigation-menu--open' : ''}"
                aria-hidden="${!isMobileMenuOpen}"
                role="menu"
            >
                <ul class="navigation-menu navigation-menu--mobile" role="menubar">
                    ${NAVIGATION_CONFIG.map(navItem => 
                        this.generateNavigationItem(navItem, currentPath, true)
                    ).join('')}
                </ul>
            </div>
        `;
    }

    /**
     * @brief Generates individual navigation item HTML
     * @private
     * @param {Object} navItem - Navigation item configuration
     * @param {string} currentPath - Currently active path for highlighting
     * @param {boolean} isMobile - Whether this is for mobile navigation
     * @returns {string} Navigation item HTML string
     */
    generateNavigationItem(navItem, currentPath, isMobile = false) {
        const isActive = currentPath === navItem.path;
        const linkClassNames = `navigation-link ${isActive ? 'navigation-link--active' : ''} ${isMobile ? 'navigation-link--mobile' : 'navigation-link--desktop'}`;
        
        return `
            <li class="navigation-item" role="none">
                <a 
                    href="${navItem.path}"
                    class="${linkClassNames}"
                    role="menuitem"
                    aria-label="${navItem.ariaLabel}"
                    ${isActive ? 'aria-current="page"' : ''}
                    data-navigation-path="${navItem.path}"
                >
                    <i class="fas fa-${navItem.icon} navigation-icon" aria-hidden="true"></i>
                    <span class="navigation-link-text">${navItem.label}</span>
                    ${isActive ? '<span class="visually-hidden">(current page)</span>' : ''}
                </a>
            </li>
        `;
    }

    /**
     * @brief Generates flashback button HTML
     * @private
     * @returns {string} Flashback button HTML string
     */
    generateFlashbackButton() {
        return `
            <button 
                class="flashback-button btn btn--secondary btn--sm"
                aria-label="Get a random flashback from my journey"
            >
                <i class="fas fa-random" aria-hidden="true"></i>
                <span class="flashback-button-text">Flashback</span>
            </button>
        `;
    }

    /**
     * @brief Initializes navigation interactivity and event handlers
     * @public
     * @param {Object} initializationData - Data for initialization
     * @returns {Promise<void>} Resolves when navigation is fully initialized
     */
    async initialize(initializationData = {}) {
        try {
            await this.setupNavigationInteractivity();
            this.isInitialized = true;
            console.info('NavigationView: Navigation interactivity initialized successfully.');
        } catch (error) {
            console.error('NavigationView: Failed to initialize navigation:', error);
            throw error;
        }
    }

    /**
     * @brief Sets up all navigation interactivity systems
     * @private
     * @returns {Promise<void>} Resolves when all interactivity systems are set up
     */
    async setupNavigationInteractivity() {
        const navigationElement = this.containerElement.querySelector('.main-navigation');
        if (!navigationElement) {
            throw new Error('NavigationView: Navigation element not found in container');
        }

        const setupPromises = [
            this.setupMobileMenuInteractions(navigationElement),
            this.setupKeyboardNavigation(navigationElement),
            this.setupScrollBehavior(navigationElement),
            this.setupNavigationClickHandlers(navigationElement),
            this.setupFlashbackInteractions(navigationElement)
        ];

        await Promise.all(setupPromises);
    }

    /**
     * @brief Sets up mobile menu interactions and event handlers
     * @private
     * @param {HTMLElement} navigationElement - The navigation container element
     * @returns {Promise<void>} Resolves when mobile menu interactions are set up
     */
    async setupMobileMenuInteractions(navigationElement) {
        const mobileMenuToggle = navigationElement.querySelector('.mobile-navigation-toggle');
        const mobileMenu = navigationElement.querySelector('.mobile-navigation-menu');
        
        if (!mobileMenuToggle || !mobileMenu) {
            console.warn('NavigationView: Mobile menu elements not found');
            return;
        }

        const eventSignal = this.eventAbortController.signal;

        // Toggle mobile menu on button click
        mobileMenuToggle.addEventListener('click', () => {
            this.toggleMobileMenuState();
        }, { signal: eventSignal });

        // Close mobile menu on escape key
        document.addEventListener('keydown', (event) => {
            if (event.key === NAVIGATION_CONSTANTS.ESCAPE_KEY && this.navigationState.isMobileMenuOpen) {
                this.closeMobileMenu();
            }
        }, { signal: eventSignal });

        // Close mobile menu when clicking outside
        document.addEventListener('click', (event) => {
            if (!navigationElement.contains(event.target) && this.navigationState.isMobileMenuOpen) {
                this.closeMobileMenu();
            }
        }, { signal: eventSignal });

        // Close mobile menu on navigation link click
        const mobileLinks = mobileMenu.querySelectorAll('.navigation-link');
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                this.closeMobileMenu();
            }, { signal: eventSignal });
        });

        // Handle window resize for mobile menu
        window.addEventListener('resize', () => {
            this.handleWindowResize();
        }, { signal: eventSignal });

        console.debug('NavigationView: Mobile menu interactions initialized.');
    }

    /**
     * @brief Sets up flashback button interactions
     * @private
     * @param {HTMLElement} navigationElement - The navigation container element
     * @returns {Promise<void>} Resolves when flashback interactions are set up
     */
    async setupFlashbackInteractions(navigationElement) {
        const flashbackButton = navigationElement.querySelector(".flashback-button");
        if (!flashbackButton) return;

        flashbackButton.addEventListener("click", () => {
            this.triggerFlashback();
        }, { signal: this.eventAbortController.signal });
    }

    /**
     * @brief Toggles mobile menu open/closed state
     * @private
     */
    toggleMobileMenuState() {
        const newMenuState = !this.navigationState.isMobileMenuOpen;
        this.navigationState.isMobileMenuOpen = newMenuState;

        this.updateMobileMenuDomState();
        this.updateBodyScrollLock();

        // Notify observers of menu state change
        this.notifyObservers('mobileMenuToggled', {
            isOpen: newMenuState,
            menuId: 'mobile-navigation-menu'
        });

        console.debug(`NavigationView: Mobile menu ${newMenuState ? 'opened' : 'closed'}.`);
    }

    /**
     * @brief Closes mobile menu and updates state
     * @private
     */
    closeMobileMenu() {
        if (!this.navigationState.isMobileMenuOpen) return;

        this.navigationState.isMobileMenuOpen = false;
        this.updateMobileMenuDomState();
        this.updateBodyScrollLock();

        this.notifyObservers('mobileMenuClosed', {
            menuId: 'mobile-navigation-menu'
        });

        console.debug('NavigationView: Mobile menu closed.');
    }

    /**
     * @brief Updates DOM state for mobile menu visibility
     * @private
     */
    updateMobileMenuDomState() {
        const mobileMenu = this.containerElement.querySelector('.mobile-navigation-menu');
        const mobileToggle = this.containerElement.querySelector('.mobile-navigation-toggle');

        if (mobileMenu) {
            mobileMenu.classList.toggle('mobile-navigation-menu--open', this.navigationState.isMobileMenuOpen);
            mobileMenu.setAttribute('aria-hidden', (!this.navigationState.isMobileMenuOpen).toString());
        }

        if (mobileToggle) {
            mobileToggle.setAttribute('aria-expanded', this.navigationState.isMobileMenuOpen.toString());
        }
    }

    /**
     * @brief Updates body scroll lock based on mobile menu state
     * @private
     */
    updateBodyScrollLock() {
        if (this.navigationState.isMobileMenuOpen) {
            document.body.style.overflow = 'hidden';
            document.body.setAttribute('data-mobile-menu-open', 'true');
        } else {
            document.body.style.overflow = '';
            document.body.removeAttribute('data-mobile-menu-open');
        }
    }

    /**
     * @brief Handles window resize events for responsive behavior
     * @private
     */
    handleWindowResize() {
        const windowWidth = window.innerWidth;
        
        // Close mobile menu when resizing to desktop breakpoint
        if (windowWidth >= NAVIGATION_CONSTANTS.MOBILE_MENU_BREAKPOINT && this.navigationState.isMobileMenuOpen) {
            this.closeMobileMenu();
        }
    }

    /**
     * @brief Sets up keyboard navigation for accessibility
     * @private
     * @param {HTMLElement} navigationElement - The navigation container element
     * @returns {Promise<void>} Resolves when keyboard navigation is set up
     */
    async setupKeyboardNavigation(navigationElement) {
        const navigationLinks = navigationElement.querySelectorAll('.navigation-link');
        
        navigationLinks.forEach((link, currentIndex) => {
            link.addEventListener('keydown', (event) => {
                this.handleNavigationKeydown(event, navigationLinks, currentIndex);
            }, { signal: this.eventAbortController.signal });
        });

        console.debug('NavigationView: Keyboard navigation initialized.');
    }

    /**
     * @brief Handles keyboard navigation events
     * @private
     * @param {KeyboardEvent} event - Keyboard event object
     * @param {NodeList} navigationLinks - Collection of navigation link elements
     * @param {number} currentIndex - Index of the currently focused link
     */
    handleNavigationKeydown(event, navigationLinks, currentIndex) {
        const { key } = event;
        const linkCount = navigationLinks.length;

        // Handle arrow key navigation
        if (NAVIGATION_CONSTANTS.ARROW_KEYS.includes(key)) {
            event.preventDefault();
            this.handleArrowKeyNavigation(key, navigationLinks, currentIndex, linkCount);
        }

        // Handle Home/End key navigation
        if (NAVIGATION_CONSTANTS.NAVIGATION_KEYS.includes(key)) {
            event.preventDefault();
            this.handleHomeEndNavigation(key, navigationLinks, linkCount);
        }
    }

    /**
     * @brief Handles arrow key navigation between menu items
     * @private
     * @param {string} key - The pressed arrow key
     * @param {NodeList} navigationLinks - Collection of navigation link elements
     * @param {number} currentIndex - Index of the currently focused link
     * @param {number} linkCount - Total number of navigation links
     */
    handleArrowKeyNavigation(key, navigationLinks, currentIndex, linkCount) {
        let targetIndex;

        switch (key) {
            case 'ArrowRight':
            case 'ArrowDown':
                targetIndex = (currentIndex + 1) % linkCount;
                break;
            case 'ArrowLeft':
            case 'ArrowUp':
                targetIndex = currentIndex > 0 ? currentIndex - 1 : linkCount - 1;
                break;
            default:
                return;
        }

        this.focusNavigationLink(navigationLinks, targetIndex);
    }

    /**
     * @brief Handles Home/End key navigation
     * @private
     * @param {string} key - The pressed key (Home or End)
     * @param {NodeList} navigationLinks - Collection of navigation link elements
     * @param {number} linkCount - Total number of navigation links
     */
    handleHomeEndNavigation(key, navigationLinks, linkCount) {
        const targetIndex = key === 'Home' ? 0 : linkCount - 1;
        this.focusNavigationLink(navigationLinks, targetIndex);
    }

    /**
     * @brief Focuses a specific navigation link by index
     * @private
     * @param {NodeList} navigationLinks - Collection of navigation link elements
     * @param {number} targetIndex - Index of the link to focus
     */
    focusNavigationLink(navigationLinks, targetIndex) {
        const targetLink = navigationLinks[targetIndex];
        if (targetLink) {
            targetLink.focus();
            
            this.notifyObservers('navigationKeyNavigated', {
                targetIndex,
                totalLinks: navigationLinks.length,
                linkHref: targetLink.getAttribute('href')
            });
        }
    }

    /**
     * @brief Sets up scroll behavior for navigation visibility
     * @private
     * @param {HTMLElement} navigationElement - The navigation container element
     * @returns {Promise<void>} Resolves when scroll behavior is set up
     */
    async setupScrollBehavior(navigationElement) {
        let isScrollHandlerRunning = false;

        const handleScroll = () => {
            if (isScrollHandlerRunning) return;

            isScrollHandlerRunning = true;
            requestAnimationFrame(() => {
                this.updateNavigationScrollState(navigationElement);
                isScrollHandlerRunning = false;
            });
        };

        window.addEventListener('scroll', handleScroll, {
            passive: true,
            signal: this.eventAbortController.signal
        });

        // Initial scroll state update
        this.updateNavigationScrollState(navigationElement);

        console.debug('NavigationView: Scroll behavior initialized.');
    }

    /**
     * @brief Updates navigation state based on scroll position
     * @private
     * @param {HTMLElement} navigationElement - The navigation container element
     */
    updateNavigationScrollState(navigationElement) {
        const currentScrollY = window.scrollY;
        const scrollDelta = currentScrollY - this.navigationState.lastScrollPosition;

        // Update navigation visibility based on scroll direction
        if (scrollDelta > NAVIGATION_CONSTANTS.SCROLL_HIDE_DELTA && currentScrollY > NAVIGATION_CONSTANTS.SCROLL_THRESHOLD) {
            this.hideNavigation(navigationElement);
        } else if (scrollDelta < NAVIGATION_CONSTANTS.SCROLL_SHOW_DELTA) {
            this.showNavigation(navigationElement);
        }

        // Update scrolled state for background styling
        if (currentScrollY > 50) {
            navigationElement.classList.add('navigation--scrolled');
            this.navigationState.hasScrolled = true;
        } else {
            navigationElement.classList.remove('navigation--scrolled');
            this.navigationState.hasScrolled = false;
        }

        this.navigationState.lastScrollPosition = currentScrollY;
    }

    /**
     * @brief Hides navigation with animation
     * @private
     * @param {HTMLElement} navigationElement - The navigation container element
     */
    hideNavigation(navigationElement) {
        if (!this.navigationState.isNavigationVisible) return;

        navigationElement.classList.add('navigation--hidden');
        this.navigationState.isNavigationVisible = false;

        this.notifyObservers('navigationHidden', {
            scrollPosition: window.scrollY
        });
    }

    /**
     * @brief Shows navigation with animation
     * @private
     * @param {HTMLElement} navigationElement - The navigation container element
     */
    showNavigation(navigationElement) {
        if (this.navigationState.isNavigationVisible) return;

        navigationElement.classList.remove('navigation--hidden');
        this.navigationState.isNavigationVisible = true;

        this.notifyObservers('navigationShown', {
            scrollPosition: window.scrollY
        });
    }

    /**
     * @brief Sets up click handlers for navigation links
     * @private
     * @param {HTMLElement} navigationElement - The navigation container element
     * @returns {Promise<void>} Resolves when click handlers are set up
     */
    async setupNavigationClickHandlers(navigationElement) {
        const navigationLinks = navigationElement.querySelectorAll('.navigation-link');
        
        navigationLinks.forEach(link => {
            link.addEventListener('click', (event) => {
                this.handleNavigationClick(event, link);
            }, { signal: this.eventAbortController.signal });
        });

        console.debug('NavigationView: Click handlers initialized.');
    }

    /**
     * @brief Handles navigation link click events
     * @private
     * @param {MouseEvent} event - Click event object
     * @param {HTMLElement} linkElement - The clicked navigation link element
     */
    handleNavigationClick(event, linkElement) {
        event.preventDefault();

        const targetPath = linkElement.getAttribute('href');
        const linkLabel = linkElement.querySelector('.navigation-link-text')?.textContent || 'Unknown';

        // Notify observers of navigation intent
        this.notifyObservers('navigationRequested', {
            targetPath,
            linkLabel,
            isExternal: linkElement.getAttribute('target') === '_blank',
            event: 'click'
        });

        console.debug(`NavigationView: Navigation requested to: ${targetPath}`);
    }

    /**
     * @brief Triggers a random flashback, navigating to a random section
     * @private
     */
    triggerFlashback() {
        const sections = Array.from(document.querySelectorAll("[data-section]"));
        if (sections.length === 0) {
            console.warn('NavigationView: No sections found for flashback navigation');
            return;
        }

        const randomSection = sections[Math.floor(Math.random() * sections.length)];
        const sectionId = randomSection.id;

        // Notify observers of flashback trigger
        this.notifyObservers("flashbackTriggered", { 
            sectionId,
            sectionElement: randomSection,
            totalSections: sections.length
        });

        console.debug(`NavigationView: Flashback triggered to section: ${sectionId}`);
    }

    /**
     * @brief Updates navigation state based on current route
     * @public
     * @param {string} currentPath - The current active path for highlighting
     */
    updateNavigationState(currentPath) {
        if (!currentPath || typeof currentPath !== 'string') {
            console.warn('NavigationView: Invalid current path provided for state update');
            return;
        }

        this.navigationState.currentPath = currentPath;
        this.updateActiveNavigationLinks(currentPath);

        this.notifyObservers('navigationStateUpdated', {
            currentPath,
            previousPath: this.navigationState.currentPath
        });

        console.debug(`NavigationView: Navigation state updated to: ${currentPath}`);
    }

    /**
     * @brief Updates active state of navigation links
     * @private
     * @param {string} currentPath - The current active path for highlighting
     */
    updateActiveNavigationLinks(currentPath) {
        const navigationLinks = this.containerElement.querySelectorAll('.navigation-link');
        
        navigationLinks.forEach(link => {
            const linkPath = link.getAttribute('href');
            const isActive = linkPath === currentPath;

            // Update visual and accessibility state
            link.classList.toggle('navigation-link--active', isActive);
            
            if (isActive) {
                link.setAttribute('aria-current', 'page');
                link.setAttribute('tabindex', '0');
            } else {
                link.removeAttribute('aria-current');
                link.removeAttribute('tabindex');
            }
        });
    }

    /**
     * @brief Sets the active section in navigation
     * @public
     * @param {string} sectionId - The section ID to set as active
     */
    setActiveSection(sectionId) {
        this.updateNavigationState(`#${sectionId}`);
    }

    /**
     * @brief Adds an observer for navigation state changes
     * @public
     * @param {Function} callback - Callback function to be notified of changes
     * @param {Object} options - Observer options
     * @param {AbortSignal} options.signal - Abort signal for removing observer
     */
    addObserver(callback, options = {}) {
        if (typeof callback !== 'function') {
            throw new Error('NavigationView: Observer callback must be a function');
        }

        this.observers.push(callback);

        // Auto-remove observer when signal is aborted
        if (options.signal) {
            options.signal.addEventListener('abort', () => {
                this.removeObserver(callback);
            });
        }

        console.debug('NavigationView: Observer added.');
    }

    /**
     * @brief Removes an observer from notification list
     * @public
     * @param {Function} callback - Callback function to remove
     */
    removeObserver(callback) {
        const observerIndex = this.observers.indexOf(callback);
        if (observerIndex > -1) {
            this.observers.splice(observerIndex, 1);
            console.debug('NavigationView: Observer removed.');
        }
    }

    /**
     * @brief Notifies all observers of state changes
     * @private
     * @param {string} eventType - Type of event that occurred
     * @param {Object} eventData - Data associated with the event
     */
    notifyObservers(eventType, eventData = {}) {
        this.observers.forEach(observer => {
            try {
                observer(eventType, {
                    ...eventData,
                    timestamp: Date.now(),
                    source: 'NavigationView'
                });
            } catch (error) {
                console.error('NavigationView: Observer error:', error);
            }
        });
    }

    /**
     * @brief Gets current navigation state
     * @public
     * @returns {Object} Current navigation state object
     */
    getNavigationState() {
        return { ...this.navigationState };
    }

    /**
     * @brief Checks if navigation is initialized
     * @public
     * @returns {boolean} True if navigation is initialized and ready
     */
    isNavigationInitialized() {
        return this.isInitialized;
    }

    /**
     * @brief Gets navigation configuration
     * @public
     * @returns {Array} Navigation configuration array
     */
    getNavigationConfig() {
        return [...NAVIGATION_CONFIG];
    }

    /**
     * @brief Cleans up resources and event listeners
     * @public
     */
    destroy() {
        // Abort all event listeners
        this.eventAbortController.abort();

        // Clear observers
        this.observers = [];

        // Reset body scroll lock
        document.body.style.overflow = '';
        document.body.removeAttribute('data-mobile-menu-open');

        this.isInitialized = false;

        console.info('NavigationView: Navigation destroyed and resources cleaned up.');
    }
}

export default NavigationView;