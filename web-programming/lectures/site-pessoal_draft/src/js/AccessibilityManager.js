/**
 * @file AccessibilityManager.js
 * @brief Comprehensive accessibility enhancements and screen reader support
 * @description Manages accessibility features, screen reader announcements, and keyboard navigation
 */

class AccessibilityManager {
    /**
     * @brief Creates a new AccessibilityManager instance
     * @constructor
     * @param {Object} configuration - Accessibility configuration options
     */
    constructor(configuration = {}) {
        /**
         * @private
         * @type {Object}
         * @description Current accessibility settings state
         */
        this.settings = {
            reducedMotion: false,
            highContrast: false,
            fontSizeMultiplier: 1.0,
            screenReaderEnabled: false,
            ...configuration.defaultSettings
        };

        /**
         * @private
         * @type {HTMLElement|null}
         * @description Live region element for screen reader announcements
         */
        this.liveRegion = null;

        /**
         * @private
         * @type {boolean}
         * @description Tracks initialization status
         */
        this.isInitialized = false;

        this.initialize = this.initialize.bind(this);
        this.detectAccessibilityPreferences = this.detectAccessibilityPreferences.bind(this);
    }

    /**
     * @brief Initializes accessibility manager and sets up observers
     * @method initialize
     * @returns {Promise<void>}
     */
    async initialize() {
        try {
            // Create live region for screen reader announcements
            this.createLiveRegion();
            
            // Detect user accessibility preferences
            await this.detectAccessibilityPreferences();
            
            // Apply initial accessibility settings
            this.applyAccessibilitySettings();
            
            // Set up event listeners for keyboard navigation
            this.setupKeyboardNavigation();
            
            // Set up mutation observer for dynamic content
            this.setupMutationObserver();
            
            this.isInitialized = true;
            console.info('AccessibilityManager initialized successfully');
        } catch (error) {
            console.error('AccessibilityManager initialization failed:', error);
        }
    }

    /**
     * @brief Creates ARIA live region for screen reader announcements
     * @method createLiveRegion
     * @private
     */
    createLiveRegion() {
        this.liveRegion = document.createElement('div');
        this.liveRegion.setAttribute('aria-live', 'polite');
        this.liveRegion.setAttribute('aria-atomic', 'true');
        this.liveRegion.setAttribute('class', 'sr-only');
        this.liveRegion.style.cssText = `
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        `;
        
        document.body.appendChild(this.liveRegion);
    }

    /**
     * @brief Detects user system accessibility preferences
     * @method detectAccessibilityPreferences
     * @returns {Promise<void>}
     * @private
     */
    async detectAccessibilityPreferences() {
        if (typeof window === 'undefined' || !window.matchMedia) return;

        // Detect reduced motion preference
        this.settings.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        
        // Detect contrast preference
        this.settings.highContrast = window.matchMedia('(prefers-contrast: high)').matches;
        
        // Load saved accessibility settings
        const savedSettings = localStorage.getItem('accessibility-settings');
        if (savedSettings) {
            try {
                const parsedSettings = JSON.parse(savedSettings);
                this.settings = { ...this.settings, ...parsedSettings };
            } catch (error) {
                console.warn('Failed to parse saved accessibility settings');
            }
        }
    }

    /**
     * @brief Applies current accessibility settings to document
     * @method applyAccessibilitySettings
     * @private
     */
    applyAccessibilitySettings() {
        const rootElement = document.documentElement;
        
        // Apply reduced motion
        if (this.settings.reducedMotion) {
            rootElement.style.setProperty('--animation-duration', '0.01ms');
            rootElement.classList.add('reduced-motion');
        } else {
            rootElement.style.removeProperty('--animation-duration');
            rootElement.classList.remove('reduced-motion');
        }
        
        // Apply high contrast
        if (this.settings.highContrast) {
            rootElement.classList.add('high-contrast');
        } else {
            rootElement.classList.remove('high-contrast');
        }
        
        // Apply font size scaling
        rootElement.style.setProperty('--font-size-multiplier', this.settings.fontSizeMultiplier.toString());
        
        // Persist settings
        this.persistSettings();
        
        // Dispatch settings changed event
        this.dispatchAccessibilityEvent('accessibility:changed', this.settings);
    }

