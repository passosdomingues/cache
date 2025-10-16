import eventBus from '../core/EventBus.js';

/**
 * @brief Accessibility manager service
 * @description Handles accessibility features and keyboard navigation
 */
class AccessibilityManager {
    constructor(dependencies = {}) {
        this.eventBus = dependencies.eventBus || eventBus;
        this.isInitialized = false;
        this.focusTrapped = false;
        this.focusableElements = [];
        this.currentFocusIndex = 0;
        this.trapContainer = null;
        this.observer = null;
        this.fontSize = 100; // percent
        
        this.announce = this.announce.bind(this);
        this.handleKeydown = this.handleKeydown.bind(this);
        this.handleFocusIn = this.handleFocusIn.bind(this);
        
        // Configuração padrão para elementos focáveis
        this.focusableSelectors = [
            'a[href]',
            'button:not([disabled])',
            'input:not([disabled])',
            'textarea:not([disabled])',
            'select:not([disabled])',
            '[tabindex]:not([tabindex="-1"])',
            '[contenteditable="true"]',
            'details',
            'details summary'
        ];
    }

    /**
     * @brief Initialize accessibility manager
     */
    async init() {
        if (this.isInitialized) {
            console.warn('AccessibilityManager: Already initialized');
            return;
        }

        try {
            this.setupEventListeners();
            this.setupFocusManagement();
            this.createAnnouncer();
            this.announcePageLoad();
            this.setupSkipLinks();
            this.loadPreferences();
            
            this.isInitialized = true;
            console.info('AccessibilityManager: Initialized successfully');
        } catch (error) {
            console.error('AccessibilityManager: Initialization failed', error);
            throw error;
        }
    }

    /**
     * @brief Set up event listeners
     */
    setupEventListeners() {
        document.addEventListener('keydown', this.handleKeydown);
        document.addEventListener('focusin', this.handleFocusIn);
        
        // EventBus subscriptions
        this.eventBus.subscribe('accessibility:announce', this.announce);
        this.eventBus.subscribe('accessibility:trapFocus', this.trapFocus.bind(this));
        this.eventBus.subscribe('accessibility:releaseFocus', this.releaseFocus.bind(this));
        this.eventBus.subscribe('accessibility:focusElement', this.focusElement.bind(this));

        this.setupMutationObserver();
    }

    /**
     * @brief Set up MutationObserver to watch for DOM changes
     */
    setupMutationObserver() {
        this.observer = new MutationObserver((mutations) => {
            let shouldUpdateFocusable = false;

            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            if (this.isFocusable(node) || node.querySelector(this.focusableSelectors.join(','))) {
                                shouldUpdateFocusable = true;
                            }
                        }
                    });

