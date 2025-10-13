/**
 * @file NavigationController.js
 * @author Rafael Passos Domingues
 * @version 3.0.0
 * @brief Controller responsible for managing site navigation and scroll behavior.
 * @description Handles smooth scrolling between sections, URL hash updates,
 * active section detection, and communication with views through custom events.
 * Implements performance-optimized scroll handling and accessibility features.
 */

/**
 * @class NavigationController
 * @brief Manages navigation, scroll behavior, and section visibility tracking
 * @description Provides smooth scrolling, URL synchronization, active section
 * detection, and navigation state management with performance optimizations
 */
class NavigationController {
    /**
     * @brief Creates an instance of NavigationController
     * @constructor
     */
    constructor() {
        /**
         * @private
         * @type {string}
         * @brief Currently active section identifier
         */
        this.currentActiveSection = '';

        /**
         * @private
         * @type {number}
         * @brief Scroll offset to compensate for fixed header (in pixels)
         */
        this.scrollOffset = 100;

        /**
         * @private
         * @type {boolean}
         * @brief Flag to track if scroll handler is currently executing
         */
        this.isScrollHandlerRunning = false;

        /**
         * @private
         * @type {number|null}
         * @brief Timeout reference for scroll debouncing
         */
        this.scrollTimeoutId = null;

        /**
         * @private
         * @type {AbortController}
         * @brief Manages cleanup of event listeners
         */
        this.eventAbortController = new AbortController();

        /**
         * @private
         * @type {IntersectionObserver|null}
         * @brief Observer for section visibility detection
         */
        this.intersectionObserver = null;

        /**
         * @private
         * @type {Object}
         * @brief Configuration constants for navigation behavior
         */
        this.navigationConfig = {
            scrollBehavior: 'smooth',
            scrollDebounceDelay: 100,
            intersectionThreshold: 0.1,
            intersectionRootMargin: '-20% 0px -70% 0px'
        };

        // Bind methods to maintain context
        this.handleScroll = this.handleScroll.bind(this);
        this.handleHashChange = this.handleHashChange.bind(this);
        this.handleIntersectionUpdate = this.handleIntersectionUpdate.bind(this);
        this.handleFlashbackTriggered = this.handleFlashbackTriggered.bind(this);
    }

    /**
     * @brief Initializes the navigation controller and sets up global observers
     * @public
     * @returns {Promise<void>} Resolves when initialization is complete
     */
    async initialize() {
        try {
            await this.setupNavigationSystem();
            console.info('NavigationController: Successfully initialized navigation system.');
        } catch (error) {
            console.error('NavigationController: Failed to initialize:', error);
            throw error;
        }
    }

    /**
     * @brief Sets up the complete navigation system with all required observers
     * @private
     * @returns {Promise<void>} Resolves when all navigation systems are set up
     */
    async setupNavigationSystem() {
        this.setupScrollHandler();
        this.setupHashChangeHandler();
        this.setupIntersectionObserver();
        this.setupKeyboardNavigation();
    }

    /**
     * @brief Navigates to a specific section with smooth scrolling
     * @public
     * @param {string} targetSectionId - ID of the destination section
     * @param {Object} options - Navigation options
     * @param {boolean} options.updateUrl - Whether to update the URL hash
     * @param {boolean} options.smoothScroll - Whether to use smooth scrolling
     * @returns {Promise<void>} Resolves when navigation is complete
     */
    async navigateToSection(targetSectionId, options = {}) {
        const {
            updateUrl = true,
            smoothScroll = true
        } = options;

        if (!this.validateSectionId(targetSectionId)) {
            console.warn(`NavigationController: Invalid section ID provided: ${targetSectionId}`);
            return;
        }

        try {
            document.body.classList.add('flashback-active');
            setTimeout(() => {
                document.body.classList.remove('flashback-active');
            }, 300);

            await this.executeScrollToSection(targetSectionId, smoothScroll);
            
            if (updateUrl) {
                this.updateUrlHash(targetSectionId);
            }

            this.updateActiveSectionState(targetSectionId);
            this.highlightNavigationForSection(targetSectionId);
            
            console.debug(`NavigationController: Successfully navigated to section: ${targetSectionId}`);
            
        } catch (error) {
            console.error(`NavigationController: Failed to navigate to section ${targetSectionId}:`, error);
            throw error;
        }
    }

