import eventBus from '../core/EventBus.js';
import { ViewManager } from '../views/ViewManager.js';

/**
 * @brief Main application controller
 * @description Orchestrates views and models for the main content
 */
class MainController {
    constructor(dependencies = {}) {
        this.eventBus = dependencies.eventBus || eventBus;
        this.contentModel = dependencies.contentModel;
        this.services = dependencies.services || {};
        
        this.viewManager = null;
        this.isInitialized = false;

        this.onContentLoaded = this.onContentLoaded.bind(this);
        this.onSectionActivated = this.onSectionActivated.bind(this);
    }

    /**
     * @brief Initialize the main controller
     * @description Sets up view manager and event listeners
     * @returns {Promise<void>}
     */
    async init() {
        if (this.isInitialized) {
            console.warn('MainController: Already initialized');
            return;
        }

        try {
            // Initialize ViewManager
            const sectionsContainer = document.getElementById('sections-container');
            if (!sectionsContainer) {
                throw new Error('MainController: sections-container element not found');
            }

            this.viewManager = new ViewManager({
                container: sectionsContainer,
                eventBus: this.eventBus
            });

            // Set up event listeners
            this.setupEventListeners();

            // Wait for content model to be ready
            if (this.contentModel && !this.contentModel.isInitialized) {
                await this.contentModel.initializeContentModel();
            }

            // Initial render
            await this.renderAllSections();

            this.isInitialized = true;
            console.info('MainController: Initialized successfully');

        } catch (error) {
            console.error('MainController: Initialization failed', error);
            this.eventBus.publish('app:error', error);
        }
    }

    /**
     * @brief Set up event listeners
     */
    setupEventListeners() {
        this.eventBus.subscribe('content:loaded', this.onContentLoaded);
        this.eventBus.subscribe('section:activated', this.onSectionActivated);
        this.eventBus.subscribe('ui:loading:hide', this.hideLoadingOverlay.bind(this));
    }

    /**
     * @brief Handle content loaded event
     * @param {Object} data - Event data
     */
    onContentLoaded(data) {
        this.renderAllSections();
    }

    /**
     * @brief Handle section activation
     * @param {Object} data - Section data
     */
    onSectionActivated(data) {
        this.highlightActiveSection(data.sectionId);
    }

    /**
     * @brief Render all sections
     * @returns {Promise<void>}
     */
    async renderAllSections() {
        if (!this.viewManager || !this.contentModel) {
            console.warn('MainController: ViewManager or ContentModel not available');
            return;
        }

        try {
            const sections = this.contentModel.getAllSections();
            
            // Clear existing content
            this.viewManager.container.innerHTML = '';
            
            // Render each section
            sections.forEach(section => {
                if (section.metadata.visible) {
                    this.viewManager.renderSection(section);
                }
            });

            this.eventBus.publish('maincontroller:sections:rendered', { sections });
            console.info(`MainController: Rendered ${sections.length} sections`);

        } catch (error) {
            console.error('MainController: Error rendering sections', error);
            this.eventBus.publish('render:error', error);
        }
    }

    /**
     * @brief Highlight active section in view
     * @param {string} sectionId - ID of the active section
     */
    highlightActiveSection(sectionId) {
        // Remove active class from all sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('section--active');
        });

        // Add active class to current section
        const activeSection = document.getElementById(sectionId);
        if (activeSection) {
            activeSection.classList.add('section--active');
        }
    }

    /**
     * @brief Hide loading overlay
     */
    hideLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 500);
        }
    }

    /**
     * @brief Get section by ID
     * @param {string} sectionId - Section identifier
     * @returns {Object|null} Section data
     */
    getSection(sectionId) {
        return this.contentModel ? this.contentModel.getSection(sectionId) : null;
    }

    /**
     * @brief Update section content
     * @param {string} sectionId - Section identifier
     * @param {Object} newContent - New content data
     */
    updateSection(sectionId, newContent) {
        if (this.contentModel) {
            this.contentModel.updateSection(sectionId, newContent);
            this.eventBus.publish('section:updated', { sectionId, newContent });
        }
    }

    /**
     * @brief Destroy controller and clean up
     */
    destroy() {
        this.eventBus.unsubscribe('content:loaded', this.onContentLoaded);
        this.eventBus.unsubscribe('section:activated', this.onSectionActivated);
        this.eventBus.unsubscribe('ui:loading:hide', this.hideLoadingOverlay);
        
        this.viewManager = null;
        this.isInitialized = false;
        
        console.info('MainController: Destroyed');
    }
}

export { MainController };