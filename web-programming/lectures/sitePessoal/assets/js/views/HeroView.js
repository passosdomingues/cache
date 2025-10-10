/**
 * @file HeroView.js
 * @author Rafael Passos Domingues
 * @version 3.0.0
 * @brief Enhanced Hero section view with improved modularity, accessibility, and performance
 * @description Renders the main hero section with professional profile, smooth scroll interactions,
 *              and optimized UX/UI patterns. Implements atomic design principles and modern ES6+ features.
 */

import BaseView from './BaseView.js';

// Configuration constants for maintainability
const HERO_CONFIG = {
    scrollBehavior: 'smooth',
    imageLoading: 'lazy',
    animationDuration: 300,
    selectors: {
        buttonsContainer: '.hero-buttons',
        primaryButton: '.btn-primary',
        secondaryButton: '.btn-secondary',
        profileImage: '.profile-image'
    },
    ariaLabels: {
        projectsButton: 'Navigate to projects section',
        contactButton: 'Navigate to contact section',
        profileImage: 'Professional profile picture'
    }
};

/**
 * @class HeroView
 * @extends BaseView
 * @brief Enhanced hero section view component
 * @description Handles rendering and interactions for the main hero section with
 *              improved accessibility, performance, and user experience patterns
 */
class HeroView extends BaseView {
    /**
     * @brief Creates a new HeroView instance
     * @param {HTMLElement} containerElement - Section element with ID "hero" for content rendering
     * @throws {TypeError} When containerElement is not a valid HTML element
     */
    constructor(containerElement) {
        if (!HeroView.isValidHTMLElement(containerElement)) {
            throw new TypeError('HeroView requires a valid HTML container element.');
        }

        const heroTemplate = HeroView.generateTemplate();
        super(containerElement, heroTemplate);

        /**
         * @private
         * @type {Object}
         * @description Internal state management for hero section
         */
        this.state = {
            isRendered: false,
            lastRenderData: null
        };
    }

    /**
     * @brief Validates if provided element is a proper HTML element
     * @param {*} element - Element to validate
     * @returns {boolean} True if element is valid HTML element
     * @static
     */
    static isValidHTMLElement(element) {
        return element instanceof HTMLElement;
    }