    /**
     * @brief Validates if a section ID is valid and exists in the DOM
     * @private
     * @param {string} sectionId - The section ID to validate
     * @returns {boolean} True if the section ID is valid and exists
     */
    validateSectionId(sectionId) {
        if (typeof sectionId !== 'string' || sectionId.trim() === '') {
            return false;
        }

        const targetElement = document.getElementById(sectionId);
        return targetElement !== null;
    }

    /**
     * @brief Executes smooth scroll to the target section
     * @private
     * @param {string} targetSectionId - ID of the section to scroll to
     * @param {boolean} useSmoothScroll - Whether to use smooth scrolling
     * @returns {Promise<void>} Resolves when scroll is complete
     */
    async executeScrollToSection(targetSectionId, useSmoothScroll = true) {
        const targetElement = document.getElementById(targetSectionId);
        
        if (!targetElement) {
            throw new Error(`Section element not found: ${targetSectionId}`);
        }

        const headerElement = document.querySelector('header');
        const headerHeight = headerElement ? headerElement.offsetHeight : 0;
        const targetScrollPosition = targetElement.offsetTop - headerHeight - this.scrollOffset;

        return new Promise((resolve) => {
            const scrollOptions = {
                top: targetScrollPosition,
                behavior: useSmoothScroll ? this.navigationConfig.scrollBehavior : 'auto'
            };

            const handleScrollEnd = () => {
                window.removeEventListener('scroll', handleScrollEnd);
                resolve();
            };

            window.addEventListener('scroll', handleScrollEnd, { 
                once: true,
                passive: true,
                signal: this.eventAbortController.signal
            });

            window.scrollTo(scrollOptions);

            // Fallback: resolve after a timeout in case scroll event doesn't fire
            setTimeout(resolve, 1000);
        });
    }

    /**
     * @brief Updates the URL hash without causing page reload
     * @private
     * @param {string} sectionId - The section ID to set in the URL hash
     */
    updateUrlHash(sectionId) {
        if (!sectionId) return;

        const currentHash = window.location.hash.slice(1);
        if (currentHash !== sectionId) {
            history.replaceState(null, '', `#${sectionId}`);
        }
    }

    /**
     * @brief Updates the internal state for the active section
     * @private
     * @param {string} sectionId - The newly active section ID
     */
    updateActiveSectionState(sectionId) {
        if (this.currentActiveSection !== sectionId) {
            const previousSectionId = this.currentActiveSection;
            this.currentActiveSection = sectionId;
            this.dispatchNavigationEvent('sectionChanged', { 
                sectionId,
                previousSectionId
            });
        }
    }

    /**
     * @brief Sets up optimized scroll handler for active section detection
     * @private
     * @description Uses requestAnimationFrame and debouncing for performance
     */
    setupScrollHandler() {
        const eventSignal = this.eventAbortController.signal;
        
        window.addEventListener('scroll', this.handleScroll, {
            passive: true,
            signal: eventSignal
        });
    }

    /**
     * @brief Handles scroll events with performance optimizations
     * @private
     */
    handleScroll() {
        if (this.isScrollHandlerRunning) return;

        this.isScrollHandlerRunning = true;

        // Debounce scroll events for performance
        if (this.scrollTimeoutId) {
            clearTimeout(this.scrollTimeoutId);
        }

        this.scrollTimeoutId = setTimeout(() => {
            requestAnimationFrame(() => {
                this.determineActiveSection();
                this.isScrollHandlerRunning = false;
            });
        }, this.navigationConfig.scrollDebounceDelay);
    }

