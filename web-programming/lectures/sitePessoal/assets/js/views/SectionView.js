/**
 * @file SectionView.js
 * @author Rafael Passos Domingues
 * @version 3.0.0
 * @brief Enhanced section view component for dynamic content rendering
 * @description Generates and manages content sections including cards, timelines,
 *              galleries, and skill lists with optimized animations, observers,
 *              and accessibility features.
 */

import BaseView from './BaseView.js';

// Configuration constants for maintainability and performance
const SECTION_CONFIG = {
    observerThreshold: 0.2,
    animationClass: 'section-visible',
    loadingStrategy: 'lazy',
    aria: {
        sectionLabel: 'content section',
        galleryLabel: 'image gallery',
        timelineLabel: 'timeline events',
        skillsLabel: 'skills list',
        cardsLabel: 'content cards'
    },
    selectors: {
        section: '.section',
        sectionTitle: '.section-title',
        sectionSubtitle: '.section-subtitle',
        cardGrid: '.card-grid',
        timeline: '.timeline',
        gallery: '.gallery',
        skillsGrid: '.skills-grid'
    }
};

/**
 * @class SectionView
 * @extends BaseView
 * @brief Advanced section management view with dynamic content rendering
 * @description Handles creation, rendering, and interaction of multiple content section types
 *              with optimized performance, accessibility, and user experience
 */
class SectionView extends BaseView {
    /**
     * @brief Creates a new SectionView instance
     * @param {HTMLElement} containerElement - Main content container element (typically <main>)
     * @throws {TypeError} When containerElement is not a valid HTML element
     */
    constructor(containerElement) {
        if (!SectionView.isValidContainerElement(containerElement)) {
            throw new TypeError('SectionView requires a valid HTML container element.');
        }

        super(containerElement, '');

        /**
         * @private
         * @type {IntersectionObserver|null}
         * @description Observer for section visibility tracking
         */
        this.intersectionObserver = null;

        /**
         * @private
         * @type {Object}
         * @description Internal state management for sections
         */
        this.sectionState = {
            renderedSections: new Map(),
            activeSection: null,
            observerInitialized: false
        };

        this.initializeIntersectionObserver();
    }

    /**
     * @brief Validates container element type and structure
     * @param {*} element - Element to validate
     * @returns {boolean} True if element is valid container
     * @static
     */
    static isValidContainerElement(element) {
        return element instanceof HTMLElement;
    }

    /**
     * @brief Renders multiple content sections with optimized batch processing
     * @param {Array<Object>} sectionsData - Array of section configuration objects
     * @returns {void}
     */
    renderSections(sectionsData) {
        if (!this.isValidSectionsData(sectionsData)) {
            console.warn('SectionView: Invalid sections data provided.');
            return;
        }

        try {
            const sectionsHTML = this.generateSectionsHTML(sectionsData);
            this.updateContainerContent(sectionsHTML);
            this.initializeSectionInteractions();
            
            console.info(`SectionView successfully rendered ${sectionsData.length} sections.`);
        } catch (error) {
            console.error('SectionView: Section rendering failed:', error);
            this.handleRenderError(error, sectionsData);
        }
    }

    /**
     * @brief Validates sections data structure and required fields
     * @param {Array<Object>} sectionsData - Sections data to validate
     * @returns {boolean} True if sections data is valid
     * @private
     */
    isValidSectionsData(sectionsData) {
        if (!Array.isArray(sectionsData)) {
            return false;
        }

        return sectionsData.every(section => 
            section && 
            typeof section === 'object' &&
            typeof section.id === 'string' &&
            section.id.trim().length > 0 &&
            typeof section.title === 'string' &&
            section.title.trim().length > 0
        );
    }

    /**
     * @brief Generates complete HTML for all sections
     * @param {Array<Object>} sectionsData - Sections configuration data
     * @returns {string} Combined HTML for all sections
     * @private
     */
    generateSectionsHTML(sectionsData) {
        return sectionsData
            .map(section => this.generateSingleSectionHTML(section))
            .join('');
    }

