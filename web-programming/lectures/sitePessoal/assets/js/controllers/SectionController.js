/**
 * @file SectionController.js
 * @author Rafael Passos Domingues
 * @version 3.0.0
 * @brief Controller responsible for managing section content logic and interactions.
 * @description Handles section changes, lazy content loading, content filtering and searching,
 * and integrates interactions between NavigationView and SectionView with performance optimizations.
 */

/**
 * @class SectionController
 * @brief Manages section content logic, lazy loading, filtering, and search functionality
 * @description Coordinates between models and views to handle dynamic content loading,
 * section visibility tracking, content filtering, and search operations with performance optimizations
 */
class SectionController {
    /**
     * @brief Creates an instance of SectionController
     * @constructor
     * @param {Object} models - Collection of application model instances
     * @param {Object} models.content - Content data model instance
     * @param {Object} models.user - User data model instance
     * @param {Object} views - Collection of view instances
     * @param {Object} views.section - Section view instance
     * @param {Object} views.navigation - Navigation view instance (optional)
     * @throws {TypeError} When required models or views are not provided
     */
    constructor(models, views) {
        this.validateDependencies(models, views);
        
        /**
         * @private
         * @type {Object}
         * @brief Collection of application data models
         */
        this.models = models;
        
        /**
         * @private
         * @type {Object}
         * @brief Collection of view instances
         */
        this.views = views;
        
        /**
         * @private
         * @type {Set}
         * @brief Tracks sections that have already loaded lazy content
         */
        this.loadedSections = new Set();
        
        /**
         * @private
         * @type {AbortController}
         * @brief Manages cleanup of event listeners
         */
        this.eventAbortController = new AbortController();
        
        /**
         * @private
         * @type {IntersectionObserver}
         * @brief Observer for lazy loading content within sections
         */
        this.lazyLoadingObserver = null;
        
        /**
         * @private
         * @type {Object}
         * @brief Configuration constants for section behavior
         */
        this.sectionConfig = {
            lazyLoadThreshold: 0.1,
            lazyLoadRootMargin: '50px 0px',
            debounceSearchDelay: 300,
            maxSearchResults: 20,
            contentLoadDelay: 100
        };

        // Bind methods to maintain context
        this.handleSectionChange = this.handleSectionChange.bind(this);
        this.handleSectionVisibility = this.handleSectionVisibility.bind(this);
        this.handleContentFilter = this.handleContentFilter.bind(this);
        this.handleSearchInput = this.handleSearchInput.bind(this);
    }

    /**
     * @brief Validates required dependencies for the controller
     * @private
     * @param {Object} models - Models object to validate
     * @param {Object} views - Views object to validate
     * @throws {TypeError} When required dependencies are missing
     */
    validateDependencies(models, views) {
        if (!models || typeof models !== 'object') {
            throw new TypeError('SectionController requires a valid models object.');
        }

        if (!views || typeof views !== 'object') {
            throw new TypeError('SectionController requires a valid views object.');
        }

        if (!views.section) {
            throw new TypeError('SectionController requires a section view instance.');
        }

        if (!models.content) {
            throw new TypeError('SectionController requires a content model instance.');
        }
    }

    /**
     * @brief Initializes the controller and sets up event systems
     * @public
     * @returns {Promise<void>} Resolves when initialization is complete
     */
    async initialize() {
        try {
            await this.setupEventHandlers();
            await this.setupLazyLoadingObserver();
            await this.preloadCriticalContent();
            
            console.info('SectionController: Successfully initialized section management system.');
        } catch (error) {
            console.error('SectionController: Failed to initialize:', error);
            throw error;
        }
    }

    /**
     * @brief Sets up event handlers for section and content events
     * @private
     * @returns {Promise<void>} Resolves when all event handlers are set up
     */
    async setupEventHandlers() {
        const eventSignal = this.eventAbortController.signal;

        // Global section change events
        document.addEventListener('navigation:sectionChanged', this.handleSectionChange, {
            signal: eventSignal
        });

        // Section view visibility events
        if (this.views.section && typeof this.views.section.addObserver === 'function') {
            this.views.section.addObserver(this.handleSectionVisibility, { signal: eventSignal });
        }

        // Custom events for filtering and searching
        document.addEventListener('content:filterRequested', this.handleContentFilter, {
            signal: eventSignal
        });

        document.addEventListener('content:searchRequested', this.handleSearchInput, {
            signal: eventSignal
        });

        console.debug('SectionController: Event handlers established.');
    }

