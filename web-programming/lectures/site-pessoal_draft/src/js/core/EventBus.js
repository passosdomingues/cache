/**
 * @brief Global event bus for component communication
 * @description Implements publish-subscribe pattern for loose coupling between MVC components
 */
export class EventBus {
    constructor() {
        this.events = new Map();
    }

    /**
     * @brief Subscribe to an event
     * @param {string} eventName - Name of the event to subscribe to
     * @param {Function} callback - Function to call when event is published
     * @returns {Function} Unsubscribe function
     */
    subscribe(eventName, callback) {
        if (!this.events.has(eventName)) {
            this.events.set(eventName, new Set());
        }
        
        const eventSet = this.events.get(eventName);
        eventSet.add(callback);

        return () => this.unsubscribe(eventName, callback);
    }

    /**
     * @brief Unsubscribe from an event
     * @param {string} eventName - Name of the event to unsubscribe from
     * @param {Function} callback - Callback function to remove
     */
    unsubscribe(eventName, callback) {
        if (this.events.has(eventName)) {
            const eventSet = this.events.get(eventName);
            eventSet.delete(callback);
        }
    }

    /**
     * @brief Publish an event with data
     * @param {string} eventName - Name of the event to publish
     * @param {*} data - Data to pass to subscribers
     */
    publish(eventName, data = null) {
        if (this.events.has(eventName)) {
            const eventSet = this.events.get(eventName);
            eventSet.forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in event handler for ${eventName}:`, error);
                }
            });
        }
    }

    /**
     * @brief Clear all events or specific event subscribers
     * @param {string} [eventName] - Optional event name to clear
     */
    clear(eventName = null) {
        if (eventName) {
            this.events.delete(eventName);
        } else {
            this.events.clear();
        }
    }
}

// Singleton instance (exportado como padrão)
export default new EventBus();