                    mutation.removedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE && this.focusableElements.includes(node)) {
                            shouldUpdateFocusable = true;
                        }
                    });
                }
            });

            if (shouldUpdateFocusable) {
                this.updateFocusableElements();
            }
        });

        this.observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['disabled', 'tabindex', 'style', 'class']
        });
    }

    /**
     * @brief Set up focus management
     */
    setupFocusManagement() {
        this.updateFocusableElements();
        
        // Garante que o foco seja visível para usuários de teclado
        if (!document.getElementById('a11y-focus-styles')) {
            const style = document.createElement('style');
            style.id = 'a11y-focus-styles';
            style.textContent = `
                :focus {
                    outline: 2px solid #4A90E2 !important;
                    outline-offset: 2px !important;
                }
                
                .sr-only {
                    position: absolute !important;
                    width: 1px !important;
                    height: 1px !important;
                    padding: 0 !important;
                    margin: -1px !important;
                    overflow: hidden !important;
                    clip: rect(0, 0, 0, 0) !important;
                    white-space: nowrap !important;
                    border: 0 !important;
                }

                .skip-link {
                    position: absolute;
                    top: -40px;
                    left: 6px;
                    background: #4A90E2;
                    color: white;
                    padding: 8px 12px;
                    text-decoration: none;
                    border-radius: 4px;
                    z-index: 10000;
                    transition: top 0.3s ease;
                }

                .skip-link:focus {
                    top: 6px;
                    outline: 2px solid #FFFFFF !important;
                }
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * @brief Set up skip links for keyboard navigation
     */
    setupSkipLinks() {
        if (document.querySelector('.skip-links')) {
            return; // Skip links já existem
        }

        const skipLinks = document.createElement('nav');
        skipLinks.className = 'skip-links';
        skipLinks.setAttribute('aria-label', 'Skip navigation');
        
        const skipTargets = [
            { href: '#main-content', text: 'Skip to main content' },
            { href: '#navigation', text: 'Skip to navigation' },
            { href: '#footer', text: 'Skip to footer' }
        ];

        skipTargets.forEach(target => {
            const skipLink = document.createElement('a');
            skipLink.href = target.href;
            skipLink.className = 'skip-link sr-only';
            skipLink.textContent = target.text;
            skipLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.focusElement(target.href);
            });
            skipLinks.appendChild(skipLink);
        });

        document.body.insertBefore(skipLinks, document.body.firstChild);
    }

    /**
     * @brief Handle focus in events
     * @param {FocusEvent} event - Focus event
     */
    handleFocusIn(event) {
        // Atualiza elementos focáveis quando o foco muda
        this.updateFocusableElements();
        
        // Publica evento de mudança de foco
        this.eventBus.publish('accessibility:focusChanged', {
            element: event.target,
            previousElement: event.relatedTarget
        });
    }

    /**
     * @brief Handle keyboard events
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleKeydown(event) {
        const target = event.target;
        const tagName = target.tagName.toLowerCase();
        
        // Ignora eventos em inputs e textareas, exceto Escape
        if ((tagName === 'input' || tagName === 'textarea' || tagName === 'select') && event.key !== 'Escape') {
            return;
        }

        switch (event.key) {
            case 'Escape':
                this.handleEscape(event);
                break;
            case 'Tab':
                this.handleTab(event);
                break;
            case 'ArrowUp':
            case 'ArrowDown':
            case 'ArrowLeft':
            case 'ArrowRight':
                this.handleArrowKeys(event);
                break;
            case 'Enter':
                this.handleEnter(event);
                break;
            case ' ':
                this.handleSpace(event);
                break;
            case 'Home':
                this.handleHome(event);
                break;
            case 'End':
                this.handleEnd(event);
                break;
        }
    }

    /**
     * @brief Handle Escape key
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleEscape(event) {
        this.eventBus.publish('accessibility:escape', event);
        
        // Fecha modais ou menus abertos
        const activeModals = document.querySelectorAll('[role="dialog"][aria-modal="true"]');
        if (activeModals.length > 0) {
            const lastModal = activeModals[activeModals.length - 1];
            this.eventBus.publish('modal:close', { element: lastModal });
        }
    }

    /**
     * @brief Handle Tab key for focus trapping
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleTab(event) {
        if (!this.focusTrapped || this.focusableElements.length === 0) {
            this.eventBus.publish('accessibility:tab', event);
            return;
        }

        event.preventDefault();

        if (event.shiftKey) {
            this.currentFocusIndex--;
            if (this.currentFocusIndex < 0) {
                this.currentFocusIndex = this.focusableElements.length - 1;
            }
        } else {
            this.currentFocusIndex++;
            if (this.currentFocusIndex >= this.focusableElements.length) {
                this.currentFocusIndex = 0;
            }
        }

        const nextElement = this.focusableElements[this.currentFocusIndex];
        if (nextElement && typeof nextElement.focus === 'function') {
            nextElement.focus();
        }
    }

    /**
     * @brief Handle arrow keys for navigation
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleArrowKeys(event) {
        const target = event.target;
        const role = target.getAttribute('role');
        const isInListbox = target.closest('[role="listbox"]');
        
        // Navegação em menus, radiogroups, listbox, etc.
        if (role === 'menuitem' || role === 'tab' || role === 'radio' || isInListbox) {
            event.preventDefault();
            this.eventBus.publish('accessibility:arrowNavigation', {
                event,
                direction: event.key,
                element: target,
                role
            });
        }
    }

    /**
     * @brief Handle Enter key
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleEnter(event) {
        const target = event.target;
        const role = target.getAttribute('role');
        
        if (role === 'button' || target.tagName === 'BUTTON' || role === 'menuitem') {
            event.preventDefault();
            target.click();
        }
    }

    /**
     * @brief Handle Space key
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleSpace(event) {
        const target = event.target;
        const role = target.getAttribute('role');
        
        if (role === 'button' || target.tagName === 'BUTTON') {
            event.preventDefault();
            target.click();
        }
    }

    /**
     * @brief Handle Home key
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleHome(event) {
        if (this.focusTrapped && this.focusableElements.length > 0) {
            event.preventDefault();
            this.currentFocusIndex = 0;
            this.focusableElements[0]?.focus();
        }
    }

    /**
     * @brief Handle End key
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleEnd(event) {
        if (this.focusTrapped && this.focusableElements.length > 0) {
            event.preventDefault();
            this.currentFocusIndex = this.focusableElements.length - 1;
            this.focusableElements[this.currentFocusIndex]?.focus();
        }
    }

    /**
     * @brief Update list of focusable elements
     */
    updateFocusableElements() {
        const allFocusable = Array.from(document.querySelectorAll(this.focusableSelectors.join(',')));
        
        this.focusableElements = allFocusable.filter(element => {
            const isVisible = element.offsetWidth > 0 && 
                            element.offsetHeight > 0 && 
                            getComputedStyle(element).visibility !== 'hidden' &&
                            getComputedStyle(element).display !== 'none';
            
            const isEnabled = !element.hasAttribute('disabled');
            const isInViewport = this.isElementInViewport(element);
            
            return isVisible && isEnabled && isInViewport;
        });
        
        // Ordena por tabindex (elementos com tabindex > 0 primeiro, depois ordem natural)
        this.focusableElements.sort((a, b) => {
            const aIndex = parseInt(a.getAttribute('tabindex') || '0');
            const bIndex = parseInt(b.getAttribute('tabindex') || '0');
            
            if (aIndex > 0 && bIndex > 0) return aIndex - bIndex;
            if (aIndex > 0) return -1;
            if (bIndex > 0) return 1;
            return 0;
        });
    }

    /**
     * @brief Check if element is in viewport
     * @param {Element} element - Element to check
     * @returns {boolean} True if element is in viewport
     */
    isElementInViewport(element) {
        const rect = element.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }

    /**
     * @brief Check if element is focusable
     * @param {Element} element - Element to check
     * @returns {boolean} True if focusable
     */
    isFocusable(element) {
        return element.matches(this.focusableSelectors.join(','));
    }

    /**
     * @brief Trap focus within a specific element
     * @param {HTMLElement} container - Container element to trap focus in
     */
    trapFocus(container) {
        if (!container || !(container instanceof HTMLElement)) {
            console.warn('AccessibilityManager: Invalid container for focus trap');
            return;
        }

        this.focusTrapped = true;
        this.trapContainer = container;
        
        // Salva o elemento atualmente focado
        this.previouslyFocusedElement = document.activeElement;
        
        // Atualiza elementos focáveis apenas dentro do container
        this.focusableElements = Array.from(container.querySelectorAll(this.focusableSelectors.join(',')))
            .filter(element => {
                return element.offsetWidth > 0 && 
                       element.offsetHeight > 0 && 
                       !element.hasAttribute('disabled');
            });
        
        this.currentFocusIndex = 0;
        
        // Foca no primeiro elemento
        if (this.focusableElements.length > 0) {
            this.focusableElements[0].focus();
        } else {
            container.setAttribute('tabindex', '-1');
            container.focus();
        }

        this.announce('Focus trapped in dialog. Press Escape to close.');
    }

    /**
     * @brief Release focus trap
     */
    releaseFocus() {
        this.focusTrapped = false;
        
        // Restaura o foco para o elemento anterior
        if (this.previouslyFocusedElement && typeof this.previouslyFocusedElement.focus === 'function') {
            this.previouslyFocusedElement.focus();
        }
        
        this.trapContainer = null;
        this.previouslyFocusedElement = null;
        this.updateFocusableElements();
    }

    /**
     * @brief Focus on specific element
     * @param {string|HTMLElement} element - Element to focus (selector or element)
     */
    focusElement(element) {
        let target;
        
        if (typeof element === 'string') {
            // Remove o # do seletor se for um ID
            const selector = element.startsWith('#') ? element : `#${element}`;
            target = document.querySelector(selector);
        } else {
            target = element;
        }
        
        if (target && typeof target.focus === 'function') {
            target.focus();
            
            // Scroll para o elemento se necessário
            const scrollOptions = {
                behavior: 'smooth',
                block: 'nearest',
                inline: 'nearest'
            };
            target.scrollIntoView(scrollOptions);
            
            // Anuncia o foco para leitores de tela
            const label = target.getAttribute('aria-label') || 
                         target.textContent?.trim() || 
                         target.getAttribute('title') || 
                         'Element';
            this.announce(`Focused on ${label}`);
        } else {
            console.warn('AccessibilityManager: Could not focus element', element);
        }
    }

    /**
     * @brief Increase font size
     */
    increaseFontSize() {
        this.fontSize = Math.min(this.fontSize + 10, 150);
        this.applyFontSize();
        this.announce(`Font size increased to ${this.fontSize}%`);
    }

    /**
     * @brief Decrease font size
     */
    decreaseFontSize() {
        this.fontSize = Math.max(this.fontSize - 10, 80);
        this.applyFontSize();
        this.announce(`Font size decreased to ${this.fontSize}%`);
    }

    /**
     * @brief Apply current font size to document
     */
    applyFontSize() {
        document.documentElement.style.fontSize = `${this.fontSize}%`;
        localStorage.setItem('fontSize', this.fontSize);
    }

    /**
     * @brief Load saved preferences
     */
    loadPreferences() {
        // Load font size
        const savedFontSize = localStorage.getItem('fontSize');
        if (savedFontSize) {
            this.fontSize = parseInt(savedFontSize);
            this.applyFontSize();
        }

        // Load high contrast - NÃO aplicar por padrão, só se explicitamente salvo
        const highContrast = localStorage.getItem('highContrast');
        if (highContrast === 'true') {
            this.toggleHighContrast(true);
        }

        // Load reduced motion
        const reducedMotion = localStorage.getItem('reducedMotion');
        if (reducedMotion === 'true') {
            this.toggleReducedMotion(true);
        }
    }

    /**
     * @brief Announce a message to screen readers
     * @param {string} message - Message to announce
     * @param {string} priority - Priority: 'polite' or 'assertive'
     */
    announce(message, priority = 'polite') {
        if (!message || typeof message !== 'string') {
            console.warn('AccessibilityManager: Invalid announcement message');
            return;
        }

        let announcer = document.getElementById('a11y-announcer');
        if (!announcer) {
            announcer = this.createAnnouncer();
        }
        
        announcer.setAttribute('aria-live', priority);
        
        // Clear previous message
        announcer.textContent = '';
        
        // Use setTimeout to ensure the clear happens and the new message is announced
        setTimeout(() => {
            announcer.textContent = message;
            
            // Clear the message after a delay for repetitive announcements
            setTimeout(() => {
                if (announcer.textContent === message) {
                    announcer.textContent = '';
                }
            }, 3000);
        }, 100);
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
        announcer.setAttribute('aria-relevant', 'additions text');
        announcer.className = 'sr-only';
        document.body.appendChild(announcer);
        return announcer;
    }

    /**
     * @brief Announce page load
     */
    announcePageLoad() {
        const pageTitle = document.title || 'Page';
        const mainHeading = document.querySelector('h1, h2, [role="heading"]');
        const pageDescription = mainHeading ? mainHeading.textContent : 'content';
        
        this.announce(`${pageTitle} loaded. ${pageDescription}`, 'polite');
    }

    /**
     * @brief Set ARIA attributes on element
     * @param {HTMLElement} element - Target element
     * @param {Object} attributes - ARIA attributes to set
     */
    setAriaAttributes(element, attributes) {
        if (!element || !attributes) {
            console.warn('AccessibilityManager: Invalid element or attributes');
            return;
        }

        Object.keys(attributes).forEach(key => {
            if (attributes[key] === null || attributes[key] === false || attributes[key] === undefined) {
                element.removeAttribute(key);
            } else {
                element.setAttribute(key, String(attributes[key]));
            }
        });
    }

    /**
     * @brief Toggle ARIA expanded state
     * @param {HTMLElement} element - Target element
     * @param {boolean} isExpanded - Expanded state
     */
    toggleExpanded(element, isExpanded) {
        this.setAriaAttributes(element, {
            'aria-expanded': isExpanded
        });
    }

    /**
     * @brief Enable/disable high contrast mode
     * @param {boolean} enable - Whether to enable high contrast
     */
    toggleHighContrast(enable) {
        if (enable) {
            document.body.classList.add('high-contrast');
            this.announce('High contrast mode enabled');
        } else {
            document.body.classList.remove('high-contrast');
            this.announce('High contrast mode disabled');
        }
        
        // Salva a preferência
        localStorage.setItem('highContrast', enable);
    }

    /**
     * @brief Enable/disable reduced motion
     * @param {boolean} enable - Whether to enable reduced motion
     */
    toggleReducedMotion(enable) {
        if (enable) {
            document.body.classList.add('reduced-motion');
            this.announce('Reduced motion enabled');
        } else {
            document.body.classList.remove('reduced-motion');
            this.announce('Reduced motion disabled');
        }
        
        // Salva a preferência
        localStorage.setItem('reducedMotion', enable);
    }

    /**
     * @brief Get accessibility status
     * @returns {Object} Current accessibility settings
     */
    getStatus() {
        return {
            isInitialized: this.isInitialized,
            focusTrapped: this.focusTrapped,
            focusableElementsCount: this.focusableElements.length,
            fontSize: this.fontSize,
            highContrast: document.body.classList.contains('high-contrast'),
            reducedMotion: document.body.classList.contains('reduced-motion')
        };
    }

    /**
     * @brief Reset all accessibility settings to default
     */
    resetSettings() {
        this.fontSize = 100;
        this.applyFontSize();
        
        document.body.classList.remove('high-contrast');
        document.body.classList.remove('reduced-motion');
        
        localStorage.removeItem('fontSize');
        localStorage.removeItem('highContrast');
        localStorage.removeItem('reducedMotion');
        
        this.announce('All accessibility settings have been reset to default');
    }

    /**
     * @brief Destroy accessibility manager
     */
    destroy() {
        document.removeEventListener('keydown', this.handleKeydown);
        document.removeEventListener('focusin', this.handleFocusIn);
        
        // Remove EventBus subscriptions
        this.eventBus.unsubscribe('accessibility:announce', this.announce);
        this.eventBus.unsubscribe('accessibility:trapFocus', this.trapFocus);
        this.eventBus.unsubscribe('accessibility:releaseFocus', this.releaseFocus);
        this.eventBus.unsubscribe('accessibility:focusElement', this.focusElement);
        
        // Clear EventBus events
        this.eventBus.clear('accessibility:escape');
        this.eventBus.clear('accessibility:tab');
        this.eventBus.clear('accessibility:arrowNavigation');
        this.eventBus.clear('accessibility:focusChanged');
        
        // Disconnect observer
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }

        // Remove created elements
        const announcer = document.getElementById('a11y-announcer');
        if (announcer) {
            announcer.remove();
        }

        const skipLinks = document.querySelector('.skip-links');
        if (skipLinks) {
            skipLinks.remove();
        }

        const focusStyles = document.getElementById('a11y-focus-styles');
        if (focusStyles) {
            focusStyles.remove();
        }

        this.isInitialized = false;
        this.focusTrapped = false;
        this.focusableElements = [];
        this.currentFocusIndex = 0;
        this.trapContainer = null;
        
        console.info('AccessibilityManager: Destroyed successfully');
    }
}

export { AccessibilityManager };