    /**
     * @brief Sets up intersection observer for lazy loading content
     * @private
     * @returns {Promise<void>} Resolves when the observer is set up
     */
    async setupLazyLoadingObserver() {
        const observerOptions = {
            root: null,
            rootMargin: this.sectionConfig.lazyLoadRootMargin,
            threshold: this.sectionConfig.lazyLoadThreshold
        };

        this.lazyLoadingObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.handleLazyElementVisible(entry.target);
                }
            });
        }, observerOptions);

        console.debug('SectionController: Lazy loading observer initialized.');
    }

    /**
     * @brief Preloads critical content for better user experience
     * @private
     * @returns {Promise<void>} Resolves when critical content is preloaded
     */
    async preloadCriticalContent() {
        try {
            // Preload content for the first visible section or hero section
            const initialSections = ['hero', 'about', 'projects'];
            
            const preloadPromises = initialSections.map(sectionId => 
                this.preloadSectionContent(sectionId)
            );

            await Promise.allSettled(preloadPromises);
            console.debug('SectionController: Critical content preloaded.');
        } catch (error) {
            console.warn('SectionController: Critical content preloading failed:', error);
        }
    }

    /**
     * @brief Handles section change events from navigation
     * @private
     * @param {CustomEvent} event - Section change event
     */
    handleSectionChange = (event) => {
        const { sectionId, previousSectionId } = event.detail;
        
        if (!sectionId) {
            console.warn('SectionController: Received section change with invalid section ID');
            return;
        }

        this.processSectionActivation(sectionId, previousSectionId);
    };

    /**
     * @brief Processes section activation and triggers related actions
     * @private
     * @param {string} activeSectionId - The newly active section ID
     * @param {string} previousSectionId - The previously active section ID
     */
    async processSectionActivation(activeSectionId, previousSectionId) {
        try {
            // Update navigation state if navigation view is available
            this.updateNavigationState(activeSectionId);
            
            // Load lazy content for the active section
            await this.loadSectionLazyContent(activeSectionId);
            
            // Track analytics for section views
            this.trackSectionView(activeSectionId);
            
            // Dispatch section activated event
            this.dispatchSectionEvent('sectionActivated', {
                activeSectionId,
                previousSectionId,
                timestamp: Date.now()
            });

            console.debug(`SectionController: Section ${activeSectionId} activated.`);
            
        } catch (error) {
            console.error(`SectionController: Failed to process section activation for ${activeSectionId}:`, error);
        }
    }

    /**
     * @brief Updates navigation state when section changes
     * @private
     * @param {string} activeSectionId - The active section ID
     */
    updateNavigationState(activeSectionId) {
        if (this.views.navigation && typeof this.views.navigation.setActiveSection === 'function') {
            this.views.navigation.setActiveSection(activeSectionId);
        }
    }

    /**
     * @brief Handles section visibility events from SectionView
     * @private
     * @param {string} eventType - Type of visibility event
     * @param {Object} eventData - Data associated with the visibility event
     */
    handleSectionVisibility = (eventType, eventData) => {
        if (eventType === 'sectionVisible' && eventData.sectionId) {
            this.onSectionBecameVisible(eventData.sectionId, eventData);
        }
    };

    /**
     * @brief Handles when a section becomes visible in the viewport
     * @private
     * @param {string} sectionId - The section ID that became visible
     * @param {Object} visibilityData - Additional visibility data
     */
    async onSectionBecameVisible(sectionId, visibilityData) {
        console.debug(`SectionController: Section '${sectionId}' is now visible.`);
        
        // Trigger animations or additional content loading
        await this.triggerSectionAnimations(sectionId);
        
        // Preload adjacent sections for smoother navigation
        this.preloadAdjacentSections(sectionId);
        
        // Dispatch visibility event
        this.dispatchSectionEvent('sectionVisible', {
            sectionId,
            intersectionRatio: visibilityData.intersectionRatio,
            timestamp: Date.now()
        });
    }

    /**
     * @brief Triggers animations for section elements
     * @private
     * @param {string} sectionId - The section ID to animate
     * @returns {Promise<void>} Resolves when animations are triggered
     */
    async triggerSectionAnimations(sectionId) {
        const sectionElement = document.getElementById(sectionId);
        if (!sectionElement) return;

        // Add animation class after a small delay for better UX
        await new Promise(resolve => setTimeout(resolve, this.sectionConfig.contentLoadDelay));
        
        sectionElement.classList.add('section--animated');
        
        // Animate child elements with staggered delays
        const animatableElements = sectionElement.querySelectorAll('[data-animate]');
        animatableElements.forEach((element, index) => {
            element.style.setProperty('--animation-delay', `${index * 0.1}s`);
            element.classList.add('element--animated');
        });
    }

    /**
     * @brief Preloads content for sections adjacent to the current one
     * @private
     * @param {string} currentSectionId - The current section ID
     */
    preloadAdjacentSections(currentSectionId) {
        const allSections = Array.from(document.querySelectorAll('[data-section]'));
        const currentIndex = allSections.findIndex(section => section.id === currentSectionId);
        
        if (currentIndex === -1) return;

        // Preload next section
        const nextSection = allSections[currentIndex + 1];
        if (nextSection && !this.loadedSections.has(nextSection.id)) {
            this.preloadSectionContent(nextSection.id);
        }

        // Preload previous section if not too far back
        const previousSection = allSections[currentIndex - 1];
        if (previousSection && currentIndex > 0 && !this.loadedSections.has(previousSection.id)) {
            this.preloadSectionContent(previousSection.id);
        }
    }

    /**
     * @brief Loads lazy content for a specific section
     * @private
     * @param {string} sectionId - The section ID to load content for
     * @returns {Promise<void>} Resolves when lazy content is loaded
     */
    async loadSectionLazyContent(sectionId) {
        if (this.loadedSections.has(sectionId)) {
            return; // Content already loaded
        }

        const sectionElement = document.getElementById(sectionId);
        if (!sectionElement) {
            console.warn(`SectionController: Section element not found: ${sectionId}`);
            return;
        }

        try {
            // Load lazy images
            await this.loadLazyImages(sectionElement);
            
            // Load lazy iframes and videos
            await this.loadLazyMedia(sectionElement);
            
            // Load dynamic content via API if needed
            await this.loadDynamicSectionContent(sectionId);
            
            // Mark section as loaded
            this.loadedSections.add(sectionId);
            
            console.debug(`SectionController: Lazy content loaded for section: ${sectionId}`);
            
        } catch (error) {
            console.error(`SectionController: Failed to load lazy content for ${sectionId}:`, error);
        }
    }

    /**
     * @brief Preloads section content without making it visible
     * @private
     * @param {string} sectionId - The section ID to preload
     * @returns {Promise<void>} Resolves when preloading is complete
     */
    async preloadSectionContent(sectionId) {
        // Implementation for preloading section content
        // This could involve fetching data, caching resources, etc.
        console.debug(`SectionController: Preloading content for section: ${sectionId}`);
    }

    /**
     * @brief Loads lazy images within a section element
     * @private
     * @param {HTMLElement} sectionElement - The section element containing lazy images
     * @returns {Promise<void>} Resolves when all images are loaded
     */
    async loadLazyImages(sectionElement) {
        const lazyImages = sectionElement.querySelectorAll('img[data-src], img[data-srcset]');
        const imageLoadPromises = Array.from(lazyImages).map(img => {
            return new Promise((resolve) => {
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    delete img.dataset.src;
                }
                if (img.dataset.srcset) {
                    img.srcset = img.dataset.srcset;
                    delete img.dataset.srcset;
                }
                
                img.addEventListener('load', resolve, { once: true });
                img.addEventListener('error', resolve, { once: true });
            });
        });

        await Promise.allSettled(imageLoadPromises);
    }

    /**
     * @brief Loads lazy media elements (iframes, videos) within a section
     * @private
     * @param {HTMLElement} sectionElement - The section element containing lazy media
     * @returns {Promise<void>} Resolves when all media elements are loaded
     */
    async loadLazyMedia(sectionElement) {
        const lazyMedia = sectionElement.querySelectorAll('[data-src]');
        
        lazyMedia.forEach(media => {
            if (media.tagName === 'IFRAME' || media.tagName === 'VIDEO') {
                media.src = media.dataset.src;
                delete media.dataset.src;
            }
        });
    }

    /**
     * @brief Loads dynamic content for a section via API or model
     * @private
     * @param {string} sectionId - The section ID to load dynamic content for
     * @returns {Promise<void>} Resolves when dynamic content is loaded
     */
    async loadDynamicSectionContent(sectionId) {
        // Implementation for loading dynamic content based on section type
        const contentHandlers = {
            projects: () => this.loadProjectsContent(),
            experiences: () => this.loadExperiencesContent(),
            research: () => this.loadResearchContent()
        };

        const handler = contentHandlers[sectionId];
        if (handler) {
            await handler();
        }
    }

    /**
     * @brief Handles content filter requests
     * @private
     * @param {CustomEvent} event - Filter request event
     */
    handleContentFilter = (event) => {
        const { category, filterType } = event.detail;
        this.filterContentByCategory(category, filterType);
    };

    /**
     * @brief Filters content by category and type
     * @public
     * @param {string} category - The category to filter by
     * @param {string} filterType - Type of content to filter (projects, experiences, etc.)
     * @returns {Array} Filtered content array
     */
    filterContentByCategory(category, filterType = 'all') {
        if (!category) {
            console.warn('SectionController: Filter category not provided');
            return [];
        }

        try {
            let content = [];
            
            if (filterType === 'all' || filterType === 'projects') {
                const projects = this.models.content.getProjects?.() || [];
                content = content.concat(projects);
            }
            
            if (filterType === 'all' || filterType === 'experiences') {
                const experiences = this.models.content.getExperiences?.() || [];
                content = content.concat(experiences);
            }

            const filteredContent = content.filter(item => 
                item.category && item.category.toLowerCase() === category.toLowerCase()
            );

            this.dispatchSectionEvent('contentFiltered', {
                category,
                filterType,
                resultCount: filteredContent.length,
                results: filteredContent
            });

            return filteredContent;

        } catch (error) {
            console.error('SectionController: Content filtering failed:', error);
            this.dispatchSectionEvent('contentFilterError', { error: error.message });
            return [];
        }
    }

    /**
     * @brief Handles search input with debouncing
     * @private
     * @param {CustomEvent} event - Search request event
     */
    handleSearchInput = (event) => {
        const { searchTerm, searchType } = event.detail;
        
        // Clear previous timeout
        if (this.searchTimeoutId) {
            clearTimeout(this.searchTimeoutId);
        }

        // Debounce search to avoid excessive operations
        this.searchTimeoutId = setTimeout(() => {
            this.executeContentSearch(searchTerm, searchType);
        }, this.sectionConfig.debounceSearchDelay);
    };

    /**
     * @brief Executes content search across multiple content types
     * @private
     * @param {string} searchTerm - The term to search for
     * @param {string} searchType - Type of content to search
     */
    executeContentSearch(searchTerm, searchType = 'all') {
        if (!searchTerm || searchTerm.trim().length < 2) {
            this.dispatchSectionEvent('searchCompleted', {
                searchTerm,
                results: [],
                resultCount: 0
            });
            return;
        }

        try {
            const searchResults = this.searchContent(searchTerm, searchType);
            
            this.dispatchSectionEvent('searchCompleted', {
                searchTerm,
                results: searchResults,
                resultCount: searchResults.length
            });

        } catch (error) {
            console.error('SectionController: Content search failed:', error);
            this.dispatchSectionEvent('searchError', { 
                searchTerm, 
                error: error.message 
            });
        }
    }

    /**
     * @brief Searches content by term in title or description
     * @public
     * @param {string} searchTerm - The term to search for
     * @param {string} contentType - Type of content to search (projects, experiences, all)
     * @returns {Array} Search results array
     */
    searchContent(searchTerm, contentType = 'all') {
        if (!searchTerm) {
            return [];
        }

        let allContent = [];
        const normalizedSearchTerm = searchTerm.toLowerCase().trim();

        if (contentType === 'all' || contentType === 'projects') {
            const projects = this.models.content.getProjects?.() || [];
            allContent = allContent.concat(projects);
        }

        if (contentType === 'all' || contentType === 'experiences') {
            const experiences = this.models.content.getExperiences?.() || [];
            allContent = allContent.concat(experiences);
        }

        const searchResults = allContent.filter(item => {
            const titleMatch = item.title && 
                item.title.toLowerCase().includes(normalizedSearchTerm);
            const descriptionMatch = item.description && 
                item.description.toLowerCase().includes(normalizedSearchTerm);
            const tagMatch = item.tags && 
                item.tags.some(tag => tag.toLowerCase().includes(normalizedSearchTerm));

            return titleMatch || descriptionMatch || tagMatch;
        }).slice(0, this.sectionConfig.maxSearchResults);

        return searchResults;
    }

    /**
     * @brief Handles lazy element visibility for dynamic loading
     * @private
     * @param {HTMLElement} element - The element that became visible
     */
    handleLazyElementVisible(element) {
        // Implementation for handling specific lazy elements
        if (element.dataset.lazyType === 'image') {
            this.loadLazyImageElement(element);
        } else if (element.dataset.lazyType === 'component') {
            this.loadLazyComponent(element);
        }
    }

    /**
     * @brief Loads a specific lazy image element
     * @private
     * @param {HTMLElement} imgElement - The image element to load
     */
    loadLazyImageElement(imgElement) {
        if (imgElement.dataset.src) {
            imgElement.src = imgElement.dataset.src;
            delete imgElement.dataset.src;
        }
        if (imgElement.dataset.srcset) {
            imgElement.srcset = imgElement.dataset.srcset;
            delete imgElement.dataset.srcset;
        }
    }

    /**
     * @brief Loads a lazy component dynamically
     * @private
     * @param {HTMLElement} componentElement - The component element to load
     */
    loadLazyComponent(componentElement) {
        // Implementation for dynamic component loading
        console.debug('SectionController: Loading lazy component', componentElement);
    }

    /**
     * @brief Tracks section views for analytics
     * @private
     * @param {string} sectionId - The section ID that was viewed
     */
    trackSectionView(sectionId) {
        // Integration point for analytics services
        const analyticsData = {
            sectionId,
            timestamp: new Date().toISOString(),
            duration: Date.now() // This would be calculated based on view time
        };
        
        console.debug('SectionController: Tracking section view', analyticsData);
    }

    /**
     * @brief Dispatches section-related events for inter-component communication
     * @private
     * @param {string} eventType - Type of section event
     * @param {Object} eventDetail - Additional event data
     */
    dispatchSectionEvent(eventType, eventDetail = {}) {
        const sectionEvent = new CustomEvent(`section:${eventType}`, {
            detail: {
                timestamp: Date.now(),
                controller: 'SectionController',
                ...eventDetail
            },
            bubbles: true,
            cancelable: true
        });

        document.dispatchEvent(sectionEvent);
    }

    /**
     * @brief Loads projects content from model
     * @private
     * @returns {Promise<void>} Resolves when projects content is loaded
     */
    async loadProjectsContent() {
        // Implementation for loading projects content
        console.debug('SectionController: Loading projects content');
    }

    /**
     * @brief Loads experiences content from model
     * @private
     * @returns {Promise<void>} Resolves when experiences content is loaded
     */
    async loadExperiencesContent() {
        // Implementation for loading experiences content
        console.debug('SectionController: Loading experiences content');
    }

    /**
     * @brief Loads research content from model
     * @private
     * @returns {Promise<void>} Resolves when research content is loaded
     */
    async loadResearchContent() {
        // Implementation for loading research content
        console.debug('SectionController: Loading research content');
    }

    /**
     * @brief Gets the set of loaded sections
     * @public
     * @returns {Set} Set of section IDs that have been loaded
     */
    getLoadedSections() {
        return new Set(this.loadedSections);
    }

    /**
     * @brief Checks if a section has been loaded
     * @public
     * @param {string} sectionId - The section ID to check
     * @returns {boolean} True if the section has been loaded
     */
    isSectionLoaded(sectionId) {
        return this.loadedSections.has(sectionId);
    }

    /**
     * @brief Cleans up resources and event listeners
     * @public
     * @description Properly tears down the controller to prevent memory leaks
     */
    destroy() {
        // Abort all event listeners
        this.eventAbortController.abort();

        // Disconnect lazy loading observer
        if (this.lazyLoadingObserver) {
            this.lazyLoadingObserver.disconnect();
            this.lazyLoadingObserver = null;
        }

        // Clear any pending timeouts
        if (this.searchTimeoutId) {
            clearTimeout(this.searchTimeoutId);
            this.searchTimeoutId = null;
        }

        // Clear loaded sections tracking
        this.loadedSections.clear();

        console.info('SectionController: Controller destroyed and resources cleaned up.');
    }
}

export default SectionController;