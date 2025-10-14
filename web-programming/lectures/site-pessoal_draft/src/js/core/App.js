import eventBus from './EventBus.js';

/**
 * @brief Main application coordinator
 * @description Manages the application lifecycle, services, and controllers.
 */
class App {
    /**
     * @brief Constructs the App instance.
     * @param {Object} [config={}] - The application configuration object.
     * @param {Object} [config.services] - A map of service names to service classes.
     * @param {Object} [config.controllers] - A map of controller names to controller classes.
     */
    constructor(config = {}) {
        this.config = config;
        this.controllers = new Map();
        this.services = new Map();
        this.isInitialized = false;
        this.eventBus = eventBus;
    }

    /**
     * @brief Initialize the application.
     * @description Sets up all services and controllers in the proper order.
     * @returns {Promise<void>}
     */
    async initialize() {
        if (this.isInitialized) {
            console.warn('App: Application has already been initialized.');
            return;
        }

        try {
            console.info('App: Starting application initialization...');
            
            await this.initializeServices();
            await this.initializeControllers();
            await this.start();
            
            this.isInitialized = true;
            console.info('App: Application initialized successfully. 🎉');
            
        } catch (error) {
            console.error('App: Initialization failed:', error);
            this.eventBus.publish('app:error', { error });
            throw error;
        }
    }

    /**
     * @brief Initialize all registered services.
     * @returns {Promise<void>}
     */
    async initializeServices() {
        const services = this.config.services || {};
        
        for (const [serviceName, ServiceClass] of Object.entries(services)) {
            try {
                const serviceInstance = new ServiceClass({ eventBus: this.eventBus });
                this.services.set(serviceName, serviceInstance);
                
                if (typeof serviceInstance.init === 'function') {
                    await serviceInstance.init();
                }
                
                console.info(`App: Service '${serviceName}' initialized.`);
            } catch (error) {
                console.error(`App: Failed to initialize service '${serviceName}':`, error);
                throw error;
            }
        }
    }

    /**
     * @brief Initialize all registered controllers.
     * @returns {Promise<void>}
     */
    async initializeControllers() {
        const controllers = this.config.controllers || {};
        
        for (const [controllerName, ControllerClass] of Object.entries(controllers)) {
            try {
                const dependencies = this.buildControllerDependencies(controllerName);
                const controllerInstance = new ControllerClass(dependencies);
                this.controllers.set(controllerName, controllerInstance);
                
                if (typeof controllerInstance.init === 'function') {
                    await controllerInstance.init();
                }
                
                console.info(`App: Controller '${controllerName}' initialized.`);
            } catch (error) {
                console.error(`App: Failed to initialize controller '${controllerName}':`, error);
                throw error;
            }
        }
    }

    /**
     * @brief Build a dependency object for a specific controller.
     * @param {string} controllerName - The name of the controller.
     * @returns {Object} An object containing the dependencies for the controller.
     */
    buildControllerDependencies(controllerName) {
        const dependencies = {
            eventBus: this.eventBus,
            services: Object.fromEntries(this.services)
        };

        // Example of providing specific dependencies based on controller needs
        // You can expand this as your application grows.
        if (controllerName === 'mainController' || controllerName === 'navigationController') {
            dependencies.contentModel = this.services.get('contentModel');
        }

        return dependencies;
    }

    /**
     * @brief Start the application's main logic.
     * @returns {Promise<void>}
     */
    async start() {
        this.eventBus.publish('app:start');
        this.eventBus.publish('ui:loading:hide');
        console.info('App: Application started.');
    }

    /**
     * @brief Get a controller instance by name.
     * @param {string} controllerName - The name of the controller.
     * @returns {Object|null} The controller instance or null if not found.
     */
    getController(controllerName) {
        return this.controllers.get(controllerName) || null;
    }

    /**
     * @brief Get a service instance by name.
     * @param {string} serviceName - The name of the service.
     * @returns {Object|null} The service instance or null if not found.
     */
    getService(serviceName) {
        return this.services.get(serviceName) || null;
    }

    /**
     * @brief Gracefully shut down the application.
     * @description Cleans up resources and event listeners from all components.
     * @returns {Promise<void>}
     */
    async shutdown() {
        if (!this.isInitialized) return;
        
        this.eventBus.publish('app:shutdown');
        
        for (const [, controller] of this.controllers) {
            if (typeof controller.destroy === 'function') {
                await controller.destroy();
            }
        }
        
        for (const [, service] of this.services) {
            if (typeof service.destroy === 'function') {
                await service.destroy();
            }
        }
        
        this.controllers.clear();
        this.services.clear();
        this.isInitialized = false;
        
        console.info('App: Application shutdown complete.');
    }
}

export { App };