    /**
     * @brief Generates the hero section HTML template with placeholders
     * @returns {string} Complete HTML template string
     * @static
     */
    static generateTemplate() {
        return `
            <div class="hero-container" role="banner">
                <div class="hero-content">
                    <div class="hero-text">
                        <h1 class="hero-title" data-testid="hero-title">{{name}}</h1>
                        <p class="hero-subtitle" data-testid="hero-subtitle">{{title}}</p>
                        <p class="hero-description" data-testid="hero-description">{{summary}}</p>
                        <div class="hero-buttons">
                            <a href="#projects" 
                               class="btn btn-primary" 
                               aria-label="${HERO_CONFIG.ariaLabels.projectsButton}"
                               data-testid="projects-button">
                                Ver Projetos
                            </a>
                            <a href="#contact" 
                               class="btn btn-secondary"
                               aria-label="${HERO_CONFIG.ariaLabels.contactButton}"
                               data-testid="contact-button">
                                Entrar em Contato
                            </a>
                        </div>
                    </div>
                    <div class="hero-image">
                        <img src="{{profileImage}}" 
                             alt="Foto de {{name}}" 
                             class="profile-image" 
                             loading="${HERO_CONFIG.imageLoading}"
                             aria-label="${HERO_CONFIG.ariaLabels.profileImage}"
                             data-testid="profile-image">
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * @brief Renders hero section with user profile data
     * @param {Object} userProfileData - User profile information for display
     * @param {string} userProfileData.name - Full name of the user
     * @param {string} userProfileData.title - Professional title or role
     * @param {string} userProfileData.summary - Professional summary or bio
     * @param {string} userProfileData.profileImage - URL or path to profile image
     * @returns {void}
     */
    render(userProfileData) {
        if (!this.isValidUserData(userProfileData)) {
            console.warn('HeroView: Invalid user data provided for rendering.');
            return;
        }

        try {
            super.render(userProfileData);
            this.initializeComponent();
            this.updateStateAfterRender(userProfileData);
            
            console.info('HeroView successfully rendered with enhanced features.');
        } catch (error) {
            console.error('HeroView: Rendering failed:', error);
            this.handleRenderError(error);
        }
    }

    /**
     * @brief Validates user data structure and required fields
     * @param {Object} userData - User data object to validate
     * @returns {boolean} True if user data is valid and complete
     * @private
     */
    isValidUserData(userData) {
        if (typeof userData !== 'object' || userData === null) {
            return false;
        }

        const requiredFields = ['name', 'title', 'summary', 'profileImage'];
        return requiredFields.every(field => 
            userData.hasOwnProperty(field) && 
            typeof userData[field] === 'string' && 
            userData[field].trim().length > 0
        );
    }

    /**
     * @brief Initializes component functionality after DOM rendering
     * @private
     */
    initializeComponent() {
        this.initializeSmoothScroll();
        this.initializeImageOptimization();
        this.initializeAccessibilityFeatures();
    }

    /**
     * @brief Sets up smooth scroll behavior for navigation buttons
     * @private
     */
    initializeSmoothScroll() {
        this.addEvent('click', HERO_CONFIG.selectors.buttonsContainer, (event) => {
            this.handleButtonClick(event);
        });
    }

    /**
     * @brief Handles button click events with smooth scroll and analytics
     * @param {Event} event - DOM click event
     * @private
     */
    handleButtonClick = (event) => {
        const clickedButton = event.target.closest('a');
        if (!clickedButton) return;

        event.preventDefault();
        
        const targetSectionId = this.extractTargetSectionId(clickedButton);
        if (!targetSectionId) return;

        this.processSmoothNavigation(targetSectionId, clickedButton);
    };

    /**
     * @brief Extracts target section ID from button href attribute
     * @param {HTMLAnchorElement} buttonElement - Clicked button element
     * @returns {string|null} Target section ID or null if invalid
     * @private
     */
    extractTargetSectionId(buttonElement) {
        const href = buttonElement.getAttribute('href');
        if (!href || !href.startsWith('#')) return null;

        const targetId = href.substring(1);
        return targetId.trim() || null;
    }

    /**
     * @brief Processes smooth navigation to target section
     * @param {string} targetSectionId - ID of section to navigate to
     * @param {HTMLAnchorElement} sourceButton - Button that triggered navigation
     * @private
     */
    processSmoothNavigation(targetSectionId, sourceButton) {
        this.notify('scrollToSection', { 
            sectionId: targetSectionId,
            source: 'hero',
            buttonType: sourceButton.className.includes('primary') ? 'primary' : 'secondary'
        });

        this.executeSmoothScroll(targetSectionId);
        this.triggerButtonAnalytics(sourceButton, targetSectionId);
    }

    /**
     * @brief Executes smooth scroll to target section
     * @param {string} targetSectionId - ID of target section element
     * @private
     */
    executeSmoothScroll(targetSectionId) {
        const targetSection = document.getElementById(targetSectionId);
        if (targetSection) {
            targetSection.scrollIntoView({ 
                behavior: HERO_CONFIG.scrollBehavior,
                block: 'start'
            });
        }
    }

    /**
     * @brief Triggers analytics for button interactions
     * @param {HTMLAnchorElement} button - Clicked button element
     * @param {string} targetSection - Target section identifier
     * @private
     */
    triggerButtonAnalytics(button, targetSection) {
        // Analytics integration point
        this.notify('heroButtonClick', {
            buttonType: button.className.includes('primary') ? 'projects' : 'contact',
            targetSection: targetSection,
            timestamp: Date.now()
        });
    }

    /**
     * @brief Initializes image optimization and loading handlers
     * @private
     */
    initializeImageOptimization() {
        const profileImage = this.element.querySelector(HERO_CONFIG.selectors.profileImage);
        if (profileImage) {
            this.handleImageLoading(profileImage);
        }
    }

    /**
     * @brief Handles profile image loading with error fallback
     * @param {HTMLImageElement} imageElement - Profile image element
     * @private
     */
    handleImageLoading = (imageElement) => {
        imageElement.addEventListener('load', () => {
            this.notify('heroImageLoaded', { 
                success: true,
                imageSrc: imageElement.src 
            });
        });

        imageElement.addEventListener('error', () => {
            console.warn('HeroView: Profile image failed to load, using fallback.');
            this.handleImageLoadError(imageElement);
        });
    };

    /**
     * @brief Handles profile image loading errors with fallback strategy
     * @param {HTMLImageElement} imageElement - Failed image element
     * @private
     */
    handleImageLoadError(imageElement) {
        const fallbackImage = this.generateFallbackImage();
        imageElement.src = fallbackImage;
        imageElement.alt = 'Default profile image';
        
        this.notify('heroImageError', {
            originalSrc: imageElement.dataset.originalSrc,
            fallbackUsed: true
        });
    }

    /**
     * @brief Generates fallback image URL or data URI
     * @returns {string} Fallback image source
     * @private
     */
    generateFallbackImage() {
        // Return a generic placeholder image or data URI
        return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PC9zdmc+';
    }

    /**
     * @brief Initializes accessibility features and ARIA attributes
     * @private
     */
    initializeAccessibilityFeatures() {
        this.enhanceKeyboardNavigation();
        this.initializeFocusManagement();
    }

    /**
     * @brief Enhances keyboard navigation for hero section
     * @private
     */
    enhanceKeyboardNavigation() {
        this.element.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                this.handleKeyboardNavigation(event);
            }
        });
    }

    /**
     * @brief Handles keyboard navigation events
     * @param {KeyboardEvent} event - Keyboard event
     * @private
     */
    handleKeyboardNavigation = (event) => {
        const interactiveElement = event.target.closest('a, button');
        if (interactiveElement && interactiveElement.getAttribute('href')?.startsWith('#')) {
            event.preventDefault();
            this.handleButtonClick(event);
        }
    };

    /**
     * @brief Initializes focus management for better accessibility
     * @private
     */
    initializeFocusManagement() {
        // Set initial focus to hero section for screen readers
        this.element.setAttribute('tabindex', '-1');
        this.element.focus();
    }

    /**
     * @brief Updates internal state after successful render
     * @param {Object} renderedData - Data used in the render operation
     * @private
     */
    updateStateAfterRender(renderedData) {
        this.state.isRendered = true;
        this.state.lastRenderData = { ...renderedData };
    }

    /**
     * @brief Handles rendering errors gracefully
     * @param {Error} error - Error encountered during rendering
     * @private
     */
    handleRenderError(error) {
        this.state.isRendered = false;
        this.notify('heroRenderError', {
            error: error.message,
            timestamp: Date.now()
        });
    }

    /**
     * @brief Cleans up event listeners and state
     * @returns {void}
     */
    destroy() {
        // Cleanup any specific event listeners or timeouts
        this.state.isRendered = false;
        this.state.lastRenderData = null;
        
        console.info('HeroView instance cleaned up successfully.');
    }
}

export default HeroView;