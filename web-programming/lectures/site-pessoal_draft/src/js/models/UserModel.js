/**
 * @file UserModel.js
 * @author Rafael Passos Domingues
 * @brief Model responsible for managing user-specific data.
 * @description Consumes data from UserData.js to provide personal information,
 * contact details, and social links to the application.
 */

import eventBus from '../core/EventBus.js';
import { USER_DATA } from '../data/UserData.js';

/**
 * @class UserModel
 * @description Manages the user's personal and contact data.
 */
class UserModel {
    /**
     * @brief Constructs the UserModel instance.
     * @param {Object} [config={}] - The configuration object.
     * @param {Object} [config.eventBus] - The application's event bus.
     */
    constructor(config = {}) {
        this.eventBus = config.eventBus || eventBus;
        this.userData = {};
        this.isInitialized = false;
    }

    /**
     * @brief Initializes the model by loading the user data.
     * @returns {Promise<void>}
     */
    async init() {
        if (this.isInitialized) {
            console.warn('UserModel: Already initialized.');
            return;
        }
        console.info('UserModel: Initializing with user data...');
        this.userData = USER_DATA;
        this.isInitialized = true;
        this.eventBus.publish('user:loaded', { userName: this.userData.personalInfo.name });
        console.info('UserModel: Initialization complete.');
    }

    /**
     * @brief Retrieves the full user data object.
     * @returns {Object} The complete user data.
     */
    getUserData() {
        return this.userData;
    }
}

export { UserModel };