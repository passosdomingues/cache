import eventBus from '../core/EventBus.js';

/**
 * @brief Base view class for all views
 * @description Provides common functionality and lifecycle methods for views
 */
export class BaseView {
    /**
     * @brief Constructs a BaseView instance.
     * @param {Object} config - The configuration object.
     * @param {HTMLElement} [config.container] - The main DOM container for the view.
     * @param {Object} [config.eventBus] - The event bus instance for communication.
     */
    constructor(config = {}) {
        this.container = config.container;
        this.eventBus = config.eventBus || eventBus;
        this.isRendered = false;
        this.isDestroyed = false;
        
        this.elements = new Map();
        this.eventHandlers = new Map();
    }

    /**
     * @brief Initialize the view.
     * @description Called before the first render, sets up initial state.
     * @returns {Promise<void>}
     */
    async init() {
        if (this.isDestroyed) {
            throw new Error('BaseView: Cannot initialize a destroyed view.');
        }
        
        console.info(`BaseView: Initializing ${this.constructor.name}`);
    }

    /**
     * @brief Render the view.
     * @description Main render method to be implemented by subclasses.
     * @returns {Promise<void>}
     */
    async render() {
        if (this.isDestroyed) {
            throw new Error('BaseView: Cannot render a destroyed view.');
        }
        
        this.isRendered = true;
        console.info(`BaseView: Rendered ${this.constructor.name}`);
    }

    /**
     * @brief Update the view.
     * @description Updates the view with new data.
     * @param {Object} data - The data for the update.
     * @returns {Promise<void>}
     */
    async update(data) {
        if (!this.isRendered || this.isDestroyed) {
            console.warn(`BaseView: Cannot update ${this.constructor.name} - not rendered or is destroyed.`);
            return;
        }
        
        console.info(`BaseView: Updated ${this.constructor.name}`, data);
    }

    /**
     * @brief Register a DOM element for easy access.
     * @param {string} key - The identifier for the element.
     * @param {HTMLElement} element - The DOM element to register.
     */
    registerElement(key, element) {
        this.elements.set(key, element);
    }

    /**
     * @brief Get a registered DOM element.
     * @param {string} key - The identifier for the element.
     * @returns {HTMLElement|undefined} The registered element or undefined if not found.
     */
    getElement(key) {
        return this.elements.get(key);
    }

    /**
     * @brief Add an event listener to an element and track it for cleanup.
     * @param {HTMLElement|string} element - The element or its registered key.
     * @param {string} event - The event type (e.g., 'click').
     * @param {Function} handler - The event handler function.
     * @param {Object} [options={}] - The event listener options.
     */
    addEventListener(element, event, handler, options = {}) {
        const actualElement = typeof element === 'string' ? this.getElement(element) : element;
        
        if (!actualElement) {
            console.warn(`BaseView: Element not found for event listener: ${element}`);
            return;
        }
        
        actualElement.addEventListener(event, handler, options);
        
        // Store for cleanup
        const handlerKey = `${typeof element === 'string' ? element : 'direct'}_${event}`;
        if (!this.eventHandlers.has(handlerKey)) {
            this.eventHandlers.set(handlerKey, []);
        }
        this.eventHandlers.get(handlerKey).push({ element: actualElement, handler, options });
    }

    /**
     * @brief Remove a specific event listener from an element.
     * @param {HTMLElement|string} element - The element or its registered key.
     * @param {string} event - The event type.
     * @param {Function} handler - The handler function to remove.
     */
    removeEventListener(element, event, handler) {
        const actualElement = typeof element === 'string' ? this.getElement(element) : element;
        
        if (actualElement) {
            actualElement.removeEventListener(event, handler);
        }
    }

    /**
     * @brief Show the view.
     * @description Makes the view's container visible.
     */
    show() {
        if (this.container) {
            this.container.style.display = '';
            this.container.style.visibility = 'visible';
        }
        
        this.eventBus.publish('view:shown', { view: this.constructor.name });
    }

