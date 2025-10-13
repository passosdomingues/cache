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
        skillsGrid: '.skills-grid',
        dynamicContentArea: '.dynamic-content-area' // New selector for dynamic content insertion
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
     * @public
     * @param {Array<Object>} sectionsData - Array of section configuration objects
     * @returns {Promise<string>} Resolves with the combined HTML for all sections.
     */
    async render(sectionsData) {
        if (!this.isValidSectionsData(sectionsData)) {
            console.warn('SectionView: Invalid sections data provided for render.');
            return '';
        }

        try {
            const sectionsHTML = this.generateSectionsHTML(sectionsData);
            // The ViewManager will update the container with this HTML
            // We then need to initialize interactions after the DOM is updated
            // this.updateContainerContent(sectionsHTML); // This is now handled by ViewManager
            // this.initializeSectionInteractions(); // This will be called by SectionController after DOM update
            
            console.info(`SectionView successfully generated HTML for ${sectionsData.length} sections.`);
            return sectionsHTML;
        } catch (error) {
            console.error('SectionView: Section rendering failed in render:', error);
            this.handleRenderError(error, sectionsData);
            return ''; // Return empty string on error
        }
    }

    /**
     * @brief Renders multiple content sections with optimized batch processing
     * @public
     * @param {Array<Object>} sectionsData - Array of section configuration objects
     * @returns {Promise<void>} Resolves when all sections are rendered.
     */
    async renderAllSections(sectionsData) {
        if (!this.isValidSectionsData(sectionsData)) {
            console.warn('SectionView: Invalid sections data provided for renderAllSections.');
            return;
        }

        try {
            const sectionsHTML = this.generateSectionsHTML(sectionsData);
            this.updateContainerContent(sectionsHTML);
            // After rendering the section structures, dynamically load their content
            for (const section of sectionsData) {
                if (section.content) {
                    await this.renderSectionContent(section.id, section.type, section.content);
                }
            }
            this.initializeSectionInteractions();
            
            console.info(`SectionView successfully rendered ${sectionsData.length} sections.`);
        } catch (error) {
            console.error('SectionView: Section rendering failed in renderAllSections:', error);
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
     * @returns {string} Generated section HTML
     * @private
     */
    generateSingleSectionHTML(sectionConfig) {
        const sectionAriaLabel = this.generateSectionAriaLabel(sectionConfig);
        
        // The dynamic-content-area will be populated later by renderSectionContent
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
                    <div class="dynamic-content-area" data-section-id="${sectionConfig.id}">
                        <!-- Dynamic content will be loaded here by SectionController -->
                    </div>
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
            projects: SECTION_CONFIG.aria.cardsLabel, // Projects will be rendered as cards
            experiences: SECTION_CONFIG.aria.timelineLabel, // Experiences will be rendered as timeline
            research: SECTION_CONFIG.aria.cardsLabel, // Research will be rendered as cards
            timeline: SECTION_CONFIG.aria.timelineLabel, // Explicit timeline
            gallery: SECTION_CONFIG.aria.galleryLabel,
            skills: SECTION_CONFIG.aria.skillsLabel
        };

        return typeLabels[sectionConfig.type] || SECTION_CONFIG.aria.sectionLabel;
    }

    /**
     * @brief Renders section-specific content based on type into the designated area.
     * @public
     * @param {string} sectionId - The ID of the section to render content into.
     * @param {string} contentType - Type of content (e.g., 'projects', 'experiences', 'timeline').
     * @param {Array<Object>} contentData - Data to render for the specific content type.
     * @returns {Promise<void>} Resolves when content is rendered.
     */
    async renderSectionContent(sectionId, contentType, contentData) {
        const sectionElement = this.container.querySelector(`#${sectionId}`);
        if (!sectionElement) {
            console.warn(`SectionView: Section element not found for ID: ${sectionId}`);
            return;
        }

        const dynamicContentArea = sectionElement.querySelector(SECTION_CONFIG.selectors.dynamicContentArea);
        if (!dynamicContentArea) {
            console.warn(`SectionView: Dynamic content area not found for section ID: ${sectionId}`);
            return;
        }

        let contentHTML = '';
        switch (contentType) {
            case 'projects':
            case 'research':
            case 'astrophysics-research':
            case 'innovation-entrepreneurship':
            case 'deep-learning-projects':
            case 'hobbies':
                contentHTML = this.renderCardsGrid(contentData);
                break;
            case 'experiences':
            case 'timeline':
            case 'about':
            case 'education-experience':
                contentHTML = this.renderTimeline(contentData);
                break;
            case 'gallery':
                contentHTML = this.renderImageGallery(contentData);
                break;
            case 'skills':
                contentHTML = this.renderSkillsGrid(contentData);
                break;
            default:
                console.warn(`SectionView: Unknown content type for rendering: ${contentType}`);
                contentHTML = `<p>No specific content renderer for type: ${contentType}</p>`;
                break;
        }

        dynamicContentArea.innerHTML = contentHTML;
        console.debug(`SectionView: Rendered dynamic content for section ${sectionId} of type ${contentType}.`);
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
                    ${cardData.image && cardData.image.src ? 
                        `<figure class="card-image-container">
                            <img src="${cardData.image.src}" 
                                  alt="${cardData.image.alt || cardData.title}" 
                                  class="card-image" 
                                  loading="${SECTION_CONFIG.loadingStrategy}">
                            ${cardData.image.caption ? `<figcaption class="card-image-caption">${cardData.image.caption}</figcaption>` : ''}
                        </figure>` : ''}
                <div class="card-content">
                    ${cardData.icon ? 
                        `<i class="fas fa-${cardData.icon} neon-icon" aria-hidden="true"></i>` : ''}
                    <h3 id="card-title-${index}" class="card-title">${cardData.title}</h3>
                    ${cardData.description ? 
                        `<p class="card-description">${cardData.description}</p>` : ''}
                    ${cardData.highlights && cardData.highlights.length > 0 ? 
                        `<ul class="card-highlights">
                            ${cardData.highlights.map(highlight => `<li>${highlight}</li>`).join('')}
                         </ul>` : ''}
                    ${cardData.links && cardData.links.length > 0 ? 
                        `<div class="card-links">
                            ${cardData.links.map(link => 
                                `<a href="${link.url}" 
                                    target="${link.type === 'external' ? '_blank' : '_self'}" 
                                    rel="${link.type === 'external' ? 'noopener noreferrer' : ''}"
                                    class="btn btn-card btn-small" 
                                    aria-label="${link.label}">
                                    ${link.label}
                                 </a>`
                            ).join('')}
                         </div>` : ''}
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
                    ${eventData.highlights && eventData.highlights.length > 0 ? 
                        `<ul class="timeline-highlights">
                            ${eventData.highlights.map(highlight => `<li>${highlight}</li>`).join("")}
                         </ul>` : ""}
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
            <div class="gallery" role="region" aria-label="${SECTION_CONFIG.aria.galleryLabel}">
                ${galleryData.map((image, index) => this.renderGalleryImage(image, index)).join('')}
            </div>
        `;
    }

    /**
     * @brief Renders individual gallery image
     * @param {Object} imageData - Image configuration object
     * @param {number} index - Image index for ARIA attributes
     * @returns {string} Single gallery image HTML
     * @private
     */
    renderGalleryImage(imageData, index) {
        return `
            <figure class="gallery-item" role="figure" aria-labelledby="gallery-caption-${index}">
                <img src="${imageData.src}" 
                     alt="${imageData.alt}" 
                     class="gallery-image" 
                     loading="${SECTION_CONFIG.loadingStrategy}">
                <figcaption id="gallery-caption-${index}" class="gallery-caption">
                    ${imageData.caption}
                </figcaption>
            </figure>
        `;
    }

    /**
     * @brief Renders skills grid with icons and levels
     * @param {Array<Object>} skillsData - Array of skill objects
     * @returns {string} Skills grid HTML
     * @private
     */
    renderSkillsGrid(skillsData) {
        if (!this.isValidArrayData(skillsData)) return '';

        return `
            <div class="skills-grid" role="list" aria-label="${SECTION_CONFIG.aria.skillsLabel}">
                ${skillsData.map(skill => this.renderSkillItem(skill)).join('')}
            </div>
        `;
    }

    /**
     * @brief Renders individual skill item
     * @param {Object} skillData - Skill configuration object
     * @returns {string} Single skill item HTML
     * @private
     */
    renderSkillItem(skillData) {
        return `
            <div class="skill-item" role="listitem">
                <i class="${skillData.icon} skill-icon" aria-hidden="true"></i>
                <span class="skill-name">${skillData.name}</span>
                <div class="skill-level-bar" role="meter" aria-valuenow="${skillData.level}" aria-valuemin="0" aria-valuemax="100">
                    <div class="skill-level-fill" style="width: ${skillData.level}%;"></div>
                </div>
            </div>
        `;
    }

    /**
     * @brief Initializes intersection observer for section visibility
     * @private
     */
    initializeIntersectionObserver() {
        if (this.sectionState.observerInitialized) return;

        const observerOptions = {
            root: null,
            rootMargin: '0px',
            threshold: SECTION_CONFIG.observerThreshold
        };

        this.intersectionObserver = new IntersectionObserver(
            this.handleIntersection.bind(this),
            observerOptions
        );

        this.sectionState.observerInitialized = true;
    }

    /**
     * @brief Initializes interactions for all rendered sections
     * @private
     */
    initializeSectionInteractions() {
        const sections = this.container.querySelectorAll(SECTION_CONFIG.selectors.section);
        sections.forEach(section => {
            if (this.intersectionObserver) {
                this.intersectionObserver.observe(section);
            }
        });
    }

    /**
     * @brief Handles intersection observer events
     * @param {Array<IntersectionObserverEntry>} entries - Observer entries
     * @private
     */
    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add(SECTION_CONFIG.animationClass);
                this.notifyVisibilityChange(entry.target.id, true, entry.intersectionRatio);
            } else {
                entry.target.classList.remove(SECTION_CONFIG.animationClass);
                this.notifyVisibilityChange(entry.target.id, false, entry.intersectionRatio);
            }
        });
    }

    /**
     * @brief Notifies observers about section visibility changes
     * @param {string} sectionId - ID of the section
     * @param {boolean} isVisible - Visibility status
     * @param {number} intersectionRatio - Intersection ratio
     * @private
     */
    notifyVisibilityChange(sectionId, isVisible, intersectionRatio) {
        this.notify({
            type: isVisible ? 'sectionVisible' : 'sectionHidden',
            data: { sectionId, intersectionRatio }
        });
    }

    /**
     * @brief Handles rendering errors gracefully
     * @param {Error} error - The rendering error
     * @param {Array<Object>} sectionsData - The data that failed to render
     * @private
     */
    handleRenderError(error, sectionsData) {
        console.error('SectionView: An error occurred during rendering:', error);
        this.notify({ type: 'error', data: { error, context: 'renderAllSections', sectionsData } });
    }

    /**
     * @brief Utility to check if data is a non-empty array
     * @param {*} data - Data to validate
     * @returns {boolean} True if data is a non-empty array
     * @private
     */
    isValidArrayData(data) {
        return Array.isArray(data) && data.length > 0;
    }

    /**
     * @brief Cleans up resources and observers
     * @public
     */
    cleanup() {
        if (this.intersectionObserver) {
            this.intersectionObserver.disconnect();
            this.intersectionObserver = null;
        }
        super.cleanup();
    }
}

export default SectionView;