    /**
     * @brief Generates HTML for a single section with accessibility attributes
     * @param {Object} sectionConfig - Section configuration object
     * @param {string} sectionConfig.id - Unique section identifier
     * @param {string} sectionConfig.title - Section main title
     * @param {string} [sectionConfig.subtitle] - Optional section subtitle
     * @param {string} [sectionConfig.type] - Content type (cards, timeline, gallery, skills)
     * @param {*} [sectionConfig.content] - Section-specific content data
     * @returns {string} Generated section HTML
     * @private
     */
    generateSingleSectionHTML(sectionConfig) {
        const sectionAriaLabel = this.generateSectionAriaLabel(sectionConfig);
        
        return `
            <section id="${sectionConfig.id}" 
                     class="section" 
                     aria-labelledby="title-${sectionConfig.id}"
                     aria-label="${sectionAriaLabel}"
                     data-section-type="${sectionConfig.type || 'default'}">
                <div class="container">
                    <header class="section-header">
                        <h2 id="title-${sectionConfig.id}" class="section-title">
                            ${sectionConfig.title}
                        </h2>
                        ${sectionConfig.subtitle ? 
                            `<p class="section-subtitle">${sectionConfig.subtitle}</p>` : ''}
                    </header>
                    ${this.renderSectionContent(sectionConfig)}
                </div>
            </section>
        `;
    }

    /**
     * @brief Generates appropriate ARIA label based on section type
     * @param {Object} sectionConfig - Section configuration
     * @returns {string} ARIA label string
     * @private
     */
    generateSectionAriaLabel(sectionConfig) {
        const typeLabels = {
            cards: SECTION_CONFIG.aria.cardsLabel,
            timeline: SECTION_CONFIG.aria.timelineLabel,
            gallery: SECTION_CONFIG.aria.galleryLabel,
            skills: SECTION_CONFIG.aria.skillsLabel
        };

        return typeLabels[sectionConfig.type] || SECTION_CONFIG.aria.sectionLabel;
    }

    /**
     * @brief Renders section-specific content based on type
     * @param {Object} sectionConfig - Section configuration
     * @returns {string} Generated content HTML
     * @private
     */
    renderSectionContent(sectionConfig) {
        const contentRenderer = this.getContentRenderer(sectionConfig.type);
        return contentRenderer(sectionConfig.content);
    }

    /**
     * @brief Gets appropriate content renderer based on section type
     * @param {string} sectionType - Type of section content
     * @returns {Function} Content rendering function
     * @private
     */
    getContentRenderer(sectionType) {
        const renderers = {
            cards: this.renderCardsGrid.bind(this),
            timeline: this.renderTimeline.bind(this),
            gallery: this.renderImageGallery.bind(this),
            skills: this.renderSkillsGrid.bind(this)
        };

        return renderers[sectionType] || this.renderDefaultContent.bind(this);
    }

    /**
     * @brief Renders default content section
     * @param {string} content - HTML content string
     * @returns {string} Wrapped content HTML
     * @private
     */
    renderDefaultContent(content) {
        if (!content || typeof content !== 'string') return '';
        
        return `
            <div class="section-content">
                ${content}
            </div>
        `;
    }

    /**
     * @brief Renders responsive card grid with enhanced accessibility
     * @param {Array<Object>} cardsData - Array of card objects
     * @returns {string} Card grid HTML
     * @private
     */
    renderCardsGrid(cardsData) {
        if (!this.isValidArrayData(cardsData)) return '';

        return `
            <div class="card-grid" role="grid" aria-label="Content cards">
                ${cardsData.map((card, index) => this.renderSingleCard(card, index)).join('')}
            </div>
        `;
    }

    /**
     * @brief Renders individual card component
     * @param {Object} cardData - Card configuration object
     * @param {number} index - Card index for ARIA attributes
     * @returns {string} Single card HTML
     * @private
     */
    renderSingleCard(cardData, index) {
        return `
            <article class="card" role="gridcell" aria-labelledby="card-title-${index}">
                ${cardData.image ? 
                    `<img src="${cardData.image}" 
                          alt="${cardData.imageAlt || cardData.title}" 
                          class="card-image" 
                          loading="${SECTION_CONFIG.loadingStrategy}">` : ''}
                <div class="card-content">
                    <h3 id="card-title-${index}" class="card-title">${cardData.title}</h3>
                    ${cardData.description ? 
                        `<p class="card-description">${cardData.description}</p>` : ''}
                    ${cardData.link ? 
                        `<a href="${cardData.link}" 
                            target="${cardData.external ? '_blank' : '_self'}" 
                            rel="${cardData.external ? 'noopener noreferrer' : ''}"
                            class="btn btn-card" 
                            aria-label="Learn more about ${cardData.title}">
                            Ver Mais
                         </a>` : ''}
                </div>
            </article>
        `;
    }

    /**
     * @brief Renders accessible timeline component
     * @param {Array<Object>} timelineData - Array of timeline events
     * @returns {string} Timeline HTML
     * @private
     */
    renderTimeline(timelineData) {
        if (!this.isValidArrayData(timelineData)) return '';

        return `
            <div class="timeline" role="list" aria-label="Timeline of events">
                ${timelineData.map((event, index) => this.renderTimelineEvent(event, index)).join('')}
            </div>
        `;
    }

