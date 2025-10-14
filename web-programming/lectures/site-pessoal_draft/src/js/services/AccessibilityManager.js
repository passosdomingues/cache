import eventBus from '../core/EventBus.js';

/**
 * @brief Accessibility manager service
 * @description Handles accessibility features and keyboard navigation
 */
export class AccessibilityManager {
    constructor(dependencies = {}) {
        this.eventBus = dependencies.eventBus || eventBus;
        this.isInitialized = false;
        this.focusTrapped = false;

        this.handleKeydown = this.handleKeydown.bind(this);
    }

    /**
     * @brief Initialize accessibility manager
     */
    async init() {
        if (this.isInitialized) return;

        this.setupEventListeners();
        this.setupFocusManagement();
        this.announcePageLoad();
        
        this.isInitialized = true;
        console.info('AccessibilityManager: Initialized');
    }

    /**
     * @brief Set up event listeners
     */
    setupEventListeners() {
        document.addEventListener('keydown', this.handleKeydown);
        
        // Observe DOM changes for new interactive elements
        this.setupMutationObserver();
    }

    /**
     * @brief Handle keyboard events
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleKeydown(event) {
        // Skip keyboard handling if user is typing in an input
        if (event.target.tagName === 'INPUT' || event.target.tagName === 'TEXTAREA') {
            return;
        }

        switch (event.key) {
            case 'Escape':
                this.handleEscapeKey(event);
                break;
            case 'Tab':
                this.handleTabKey(event);
                break;
            case 'Enter':
            case ' ':
                this.handleActionKey(event);
                break;
        }
    }

    /**
     * @brief Handle escape key
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleEscapeKey(event) {
        // Close any open modals or menus
        this.eventBus.publish('accessibility:escape', { event });
    }

    /**
     * @brief Handle tab key for focus trapping
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleTabKey(event) {
        if (!this.focusTrapped) return;

        // Implement focus trapping logic for modals
        this.eventBus.publish('accessibility:tab', { event });
    }

    /**
     * @brief Handle action keys (Enter/Space)
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleActionKey(event) {
        // Ensure buttons and links can be activated with space/enter
        const element = event.target;
        if (element.tagName === 'BUTTON' || (element.tagName === 'A' && element.getAttribute('href'))) {
            event.preventDefault();
            element.click();
        }
    }

    /**
     * @brief Set up focus management
     */
    setupFocusManagement() {
        // Add skip link functionality
        this.setupSkipLinks();
        
        // Manage focus for dynamic content
        this.eventBus.subscribe('view:section:rendered', (data) => {
            this.manageFocusForNewContent(data.element);
        });
    }

    /**
     * @brief Set up skip links
     */
    setupSkipLinks() {
        const skipLink = document.querySelector('.skip-link');
        if (skipLink) {
            skipLink.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = skipLink.getAttribute('href')?.replace('#', '');
                const target = document.getElementById(targetId);
                if (target) {
                    target.setAttribute('tabindex', '-1');
                    target.focus();
                }
            });
        }
    }

    /**
     * @brief Manage focus for new content
     * @param {HTMLElement} element - Newly added element
     */
    manageFocusForNewContent(element) {
        // If the element is a heading or important content, focus it for screen readers
        if (element.querySelector('h1, h2, [role="main"]')) {
            element.setAttribute('tabindex', '-1');
            element.focus();
            
            // Announce to screen readers
            this.announceContent('New section loaded');
        }
    }

    /**
     * @brief Set up mutation observer for dynamic content
     */
    setupMutationObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // Element node
                        this.enhanceAccessibility(node);
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    /**
     * @brief Enhance accessibility of elements
     * @param {Element} element - Element to enhance
     */
    enhanceAccessibility(element) {
        // Add ARIA labels to interactive elements
        if (element.tagName === 'BUTTON' && !element.getAttribute('aria-label')) {
            const text = element.textContent.trim();
            if (text) {
                element.setAttribute('aria-label', text);
            }
        }

        // Ensure images have alt attributes
        if (element.tagName === 'IMG' && !element.getAttribute('alt')) {
            element.setAttribute('alt', 'Decorative image');
        }
    }

    /**
     * @brief Announce page load to screen readers
     */
    announcePageLoad() {
        this.announceContent('Page loaded successfully');
    }

    /**
     * @brief Announce content to screen readers
     * @param {string} message - Message to announce
     */
    announceContent(message) {
        const announcer = document.getElementById('a11y-announcer') || this.createAnnouncer();
        announcer.textContent = message;
    }

    /**
     * @brief Create ARIA live region announcer
     * @returns {HTMLElement} Announcer element
     */
    createAnnouncer() {
        const announcer = document.createElement('div');
        announcer.id = 'a11y-announcer';
        announcer.setAttribute('aria-live', 'polite');
        announcer.setAttribute('aria-atomic', 'true');
        announcer.style.cssText = `
            position: absolute;
            left: -10000px;
            width: 1px;
            height: 1px;
            overflow: hidden;
        `;
        document.body.appendChild(announcer);
        return announcer;
    }

    /**
     * @brief Enable focus trapping
     * @param {HTMLElement} container - Container to trap focus within
     */
    enableFocusTrap(container) {
        this.focusTrapped = true;
        this.eventBus.publish('accessibility:focus:trap:enabled', { container });
    }

    /**
     * @brief Disable focus trapping
     */
    disableFocusTrap() {
        this.focusTrapped = false;
        this.eventBus.publish('accessibility:focus:trap:disabled');
    }

    /**
     * @brief Destroy accessibility manager
     */
    destroy() {
        document.removeEventListener('keydown', this.handleKeydown);
        this.eventBus.clear('accessibility:escape');
        this.eventBus.clear('accessibility:tab');
        
        this.isInitialized = false;
        console.info('AccessibilityManager: Destroyed');
    }
}