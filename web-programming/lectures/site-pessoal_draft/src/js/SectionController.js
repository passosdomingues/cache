/**
 * @file SectionController.js
 * @author Rafael Passos Domingues
 * @version 3.0.0
 * @brief Controller responsible for managing section content logic and interactions.
 * @description Handles section changes, lazy content loading, content filtering and searching,
 * and integrates interactions between NavigationView and SectionView with performance optimizations.
 */

import SectionView from './SectionView.js';

/**
 * @constant {Object} SECTION_CONFIG
 * @brief Configuration constants for section behavior and performance
 */
const SECTION_CONFIG = {
    LAZY_LOADING: {
        threshold: 0.1,
        rootMargin: '50px 0px',
        contentLoadDelay: 100
    },
    SEARCH: {
        debounceDelay: 300,
        maxResults: 20,
        minSearchLength: 2
    },
    ANIMATION: {
        staggerDelay: 100,
        transitionDuration: 300
    },
    PRELOAD: {
        adjacentSections: 1,
        criticalSections: ['hero', 'about', 'projects']
    }
};

/**
 * @constant {Object} ERROR_MESSAGES
 * @brief Standardized error messages for SectionController operations
 */
const ERROR_MESSAGES = {
    INVALID_MODELS: 'SectionController requires a valid models object.',
    INVALID_VIEWS: 'SectionController requires a valid views object or SectionView instance.',
    MISSING_SECTION_VIEW: 'SectionController requires a section view instance.',
    MISSING_CONTENT_MODEL: 'SectionController requires a content model instance.',
    INVALID_SECTION_ID: 'Invalid section ID provided for operation.',
    CONTENT_LOAD_FAILED: 'Failed to load content for section:'
};

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
     * @param {Object|SectionView} views - Collection of view instances or direct SectionView instance
     * @param {Object} [views.section] - Section view instance (if views is an object)
     * @param {Object} [views.navigation] - Navigation view instance (optional)
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
        // Handle both object format and direct SectionView instance
        if (views instanceof SectionView) {
            this.views = { section: views };
        } else {
            this.views = views;
        }
        
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
         * @type {IntersectionObserver|null}
         * @brief Observer for lazy loading content within sections
         */
        this.lazyLoadingObserver = null;
        
        /**
         * @private
         * @type {number|null}
         * @brief Timeout reference for search debouncing
         */
        this.searchTimeoutId = null;
        
        /**
         * @private
         * @type {Object}
         * @brief Configuration constants for section behavior
         */
        this.config = { ...SECTION_CONFIG };

        /**
         * @private
         * @type {boolean}
         * @brief Tracks initialization state of the controller
         */
        this.isInitialized = false;

        // Bind methods to maintain context
        this.handleSectionChange = this.handleSectionChange.bind(this);
        this.handleSectionVisibility = this.handleSectionVisibility.bind(this);
        this.handleContentFilter = this.handleContentFilter.bind(this);
        this.handleSearchInput = this.handleSearchInput.bind(this);
        this.handleLazyElementVisible = this.handleLazyElementVisible.bind(this);
    }

    /**
     * @brief Validates required dependencies for the controller
     * @private
     * @param {Object} models - Models object to validate
     * @param {Object|SectionView} views - Views object or SectionView instance to validate
     * @throws {TypeError} When required dependencies are missing
     */
    validateDependencies(models, views) {
        // Validate models parameter
        if (!models || typeof models !== 'object') {
            throw new TypeError(ERROR_MESSAGES.INVALID_MODELS);
        }

        // Validate views parameter - accept both object format and SectionView instance
        if (!views || (typeof views !== 'object' && !(views instanceof SectionView))) {
            throw new TypeError(ERROR_MESSAGES.INVALID_VIEWS);
        }

        // Validate section view availability
        const hasSectionView = (views.section && typeof views.section === 'object') || 
                              (views instanceof SectionView);
        
        if (!hasSectionView) {
            throw new TypeError(ERROR_MESSAGES.MISSING_SECTION_VIEW);
        }

        // Validate content model availability
        if (!models.content || typeof models.content !== 'object') {
            throw new TypeError(ERROR_MESSAGES.MISSING_CONTENT_MODEL);
        }

        // Validate content model has required methods
        const requiredModelMethods = ['getSections', 'getSectionById', 'getProjects', 'getExperiences'];
        const missingMethods = requiredModelMethods.filter(
            method => !models.content[method] || typeof models.content[method] !== 'function'
        );

        if (missingMethods.length > 0) {
            throw new TypeError(
                `Content model missing required methods: ${missingMethods.join(', ')}`
            );
        }
    }

    /**
     * @brief Initializes the controller and sets up event systems
     * @public
     * @returns {Promise<void>} Resolves when initialization is complete
     */
    async initialize() {
        if (this.isInitialized) {
            console.warn('SectionController: Already initialized');
            return;
        }

        try {
            const initializationTasks = [
                this.setupEventHandlers(),
                this.setupLazyLoadingObserver(),
                this.preloadCriticalContent()
            ];

            await Promise.all(initializationTasks);
            this.isInitialized = true;
            
            console.info('SectionController: Successfully initialized section management system.');
        } catch (error) {
            console.error('SectionController: Failed to initialize:', error);
            throw error;
        }
    }

    /**
     * @brief Renders all sections into the DOM using SectionView.
     * @public
     * @param {Array<Object>} sectionsData - An array of section data objects.
     * @returns {Promise<void>} Resolves when all sections are rendered.
     */
    async renderSections(sectionsData) {
        if (!this.views.section) {
            console.error('SectionController: SectionView is not available for rendering sections.');
            return;
        }
        console.info('SectionController: Rendering all sections.');
        await this.views.section.renderAllSections(sectionsData);
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

        // Handle browser visibility changes for performance optimization
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this), {
            signal: eventSignal
        });

        console.debug('SectionController: Event handlers established.');
    }

    /**
     * @brief Handles browser visibility changes for performance optimization
     * @private
     */
    handleVisibilityChange() {
        if (document.hidden) {
            // Reduce performance impact when tab is not visible
            this.pauseNonCriticalOperations();
        } else {
            // Resume normal operations when tab becomes visible
            this.resumeOperations();
        }
    }

    /**
     * @brief Pauses non-critical operations when tab is not visible
     * @private
     */
    pauseNonCriticalOperations() {
        if (this.lazyLoadingObserver) {
            this.lazyLoadingObserver.disconnect();
        }
    }

    /**
     * @brief Resumes operations when tab becomes visible
     * @private
     */
    resumeOperations() {
        if (this.lazyLoadingObserver) {
            // Reconnect lazy loading observer
            const sections = document.querySelectorAll('[data-section]');
            sections.forEach(section => {
                this.lazyLoadingObserver.observe(section);
            });
        }
    }

    /**
     * @brief Sets up intersection observer for lazy loading content
     * @private
     * @returns {Promise<void>} Resolves when the observer is set up
     */
    async setupLazyLoadingObserver() {
        const observerOptions = {
            root: null,
            rootMargin: this.config.LAZY_LOADING.rootMargin,
            threshold: this.config.LAZY_LOADING.threshold
        };

        this.lazyLoadingObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.handleLazyElementVisible(entry.target);
                }
            });
        }, observerOptions);

        // Start observing all sections
        const sections = document.querySelectorAll('[data-section]');
        sections.forEach(section => {
            this.lazyLoadingObserver.observe(section);
        });

        console.debug('SectionController: Lazy loading observer initialized.');
    }

    /**
     * @brief Preloads critical content for better user experience
     * @private
     * @returns {Promise<void>} Resolves when critical content is preloaded
     */
    async preloadCriticalContent() {
        try {
            const preloadPromises = this.config.PRELOAD.criticalSections.map(sectionId => 
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
    handleSectionChange(event) {
        if (!event || !event.detail) {
            console.warn('SectionController: Invalid section change event');
            return;
        }
        
        const { sectionId, previousSectionId } = event.detail;
        
        if (!this.isValidSectionId(sectionId)) {
            console.warn('SectionController: Received section change with invalid section ID:', sectionId);
            return;
        }

        this.processSectionActivation(sectionId, previousSectionId);
    }

    /**
     * @brief Validates if a section ID is valid
     * @private
     * @param {string} sectionId - Section ID to validate
     * @returns {boolean} True if section ID is valid
     */
    isValidSectionId(sectionId) {
        return typeof sectionId === 'string' && sectionId.trim().length > 0;
    }

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
            this.dispatchSectionEvent('sectionActivationError', {
                activeSectionId,
                error: error.message
            });
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
    handleSectionVisibility(eventType, eventData) {
        if (eventType === 'sectionVisible' && eventData.sectionId) {
            this.onSectionBecameVisible(eventData.sectionId, eventData);
        }
    }

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
        await new Promise(resolve => 
            setTimeout(resolve, this.config.LAZY_LOADING.contentLoadDelay)
        );
        
        sectionElement.classList.add('section--animated');
        
        // Animate child elements with staggered delays
        const animatableElements = sectionElement.querySelectorAll('[data-animate]');
        animatableElements.forEach((element, index) => {
            const delay = index * this.config.ANIMATION.staggerDelay;
            element.style.transitionDelay = `${delay}ms`;
            element.classList.add('animate-in');
        });
    }

    /**
     * @brief Preloads content for adjacent sections to improve perceived performance
     * @private
     * @param {string} currentSectionId - The ID of the currently active section
     */
    async preloadAdjacentSections(currentSectionId) {
        const allSections = await this.models.content.getSections();
        const currentSectionIndex = allSections.findIndex(s => s.id === currentSectionId);

        if (currentSectionIndex === -1) return;

        const sectionsToPreload = [];
        for (let i = 1; i <= this.config.PRELOAD.adjacentSections; i++) {
            // Preload next section
            if (currentSectionIndex + i < allSections.length) {
                sectionsToPreload.push(allSections[currentSectionIndex + i].id);
            }
            // Preload previous section
            if (currentSectionIndex - i >= 0) {
                sectionsToPreload.push(allSections[currentSectionIndex - i].id);
            }
        }

        const preloadPromises = sectionsToPreload.map(sectionId => 
            this.preloadSectionContent(sectionId)
        );

        await Promise.allSettled(preloadPromises);
        console.debug(`SectionController: Preloaded adjacent sections for ${currentSectionId}:`, sectionsToPreload);
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
                // Create a new image element to test loading
                const testImage = new Image();
                
                if (img.dataset.src) {
                    testImage.src = img.dataset.src;
                    img.src = img.dataset.src;
                    delete img.dataset.src;
                }
                
                if (img.dataset.srcset) {
                    img.srcset = img.dataset.srcset;
                    delete img.dataset.srcset;
                }
                
                // Remove loading attribute if set to lazy
                if (img.loading === 'lazy') {
                    img.loading = 'eager';
                }
                
                testImage.addEventListener('load', () => {
                    img.classList.add('image-loaded');
                    resolve();
                }, { once: true });
                
                testImage.addEventListener('error', () => {
                    console.warn('SectionController: Failed to load image:', img.dataset.src || img.src);
                    img.classList.add('image-error');
                    resolve();
                }, { once: true });
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
                
                // Remove loading attribute if set to lazy
                if (media.loading === 'lazy') {
                    media.loading = 'eager';
                }
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
        try {
            const sectionData = await this.models.content.getSectionById(sectionId);
            
            if (sectionData && sectionData.type) {
                const contentMapping = {
                    'about': 'getAboutContent',
                    'astrophysics': 'getAstrophysicsContent',
                    'observatory': 'getObservatoryContent',
                    'craam': 'getCraamContent',
                    'lna': 'getLNATelescopeContent',
                    'education': 'getEducationContent',
                    'innovation': 'getInnovationContent',
                    'deep-learning': 'getDeepLearningProjectsContent',
                    'projects': 'getProjectsContent',
                    'hobbies': 'getHobbiesContent',
                    'skills': 'getSkillsContent'
                };

                const contentMethod = contentMapping[sectionData.type];
                if (!contentMethod || typeof this.models.content[contentMethod] !== 'function') {
                    console.warn(`No content loader for section type: ${sectionData.type}`);
                    return;
                }

                const contentData = await this.models.content[contentMethod]();
                if (contentData && (!Array.isArray(contentData) || contentData.length > 0)) {
                    await this.views.section.renderSectionContent(sectionId, sectionData.type, contentData);
                }
            }
        } catch (error) {
            console.error(`${ERROR_MESSAGES.CONTENT_LOAD_FAILED} ${sectionId}`, error);
            this.dispatchSectionEvent('contentLoadError', {
                sectionId,
                error: error.message
            });
        }
    }

    /**
     * @brief Handles content filter requests
     * @private
     * @param {CustomEvent} event - Filter request event
     */
    handleContentFilter(event) {
        const { category, filterType } = event.detail;
        this.filterContentByCategory(category, filterType);
    }

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
                const projects = this.models.content.getProjects() || [];
                content = content.concat(projects);
            }
            
            if (filterType === 'all' || filterType === 'experiences') {
                const experiences = this.models.content.getExperiences() || [];
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
    handleSearchInput(event) {
        const { searchTerm, searchType } = event.detail;
        
        // Clear previous timeout
        if (this.searchTimeoutId) {
            clearTimeout(this.searchTimeoutId);
        }

        // Debounce search to avoid excessive operations
        this.searchTimeoutId = setTimeout(() => {
            this.executeContentSearch(searchTerm, searchType);
        }, this.config.SEARCH.debounceDelay);
    }

    /**
     * @brief Executes content search across multiple content types
     * @private
     * @param {string} searchTerm - The term to search for
     * @param {string} searchType - Type of content to search
     */
    executeContentSearch(searchTerm, searchType = 'all') {
        if (!searchTerm || searchTerm.trim().length < this.config.SEARCH.minSearchLength) {
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
            const projects = this.models.content.getProjects() || [];
            allContent = allContent.concat(projects);
        }

        if (contentType === 'all' || contentType === 'experiences') {
            const experiences = this.models.content.getExperiences() || [];
            allContent = allContent.concat(experiences);
        }

        const searchResults = allContent.filter(item => {
            const titleMatch = item.title && 
                item.title.toLowerCase().includes(normalizedSearchTerm);
            const descriptionMatch = item.description && 
                item.description.toLowerCase().includes(normalizedSearchTerm);
            const tagMatch = item.tags && 
                item.tags.some(tag => tag.toLowerCase().includes(normalizedSearchTerm));
            const categoryMatch = item.category && 
                item.category.toLowerCase().includes(normalizedSearchTerm);

            return titleMatch || descriptionMatch || tagMatch || categoryMatch;
        }).slice(0, this.config.SEARCH.maxResults);

        return searchResults;
    }

    /**
     * @brief Handles lazy element visibility for dynamic loading
     * @private
     * @param {HTMLElement} element - The element that became visible
     */
    handleLazyElementVisible(element) {
        if (element.dataset.lazyType === 'image') {
            this.loadLazyImageElement(element);
        } else if (element.dataset.lazyType === 'component') {
            this.loadLazyComponent(element);
        } else if (element.dataset.lazyType === 'video') {
            this.loadLazyVideoElement(element);
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
     * @brief Loads a lazy video element
     * @private
     * @param {HTMLElement} videoElement - The video element to load
     */
    loadLazyVideoElement(videoElement) {
        if (videoElement.dataset.src) {
            videoElement.src = videoElement.dataset.src;
            delete videoElement.dataset.src;
        }
        
        // Load poster image if available
        if (videoElement.dataset.poster) {
            videoElement.poster = videoElement.dataset.poster;
            delete videoElement.dataset.poster;
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
        
        // Dispatch event for component loading
        this.dispatchSectionEvent('lazyComponentLoaded', {
            element: componentElement,
            componentType: componentElement.dataset.componentType
        });
    }

    /**
     * @brief Tracks section views for analytics
     * @private
     * @param {string} sectionId - The section ID that was viewed
     */
    trackSectionView(sectionId) {
        const analyticsData = {
            sectionId,
            timestamp: new Date().toISOString(),
            viewCount: this.getSectionViewCount(sectionId) + 1
        };
        
        // Store view count in session storage
        this.incrementSectionViewCount(sectionId);
        
        this.dispatchSectionEvent('sectionViewTracked', analyticsData);
        
        console.debug('SectionController: Tracking section view', analyticsData);
    }

    /**
     * @brief Gets the view count for a specific section
     * @private
     * @param {string} sectionId - The section ID
     * @returns {number} View count for the section
     */
    getSectionViewCount(sectionId) {
        try {
            const viewData = sessionStorage.getItem(`section_views_${sectionId}`);
            return viewData ? parseInt(viewData, 10) : 0;
        } catch (error) {
            console.warn('SectionController: Could not access session storage:', error);
            return 0;
        }
    }

    /**
     * @brief Increments the view count for a specific section
     * @private
     * @param {string} sectionId - The section ID
     */
    incrementSectionViewCount(sectionId) {
        try {
            const currentCount = this.getSectionViewCount(sectionId);
            sessionStorage.setItem(`section_views_${sectionId}`, (currentCount + 1).toString());
        } catch (error) {
            console.warn('SectionController: Could not update session storage:', error);
        }
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
     * @param {Object} sectionData - Section data for context
     * @returns {Promise<void>} Resolves when projects content is loaded
     */
    async loadProjectsContent(sectionData) {
        try {
            const projects = await this.models.content.getProjects();
            this.dispatchSectionEvent('projectsContentLoaded', {
                sectionData,
                projects,
                projectCount: projects.length
            });
            console.debug('SectionController: Projects content loaded');
        } catch (error) {
            console.error('SectionController: Failed to load projects content:', error);
            throw error;
        }
    }

    /**
     * @brief Loads experiences content from model
     * @private
     * @param {Object} sectionData - Section data for context
     * @returns {Promise<void>} Resolves when experiences content is loaded
     */
    async loadExperiencesContent(sectionData) {
        try {
            const experiences = await this.models.content.getExperiences();
            this.dispatchSectionEvent('experiencesContentLoaded', {
                sectionData,
                experiences,
                experienceCount: experiences.length
            });
            console.debug('SectionController: Experiences content loaded');
        } catch (error) {
            console.error('SectionController: Failed to load experiences content:', error);
            throw error;
        }
    }

    /**
     * @brief Loads research content from model
     * @private
     * @param {Object} sectionData - Section data for context
     * @returns {Promise<void>} Resolves when research content is loaded
     */
    async loadResearchContent(sectionData) {
        try {
            const research = await this.models.content.getResearch();
            this.dispatchSectionEvent('researchContentLoaded', {
                sectionData,
                research,
                researchCount: research.length
            });
            console.debug('SectionController: Research content loaded');
        } catch (error) {
            console.error('SectionController: Failed to load research content:', error);
            throw error;
        }
    }

    /**
     * @brief Loads timeline content from model
     * @private
     * @param {Object} sectionData - Section data for context
     * @returns {Promise<void>} Resolves when timeline content is loaded
     */
    async loadTimelineContent(sectionData) {
        try {
            const timeline = await this.models.content.getTimeline();
            this.dispatchSectionEvent('timelineContentLoaded', {
                sectionData,
                timeline,
                timelineCount: timeline.length
            });
            console.debug('SectionController: Timeline content loaded');
        } catch (error) {
            console.error('SectionController: Failed to load timeline content:', error);
            throw error;
        }
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
     * @brief Gets the initialization state of the controller
     * @public
     * @returns {boolean} True if the controller is initialized
     */
    getInitializationState() {
        return this.isInitialized;
    }

    /**
     * @brief Updates controller configuration
     * @public
     * @param {Object} newConfig - New configuration options
     */
    updateConfiguration(newConfig) {
        this.config = {
            ...this.config,
            ...newConfig
        };
        console.debug('SectionController: Configuration updated', this.config);
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

        // Reset initialization state
        this.isInitialized = false;

        console.info('SectionController: Controller destroyed and resources cleaned up.');
    }
}

export default SectionController;