    /**
     * @brief Renders individual timeline event
     * @param {Object} eventData - Event configuration object
     * @param {number} index - Event index for ARIA attributes
     * @returns {string} Single timeline event HTML
     * @private
     */
    renderTimelineEvent(eventData, index) {
        return `
            <div class="timeline-item" role="listitem">
                <div class="timeline-content" aria-labelledby="timeline-title-${index}">
                    <h3 id="timeline-title-${index}" class="timeline-title">${eventData.title}</h3>
                    ${eventData.date ? 
                        `<time class="timeline-date" datetime="${this.formatDateForAccessibility(eventData.date)}">
                            ${eventData.date}
                         </time>` : ''}
                    <p class="timeline-description">${eventData.description}</p>
                </div>
            </div>
        `;
    }

    /**
     * @brief Formats date for accessibility attributes
     * @param {string} dateString - Human-readable date string
     * @returns {string} Machine-readable date string
     * @private
     */
    formatDateForAccessibility(dateString) {
        // Simple implementation - in production, use proper date parsing
        return dateString.replace(/\//g, '-');
    }

    /**
     * @brief Renders optimized image gallery with lazy loading
     * @param {Array<Object>} galleryData - Array of image objects
     * @returns {string} Gallery HTML
     * @private
     */
    renderImageGallery(galleryData) {
        if (!this.isValidArrayData(galleryData)) return '';

        return `
            <div class="gallery" role="group" aria-label="${SECTION_CONFIG.aria.galleryLabel}">
                ${galleryData.map((image, index) => this.renderGalleryImage(image, index)).join('')}
            </div>
        `;
    }

    /**
     * @brief Renders individual gallery image with caption
     * @param {Object} imageData - Image configuration object
     * @param {number} index - Image index for ARIA attributes
     * @returns {string} Single gallery item HTML
     * @private
     */
    renderGalleryImage(imageData, index) {
        return `
            <figure class="gallery-item" role="figure" aria-labelledby="gallery-caption-${index}">
                <img src="${imageData.src}" 
                     alt="${imageData.alt || 'Gallery image'}" 
                     loading="${SECTION_CONFIG.loadingStrategy}"
                     class="gallery-image">
                ${imageData.caption ? 
                    `<figcaption id="gallery-caption-${index}" class="gallery-caption">
                        ${imageData.caption}
                     </figcaption>` : ''}
            </figure>
        `;
    }

    /**
     * @brief Renders skills grid with progress indicators
     * @param {Array<Object>} skillsData - Array of skill objects
     * @returns {string} Skills grid HTML
     * @private
     */
    renderSkillsGrid(skillsData) {
        if (!this.isValidArrayData(skillsData)) return '';

        return `
            <div class="skills-grid" role="list" aria-label="${SECTION_CONFIG.aria.skillsLabel}">
                ${skillsData.map((skill, index) => this.renderSkillItem(skill, index)).join('')}
            </div>
        `;
    }

    /**
     * @brief Renders individual skill item with progress bar
     * @param {Object} skillData - Skill configuration object
     * @param {number} index - Skill index for ARIA attributes
     * @returns {string} Single skill item HTML
     * @private
     */
    renderSkillItem(skillData, index) {
        const progressBar = skillData.level ? 
            `<div class="skill-bar" role="progressbar" 
                  aria-valuenow="${skillData.level}" 
                  aria-valuemin="0" 
                  aria-valuemax="100"
                  aria-label="Progress for ${skillData.name}">
                <div class="skill-progress" style="width: ${skillData.level}%"></div>
             </div>` : '';

        return `
            <div class="skill-item" role="listitem">
                <span class="skill-name">${skillData.name}</span>
                ${progressBar}
            </div>
        `;
    }

    /**
     * @brief Validates array data for content rendering
     * @param {Array} data - Data array to validate
     * @returns {boolean} True if data is valid array
     * @private
     */
    isValidArrayData(data) {
        return Array.isArray(data) && data.length > 0;
    }

    /**
     * @brief Updates container content and manages state
     * @param {string} htmlContent - HTML content to insert
     * @private
     */
    updateContainerContent(htmlContent) {
        this.container.innerHTML = htmlContent;
        this.updateSectionState();
    }

    /**
     * @brief Updates internal section state tracking
     * @private
     */
    updateSectionState() {
        const sections = this.container.querySelectorAll(SECTION_CONFIG.selectors.section);
        this.sectionState.renderedSections.clear();
        
        sections.forEach(section => {
            this.sectionState.renderedSections.set(section.id, {
                element: section,
                type: section.dataset.sectionType,
                isVisible: false
            });
        });
    }

    /**
     * @brief Initializes intersection observer for section visibility
     * @private
     */
    initializeIntersectionObserver() {
        this.intersectionObserver = new IntersectionObserver(
            this.handleIntersection.bind(this),
            { threshold: SECTION_CONFIG.observerThreshold }
        );
        this.sectionState.observerInitialized = true;
    }

    /**
     * @brief Handles intersection observer callbacks
     * @param {Array<IntersectionObserverEntry>} entries - Observer entries
     * @private
     */
    handleIntersection = (entries) => {
        entries.forEach(entry => {
            const sectionId = entry.target.id;
            this.processSectionVisibility(entry, sectionId);
        });
    };

    /**
     * @brief Processes section visibility changes
     * @param {IntersectionObserverEntry} entry - Intersection entry
     * @param {string} sectionId - ID of the section
     * @private
     */
    processSectionVisibility(entry, sectionId) {
        if (entry.isIntersecting) {
            this.activateSection(sectionId, entry.target);
        } else {
            this.deactivateSection(sectionId);
        }
    }

    /**
     * @brief Activates section when it becomes visible
     * @param {string} sectionId - ID of the section to activate
     * @param {HTMLElement} sectionElement - Section DOM element
     * @private
     */
    activateSection(sectionId, sectionElement) {
        sectionElement.classList.add(SECTION_CONFIG.animationClass);
        this.sectionState.activeSection = sectionId;
        
        const sectionData = this.sectionState.renderedSections.get(sectionId);
        if (sectionData) {
            sectionData.isVisible = true;
        }

        this.notify('sectionVisible', { 
            sectionId,
            sectionType: sectionElement.dataset.sectionType,
            timestamp: Date.now()
        });
    }

    /**
     * @brief Deactivates section when it leaves viewport
     * @param {string} sectionId - ID of the section to deactivate
     * @private
     */
    deactivateSection(sectionId) {
        const sectionData = this.sectionState.renderedSections.get(sectionId);
        if (sectionData) {
            sectionData.isVisible = false;
        }
    }

    /**
     * @brief Initializes all section interactions and observers
     * @private
     */
    initializeSectionInteractions() {
        this.observeAllSections();
        this.initializeSectionEventHandlers();
    }

    /**
     * @brief Starts observing all rendered sections
     * @private
     */
    observeAllSections() {
        const sections = this.container.querySelectorAll(SECTION_CONFIG.selectors.section);
        sections.forEach(section => {
            this.intersectionObserver.observe(section);
        });
    }

    /**
     * @brief Initializes event handlers for section interactions
     * @private
     */
    initializeSectionEventHandlers() {
        this.initializeCardInteractions();
        this.initializeGalleryInteractions();
    }

    /**
     * @brief Initializes card-specific event handlers
     * @private
     */
    initializeCardInteractions() {
        this.addEvent('click', '.card .btn-card', (event) => {
            const card = event.target.closest('.card');
            const cardTitle = card?.querySelector('.card-title')?.textContent;
            
            this.notify('cardInteraction', {
                action: 'click',
                cardTitle,
                timestamp: Date.now()
            });
        });
    }

    /**
     * @brief Initializes gallery-specific event handlers
     * @private
     */
    initializeGalleryInteractions() {
        this.addEvent('click', '.gallery-image', (event) => {
            const image = event.target;
            const caption = image.parentElement.querySelector('.gallery-caption')?.textContent;
            
            this.notify('galleryImageClick', {
                imageSrc: image.src,
                imageAlt: image.alt,
                caption,
                timestamp: Date.now()
            });
        });
    }

    /**
     * @brief Handles rendering errors gracefully
     * @param {Error} error - Error encountered during rendering
     * @param {Array} sectionsData - Original sections data for recovery
     * @private
     */
    handleRenderError(error, sectionsData) {
        this.notify('sectionRenderError', {
            error: error.message,
            sectionsCount: sectionsData?.length || 0,
            timestamp: Date.now()
        });

        // Fallback: render basic sections without advanced features
        if (sectionsData) {
            const fallbackHTML = sectionsData.map(section => `
                <section id="${section.id}">
                    <h2>${section.title}</h2>
                    ${section.subtitle ? `<p>${section.subtitle}</p>` : ''}
                </section>
            `).join('');
            
            this.container.innerHTML = fallbackHTML;
        }
    }

    /**
     * @brief Cleans up observers and event listeners
     * @returns {void}
     */
    destroy() {
        if (this.intersectionObserver) {
            this.intersectionObserver.disconnect();
            this.intersectionObserver = null;
        }

        this.sectionState.renderedSections.clear();
        this.sectionState.activeSection = null;
        this.sectionState.observerInitialized = false;

        console.info('SectionView instance cleaned up successfully.');
    }
}

export default SectionView;