    /**
     * @brief Hide the view.
     * @description Hides the view's container.
     */
    hide() {
        if (this.container) {
            this.container.style.display = 'none';
        }
        
        this.eventBus.publish('view:hidden', { view: this.constructor.name });
    }

    /**
     * @brief Create a DOM element with specified attributes and content.
     * @param {string} tag - The HTML tag name (e.g., 'div').
     * @param {Object} [attributes={}] - An object of element attributes.
     * @param {string} [textContent=''] - The text content for the element.
     * @returns {HTMLElement} The created DOM element.
     */
    createElement(tag, attributes = {}, textContent = '') {
        const element = document.createElement(tag);
        
        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'className') {
                element.className = value;
            } else if (key === 'dataset') {
                Object.entries(value).forEach(([dataKey, dataValue]) => {
                    element.dataset[dataKey] = dataValue;
                });
            } else if (key.startsWith('on') && typeof value === 'function') {
                const eventName = key.substring(2).toLowerCase();
                element.addEventListener(eventName, value);
            } else {
                element.setAttribute(key, value);
            }
        });
        
        if (textContent) {
            element.textContent = textContent;
        }
        
        return element;
    }

    /**
     * @brief Escape HTML to prevent XSS vulnerabilities.
     * @param {string} text - The text to escape.
     * @returns {string} The escaped HTML string.
     */
    escapeHtml(text) {
        if (!text) return '';
        
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * @brief Add a CSS class to an element.
     * @param {HTMLElement|string} element - The element or its registered key.
     * @param {string} className - The CSS class to add.
     */
    addClass(element, className) {
        const actualElement = typeof element === 'string' ? this.getElement(element) : element;
        if (actualElement) {
            actualElement.classList.add(className);
        }
    }

    /**
     * @brief Remove a CSS class from an element.
     * @param {HTMLElement|string} element - The element or its registered key.
     * @param {string} className - The CSS class to remove.
     */
    removeClass(element, className) {
        const actualElement = typeof element === 'string' ? this.getElement(element) : element;
        if (actualElement) {
            actualElement.classList.remove(className);
        }
    }

    /**
     * @brief Toggle a CSS class on an element.
     * @param {HTMLElement|string} element - The element or its registered key.
     * @param {string} className - The CSS class to toggle.
     */
    toggleClass(element, className) {
        const actualElement = typeof element === 'string' ? this.getElement(element) : element;
        if (actualElement) {
            actualElement.classList.toggle(className);
        }
    }

    /**
     * @brief Set the text content of an element safely.
     * @param {HTMLElement|string} element - The element or its registered key.
     * @param {string} text - The text content to set.
     */
    setText(element, text) {
        const actualElement = typeof element === 'string' ? this.getElement(element) : element;
        if (actualElement) {
            actualElement.textContent = text; // textContent automatically escapes HTML
        }
    }

    /**
     * @brief Set the inner HTML of an element.
     * @param {HTMLElement|string} element - The element or its registered key.
     * @param {string} html - The HTML string to set. Use with caution.
     */
    setHTML(element, html) {
        const actualElement = typeof element === 'string' ? this.getElement(element) : element;
        if (actualElement) {
            actualElement.innerHTML = html;
        }
    }

    /**
     * @brief Destroy the view and clean up resources.
     * @description Removes all registered event listeners and clears element references.
     */
    destroy() {
        if (this.isDestroyed) return;

        // Remove all tracked event listeners
        this.eventHandlers.forEach((handlers) => {
            handlers.forEach(({ element, handler, options }) => {
                const eventName = [...element.getAttributeNames()].find(attr => attr.startsWith('on'))?.substring(2);
                if (eventName) {
                    element.removeEventListener(eventName, handler, options);
                }
            });
        });
        
        this.eventHandlers.clear();
        this.elements.clear();
        
        this.isRendered = false;
        this.isDestroyed = true;
        
        console.info(`BaseView: Destroyed ${this.constructor.name}`);
    }
}