    /**
     * @brief Sets up comprehensive keyboard navigation
     * @method setupKeyboardNavigation
     * @private
     */
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (event) => {
            // Skip if inside form element
            if (['INPUT', 'TEXTAREA', 'SELECT'].includes(event.target.tagName)) {
                return;
            }

            switch (event.key) {
                case 'Tab':
                    this.handleTabNavigation(event);
                    break;
                case 'Escape':
                    this.handleEscapeKey(event);
                    break;
                case 'Enter':
                    this.handleEnterKey(event);
                    break;
            }
        });
    }

    /**
     * @brief Handles tab navigation for keyboard users
     * @method handleTabNavigation
     * @param {KeyboardEvent} event - Keyboard event
     * @private
     */
    handleTabNavigation(event) {
        // Add visual indicator for keyboard navigation
        document.documentElement.classList.add('keyboard-navigation');
    }

    /**
     * @brief Sets up mutation observer for dynamic content accessibility
     * @method setupMutationObserver
     * @private
     */
    setupMutationObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.enhanceElementAccessibility(node);
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
     * @brief Enhances accessibility of dynamically added elements
     * @method enhanceElementAccessibility
     * @param {Element} element - Element to enhance
     * @private
     */
    enhanceElementAccessibility(element) {
        // Add ARIA labels to interactive elements missing them
        if (element.hasAttribute('role') || ['BUTTON', 'A', 'INPUT'].includes(element.tagName)) {
            if (!element.hasAttribute('aria-label') && !element.textContent.trim()) {
                const label = this.generateAccessibleLabel(element);
                if (label) {
                    element.setAttribute('aria-label', label);
                }
            }
        }

        // Ensure focus management for modal elements
        if (element.hasAttribute('role') && ['dialog', 'modal'].includes(element.getAttribute('role'))) {
            element.setAttribute('tabindex', '-1');
        }
    }

    /**
     * @brief Announces message to screen readers
     * @method announceToScreenReader
     * @param {string} message - Message to announce
     * @param {string} priority - Announcement priority ('polite' or 'assertive')
     * @returns {void}
     */
    announceToScreenReader(message, priority = 'polite') {
        if (!this.liveRegion) {
            console.warn('Live region not initialized for screen reader announcement');
            return;
        }

        this.liveRegion.setAttribute('aria-live', priority);
        this.liveRegion.textContent = message;
        
        // Clear message after announcement
        setTimeout(() => {
            if (this.liveRegion.textContent === message) {
                this.liveRegion.textContent = '';
            }
        }, 1000);
    }

    /**
     * @brief Announces view changes for screen reader users
     * @method announceViewChange
     * @param {string} viewName - Name of the view being loaded
     * @returns {void}
     */
    announceViewChange(viewName) {
        const message = `Loaded ${viewName} view`;
        this.announceToScreenReader(message, 'polite');
    }

    /**
     * @brief Updates accessibility setting
     * @method updateSetting
     * @param {string} setting - Setting name to update
     * @param {any} value - New setting value
     * @returns {void}
     */
    updateSetting(setting, value) {
        if (this.settings.hasOwnProperty(setting)) {
            this.settings[setting] = value;
            this.applyAccessibilitySettings();
            console.info(`Accessibility setting "${setting}" updated to:`, value);
        } else {
            console.warn(`Accessibility setting "${setting}" not found`);
        }
    }

    /**
     * @brief Persists accessibility settings to storage
     * @method persistSettings
     * @private
     */
    persistSettings() {
        try {
            localStorage.setItem('accessibility-settings', JSON.stringify(this.settings));
        } catch (error) {
            console.warn('Failed to persist accessibility settings:', error);
        }
    }

    /**
     * @brief Dispatches accessibility events
     * @method dispatchAccessibilityEvent
     * @param {string} eventName - Name of event to dispatch
     * @param {Object} eventDetail - Event detail data
     * @private
     */
    dispatchAccessibilityEvent(eventName, eventDetail) {
        const accessibilityEvent = new CustomEvent(eventName, {
            detail: {
                ...eventDetail,
                timestamp: Date.now()
            },
            bubbles: true
        });
        
        window.dispatchEvent(accessibilityEvent);
    }

    /**
     * @brief Gets current accessibility settings
     * @method getSettings
     * @returns {Object} Current accessibility settings
     */
    getSettings() {
        return { ...this.settings };
    }

    /**
     * @brief Cleans up accessibility manager resources
     * @method destroy
     * @returns {void}
     */
    destroy() {
        if (this.liveRegion && this.liveRegion.parentNode) {
            this.liveRegion.parentNode.removeChild(this.liveRegion);
        }
        
        this.isInitialized = false;
        console.info('AccessibilityManager destroyed successfully');
    }
}

export default AccessibilityManager;