    /**
     * @brief Determines the currently active section based on scroll position
     * @private
     */
    determineActiveSection() {
        const sections = document.querySelectorAll('[data-section]');
        const scrollPosition = window.scrollY + this.scrollOffset;

        let closestSection = null;
        let smallestDistance = Infinity;

        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionBottom = sectionTop + sectionHeight;

            // Calculate distance from current scroll position to section
            const distanceToTop = Math.abs(scrollPosition - sectionTop);
            const distanceToBottom = Math.abs(scrollPosition - sectionBottom);
            const minDistance = Math.min(distanceToTop, distanceToBottom);

            // Check if section is in viewport and closest
            if (scrollPosition >= sectionTop && scrollPosition <= sectionBottom) {
                closestSection = section.id;
                smallestDistance = 0;
            } else if (minDistance < smallestDistance) {
                smallestDistance = minDistance;
                closestSection = section.id;
            }
        });

        if (closestSection && closestSection !== this.currentActiveSection) {
            this.updateActiveSectionState(closestSection);
            this.highlightNavigationForSection(closestSection);
        }
    }

    /**
     * @brief Sets up intersection observer for more accurate section detection
     * @private
     */
    setupIntersectionObserver() {
        const observerOptions = {
            root: null,
            rootMargin: this.navigationConfig.intersectionRootMargin,
            threshold: this.navigationConfig.intersectionThreshold
        };

        this.intersectionObserver = new IntersectionObserver(
            this.handleIntersectionUpdate,
            observerOptions
        );

        // Observe all sections
        const sections = document.querySelectorAll('[data-section]');
        sections.forEach(section => {
            this.intersectionObserver.observe(section);
        });
    }

    /**
     * @brief Handles intersection observer updates for section visibility
     * @private
     * @param {IntersectionObserverEntry[]} entries - Intersection observer entries
     */
    handleIntersectionUpdate(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.id;
                this.dispatchNavigationEvent('sectionVisible', { 
                    sectionId,
                    intersectionRatio: entry.intersectionRatio 
                });
            }
        });
    }

    /**
     * @brief Sets up hash change handler for URL-based navigation
     * @private
     */
    setupHashChangeHandler() {
        const eventSignal = this.eventAbortController.signal;
        
        window.addEventListener('hashchange', this.handleHashChange, {
            signal: eventSignal
        });
    }

    /**
     * @brief Handles URL hash changes for navigation
     * @private
     */
    handleHashChange() {
        const sectionIdFromHash = window.location.hash.slice(1);
        
        if (sectionIdFromHash && sectionIdFromHash !== this.currentActiveSection) {
            this.navigateToSection(sectionIdFromHash, { 
                updateUrl: false,
                smoothScroll: true 
            });
        }
    }

    /**
     * @brief Sets up keyboard navigation for accessibility
     * @private
     */
    setupKeyboardNavigation() {
        const eventSignal = this.eventAbortController.signal;
        
        document.addEventListener('keydown', (event) => {
            this.handleKeyboardNavigation(event);
        }, { signal: eventSignal });
    }

    /**
     * @brief Handles keyboard navigation events
     * @private
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleKeyboardNavigation(event) {
        // Only handle navigation when user is not focused in form elements
        if (this.isUserInFormElement(event.target)) {
            return;
        }

        const navigationHandlers = {
            'ArrowUp': () => this.navigateToPreviousSection(),
            'ArrowDown': () => this.navigateToNextSection(),
            'Home': () => this.navigateToFirstSection(),
            'End': () => this.navigateToLastSection()
        };

        const handler = navigationHandlers[event.key];
        if (handler && !event.ctrlKey && !event.altKey && !event.metaKey) {
            event.preventDefault();
            handler();
        }
    }

    /**
     * @brief Checks if user is currently focused in a form element
     * @private
     * @param {Element} targetElement - The currently focused element
     * @returns {boolean} True if user is in a form element
     */
    isUserInFormElement(targetElement) {
        const formElements = ['INPUT', 'TEXTAREA', 'SELECT', 'BUTTON'];
        return formElements.includes(targetElement.tagName) || 
               targetElement.isContentEditable;
    }

    /**
     * @brief Navigates to the previous section
     * @private
     */
    navigateToPreviousSection() {
        const sections = Array.from(document.querySelectorAll('[data-section]'));
        const currentIndex = sections.findIndex(section => section.id === this.currentActiveSection);
        
        if (currentIndex > 0) {
            const previousSection = sections[currentIndex - 1];
            this.navigateToSection(previousSection.id);
        }
    }

    /**
     * @brief Navigates to the next section
     * @private
     */
    navigateToNextSection() {
        const sections = Array.from(document.querySelectorAll('[data-section]'));
        const currentIndex = sections.findIndex(section => section.id === this.currentActiveSection);
        
        if (currentIndex < sections.length - 1) {
            const nextSection = sections[currentIndex + 1];
            this.navigateToSection(nextSection.id);
        }
    }

    /**
     * @brief Navigates to the first section
     * @private
     */
    navigateToFirstSection() {
        const firstSection = document.querySelector('[data-section]');
        if (firstSection) {
            this.navigateToSection(firstSection.id);
        }
    }

    /**
     * @brief Navigates to the last section
     * @private
     */
    navigateToLastSection() {
        const sections = document.querySelectorAll('[data-section]');
        const lastSection = sections[sections.length - 1];
        if (lastSection) {
            this.navigateToSection(lastSection.id);
        }
    }

    /**
     * @brief Highlights the active section in the navigation menu
     * @public
     * @param {string} activeSectionId - ID of the active section to highlight
     */
    highlightNavigationForSection(activeSectionId) {
        if (!activeSectionId) return;

        const navigationLinks = document.querySelectorAll('[data-nav-link]');
        
        navigationLinks.forEach(link => {
            const linkSectionId = link.getAttribute('href')?.replace('#', '') || 
                                link.getAttribute('data-section');
            
            const isActive = linkSectionId === activeSectionId;
            
            // Update visual state
            link.classList.toggle('nav-link--active', isActive);
            link.setAttribute('aria-current', isActive ? 'location' : 'false');
            
            // Update accessibility attributes
            if (isActive) {
                link.setAttribute('tabindex', '0');
            } else {
                link.removeAttribute('tabindex');
            }
        });

        this.dispatchNavigationEvent('navigationHighlighted', { activeSectionId });
    }

    /**
     * @brief Dispatches custom navigation events for inter-component communication
     * @private
     * @param {string} eventType - Type of navigation event
     * @param {Object} eventDetail - Additional event data
     */
    dispatchNavigationEvent(eventType, eventDetail = {}) {
        const navigationEvent = new CustomEvent(`navigation:${eventType}`, {
            detail: {
                timestamp: Date.now(),
                controller: 'NavigationController',
                ...eventDetail
            },
            bubbles: true,
            cancelable: true
        });

        document.dispatchEvent(navigationEvent);
    }

    /**
     * @brief Handles the flashback triggered event from NavigationView.
     * @public
     * @param {Object} eventData - Data from the flashback event, including the sectionId.
     */
    handleFlashbackTriggered(eventData) {
        if (eventData && eventData.sectionId) {
            console.debug(`NavigationController: Flashback triggered to section: ${eventData.sectionId}`);
            this.navigateToSection(eventData.sectionId);
        } else {
            console.warn("NavigationController: Flashback triggered without a valid sectionId.");
        }
    }

    /**
     * @brief Registers an observer to listen for events from the NavigationView.
     * @public
     * @param {Object} navigationView - The NavigationView instance to observe.
     */
    registerNavigationViewObserver(navigationView) {
        if (navigationView && typeof navigationView.addObserver === 'function') {
            navigationView.addObserver('flashbackTriggered', this.handleFlashbackTriggered.bind(this));
            console.info("NavigationController: Registered as observer for 'flashbackTriggered' event.");
        } else {
            console.error("NavigationController: Invalid NavigationView instance provided for observer registration.");
        }
    }

    /**
     * @brief Gets the currently active section ID
     * @public
     * @returns {string} The current active section ID
     */
    getCurrentActiveSection() {
        return this.currentActiveSection;
    }

    /**
     * @brief Updates the scroll offset (useful for dynamic header heights)
     * @public
     * @param {number} newOffset - New scroll offset in pixels
     */
    updateScrollOffset(newOffset) {
        if (typeof newOffset === 'number' && newOffset >= 0) {
            this.scrollOffset = newOffset;
            console.debug(`NavigationController: Scroll offset updated to ${newOffset}px`);
        } else {
            console.warn('NavigationController: Invalid scroll offset provided');
        }
    }

    /**
     * @brief Cleans up resources and event listeners
     * @public
     * @description Properly tears down the controller to prevent memory leaks
     */
    destroy() {
        // Abort all event listeners
        this.eventAbortController.abort();

        // Disconnect intersection observer
        if (this.intersectionObserver) {
            this.intersectionObserver.disconnect();
            this.intersectionObserver = null;
        }

        // Clear any pending timeouts
        if (this.scrollTimeoutId) {
            clearTimeout(this.scrollTimeoutId);
            this.scrollTimeoutId = null;
        }

        this.currentActiveSection = '';
        this.isScrollHandlerRunning = false;

        console.info('NavigationController: Controller destroyed and resources cleaned up.');
    }
}

export default NavigationController;