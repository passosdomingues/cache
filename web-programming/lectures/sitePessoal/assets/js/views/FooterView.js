/**
 * @file FooterView.js
 * @author Rafael Passos Domingues
 * @version 3.0.0
 * @brief View responsible for rendering the website footer with dynamic content.
 * @description Extends BaseView to render footer content including social links,
 * contact information, copyright with current year, and additional credits
 * with accessibility features and performance optimizations.
 */

import BaseView from './BaseView.js';

/**
 * @constant {Object} FOOTER_CONFIGURATION
 * @brief Configuration constants for footer structure and behavior
 * @description Defines social media platforms, accessibility labels, and template structure
 */
const FOOTER_CONFIGURATION = {
    SOCIAL_PLATFORMS: [
        {
            platform: 'GitHub',
            icon: 'github',
            ariaLabel: 'Visit GitHub profile',
            rel: 'noopener noreferrer',
            target: '_blank',
            urlTemplate: '{{github}}',
            priority: 1
        },
        {
            platform: 'LinkedIn',
            icon: 'linkedin-in',
            ariaLabel: 'Visit LinkedIn profile',
            rel: 'noopener noreferrer',
            target: '_blank',
            urlTemplate: '{{linkedin}}',
            priority: 2
        },
        {
            platform: 'Instagram',
            icon: 'instagram',
            ariaLabel: 'Visit Instagram profile',
            rel: 'noopener noreferrer',
            target: '_blank',
            urlTemplate: 'https://instagram.com/{{instagram}}',
            priority: 3
        },
        {
            platform: 'Email',
            icon: 'envelope',
            ariaLabel: 'Send email',
            rel: null,
            target: null,
            urlTemplate: 'mailto:{{email}}',
            priority: 4
        }
    ],
    ACCESSIBILITY: {
        footerLabel: 'Site footer',
        socialLinksLabel: 'Social media links',
        creditsLabel: 'Additional resources and credits'
    },
    TEMPLATE_CLASSES: {
        container: 'footer-container',
        content: 'footer-content',
        socialLinks: 'social-links',
        socialLink: 'social-link',
        footerText: 'footer-text',
        credits: 'footer-credits',
        copyright: 'footer-copyright'
    }
};

/**
 * @class FooterView
 * @brief Footer view component extending BaseView with dynamic content rendering
 * @description Handles footer rendering with social links, contact information,
 * copyright notice, and credits with accessibility features and performance optimizations
 */
class FooterView extends BaseView {
    /**
     * @brief Creates a FooterView instance
     * @constructor
     * @param {HTMLElement} containerElement - Footer DOM element where content will be rendered
     * @param {Object} options - Configuration options for footer behavior
     * @param {boolean} options.autoRender - Whether to auto-render on construction
     * @param {boolean} options.enableSocialLinks - Whether to render social media links
     * @param {boolean} options.showCurrentYear - Whether to display current year in copyright
     * @throws {TypeError} When containerElement is not a valid HTMLElement
     */
    constructor(containerElement, options = {}) {
        super(containerElement, '', {
            autoRender: options.autoRender || false,
            enableSanitization: true
        });

        this.validateFooterContainer(containerElement);

        const {
            enableSocialLinks = true,
            showCurrentYear = true
        } = options;

        /**
         * @private
         * @type {Object}
         * @brief Footer-specific configuration options
         */
        this.footerConfiguration = {
            enableSocialLinks,
            showCurrentYear,
            currentYear: showCurrentYear ? new Date().getFullYear() : null
        };

        /**
         * @private
         * @type {string}
         * @brief Cached template for performance optimization
         */
        this.cachedTemplate = this.generateFooterTemplate();

        // Update BaseView template with generated footer template
        this.updateTemplate(this.cachedTemplate, false);

        console.debug('FooterView: Footer view instance created.');
    }

    /**
     * @brief Validates that the container element is appropriate for footer content
     * @private
     * @param {HTMLElement} containerElement - Container element to validate
     * @throws {TypeError} When container element is not suitable for footer content
     */
    validateFooterContainer(containerElement) {
        if (!containerElement || !(containerElement instanceof HTMLElement)) {
            throw new TypeError('FooterView requires a valid HTMLElement container.');
        }

        // Suggest using footer element for semantic correctness
        if (containerElement.tagName !== 'FOOTER') {
            console.warn('FooterView: Container element is not a <footer> element. Consider using a semantic footer element for better accessibility.');
        }
    }

    /**
     * @brief Generates the complete footer template with dynamic sections
     * @private
     * @returns {string} Complete footer HTML template string
     */
    generateFooterTemplate() {
        const {
            container,
            content,
            socialLinks,
            footerText,
            credits,
            copyright
        } = FOOTER_CONFIGURATION.TEMPLATE_CLASSES;

        return `
            <div class="${container}" role="contentinfo" aria-label="${FOOTER_CONFIGURATION.ACCESSIBILITY.footerLabel}">
                <div class="${content}">
                    ${this.generateSocialLinksSection()}
                    ${this.generateCopyrightSection()}
                    ${this.generateCreditsSection()}
                </div>
            </div>
        `;
    }

    /**
     * @brief Generates social media links section HTML
     * @private
     * @returns {string} Social links section HTML string
     */
    generateSocialLinksSection() {
        if (!this.footerConfiguration.enableSocialLinks) {
            return '';
        }

        const socialLinksHtml = FOOTER_CONFIGURATION.SOCIAL_PLATFORMS
            .sort((a, b) => a.priority - b.priority)
            .map(platform => this.generateSocialLinkHtml(platform))
            .join('');

        return `
            <div class="${FOOTER_CONFIGURATION.TEMPLATE_CLASSES.socialLinks}" 
                 aria-label="${FOOTER_CONFIGURATION.ACCESSIBILITY.socialLinksLabel}"
                 role="list">
                ${socialLinksHtml}
            </div>
        `;
    }

    /**
     * @brief Generates individual social media link HTML
     * @private
     * @param {Object} platformConfig - Social platform configuration
     * @returns {string} Social link HTML string
     */
    generateSocialLinkHtml(platformConfig) {
        const {
            platform,
            icon,
            ariaLabel,
            rel,
            target,
            urlTemplate
        } = platformConfig;

        const relAttribute = rel ? `rel="${rel}"` : '';
        const targetAttribute = target ? `target="${target}"` : '';

        return `
            <a href="${urlTemplate}" 
               class="${FOOTER_CONFIGURATION.TEMPLATE_CLASSES.socialLink} ${FOOTER_CONFIGURATION.TEMPLATE_CLASSES.socialLink}--${platform.toLowerCase()}"
               ${targetAttribute}
               ${relAttribute}
               aria-label="${ariaLabel}"
               data-platform="${platform.toLowerCase()}"
               role="listitem">
                <i class="fab fa-${icon}" aria-hidden="true"></i>
                <span class="visually-hidden">${platform}</span>
            </a>
        `;
    }

    /**
     * @brief Generates copyright section HTML with dynamic year
     * @private
     * @returns {string} Copyright section HTML string
     */
    generateCopyrightSection() {
        const yearText = this.footerConfiguration.showCurrentYear 
            ? `&copy; ${this.footerConfiguration.currentYear} {{name}}.`
            : '&copy; {{name}}.';

        return `
            <div class="${FOOTER_CONFIGURATION.TEMPLATE_CLASSES.copyright}">
                <p class="${FOOTER_CONFIGURATION.TEMPLATE_CLASSES.footerText}">
                    ${yearText} All rights reserved.
                </p>
            </div>
        `;
    }

    /**
     * @brief Generates credits and additional links section HTML
     * @private
     * @returns {string} Credits section HTML string
     */
    generateCreditsSection() {
        return `
            <div class="${FOOTER_CONFIGURATION.TEMPLATE_CLASSES.credits}" 
                 aria-label="${FOOTER_CONFIGURATION.ACCESSIBILITY.creditsLabel}">
                <p>
                    <a href="{{site}}" 
                       target="_blank" 
                       rel="noopener noreferrer"
                       aria-label="Visit Professor website - Pandefísica">
                        Professor Website - Pandefísica
                    </a>
                </p>
            </div>
        `;
    }

    /**
     * @brief Renders footer content with author data and sets up interactivity
     * @public
     * @param {Object} authorData - Object containing author information for template interpolation
     * @param {string} authorData.name - Author's full name for copyright
     * @param {string} authorData.github - GitHub profile URL
     * @param {string} authorData.linkedin - LinkedIn profile URL
     * @param {string} authorData.instagram - Instagram username
     * @param {string} authorData.email - Email address for contact
     * @param {string} authorData.site - Primary website URL
     * @param {Object} options - Rendering options
     * @param {boolean} options.setupEventHandlers - Whether to set up footer event handlers
     * @returns {Promise<void>} Resolves when footer is successfully rendered
     * @throws {Error} When author data is invalid or rendering fails
     */
    async render(authorData = {}, options = {}) {
        const { setupEventHandlers = true } = options;

        try {
            this.validateAuthorData(authorData);

            // Render footer content with author data
            await super.render(authorData);

            // Set up event handlers if requested
            if (setupEventHandlers) {
                await this.setupFooterEventHandlers();
            }

            // Update footer-specific attributes
            this.updateFooterAccessibility();

            // Notify observers of successful render
            this.notifyObservers('footer:rendered', {
                authorName: authorData.name,
                socialPlatforms: FOOTER_CONFIGURATION.SOCIAL_PLATFORMS.map(p => p.platform),
                timestamp: Date.now()
            });

            console.info('FooterView: Footer rendered successfully with author data.');

        } catch (error) {
            console.error('FooterView: Footer rendering failed:', error);
            
            this.notifyObservers('footer:error', {
                error: error.message,
                authorData,
                operation: 'render'
            });

            throw error;
        }
    }

    /**
     * @brief Validates author data for template interpolation
     * @private
     * @param {Object} authorData - Author data object to validate
     * @throws {TypeError} When author data is invalid or missing required fields
     */
    validateAuthorData(authorData) {
        if (!authorData || typeof authorData !== 'object') {
            throw new TypeError('FooterView: Author data must be a valid object.');
        }

        const requiredFields = ['name', 'github', 'linkedin', 'instagram', 'email', 'site'];
        const missingFields = requiredFields.filter(field => !authorData[field]);

        if (missingFields.length > 0) {
            throw new TypeError(`FooterView: Missing required author data fields: ${missingFields.join(', ')}`);
        }

        // Validate URL formats
        this.validateSocialUrls(authorData);
    }

    /**
     * @brief Validates social media URLs for proper format
     * @private
     * @param {Object} authorData - Author data containing social URLs
     * @throws {TypeError} When social URLs are invalid
     */
    validateSocialUrls(authorData) {
        const urlValidators = {
            github: (url) => url.startsWith('https://github.com/') || url.startsWith('https://www.github.com/'),
            linkedin: (url) => url.startsWith('https://linkedin.com/') || url.startsWith('https://www.linkedin.com/'),
            site: (url) => url.startsWith('https://') || url.startsWith('http://')
        };

        Object.keys(urlValidators).forEach(platform => {
            if (authorData[platform] && !urlValidators[platform](authorData[platform])) {
                console.warn(`FooterView: ${platform} URL may be invalid: ${authorData[platform]}`);
            }
        });

        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (authorData.email && !emailRegex.test(authorData.email)) {
            console.warn(`FooterView: Email address may be invalid: ${authorData.email}`);
        }
    }

    /**
     * @brief Sets up event handlers for footer interactive elements
     * @private
     * @returns {Promise<void>} Resolves when event handlers are set up
     */
    async setupFooterEventHandlers() {
        try {
            // Set up social link click tracking
            this.setupSocialLinkTracking();

            // Set up email link handler
            this.setupEmailLinkHandler();

            // Set up external link safety handlers
            this.setupExternalLinkHandlers();

            console.debug('FooterView: Footer event handlers initialized.');

        } catch (error) {
            console.error('FooterView: Failed to set up footer event handlers:', error);
            throw error;
        }
    }

    /**
     * @brief Sets up click tracking for social media links
     * @private
     */
    setupSocialLinkTracking() {
        const socialLinkSelector = `.${FOOTER_CONFIGURATION.TEMPLATE_CLASSES.socialLink}`;
        
        this.addEventListener('click', socialLinkSelector, (event, context) => {
            const socialLink = event.currentTarget;
            const platform = socialLink.getAttribute('data-platform');
            const href = socialLink.getAttribute('href');

            this.handleSocialLinkClick(platform, href, event);

            // Notify observers of social link interaction
            this.notifyObservers('footer:socialLinkClicked', {
                platform,
                href,
                timestamp: Date.now(),
                eventType: 'click'
            });
        });
    }

    /**
     * @brief Handles social media link click events
     * @private
     * @param {string} platform - Social media platform identifier
     * @param {string} href - Link URL that was clicked
     * @param {Event} event - Original click event
     */
    handleSocialLinkClick(platform, href, event) {
        console.debug(`FooterView: Social link clicked - Platform: ${platform}, URL: ${href}`);

        // Add analytics tracking here if needed
        // Example: this.trackSocialEngagement(platform, href);

        // For email links, we might want to handle differently
        if (platform === 'email') {
            this.handleEmailLinkClick(href, event);
        }
    }

    /**
     * @brief Sets up specialized handler for email links
     * @private
     */
    setupEmailLinkHandler() {
        const emailLinkSelector = `.${FOOTER_CONFIGURATION.TEMPLATE_CLASSES.socialLink}--email`;
        
        this.addEventListener('click', emailLinkSelector, (event, context) => {
            // Email links are handled by browser by default
            // We can add additional tracking or validation here
            console.debug('FooterView: Email link clicked');
            
            this.notifyObservers('footer:emailLinkClicked', {
                timestamp: Date.now(),
                eventType: 'click'
            });
        });
    }

    /**
     * @brief Handles email link click with additional safety checks
     * @private
     * @param {string} href - Email href (mailto: address)
     * @param {Event} event - Original click event
     */
    handleEmailLinkClick(href, event) {
        // Validate email format before allowing the click
        const emailAddress = href.replace('mailto:', '');
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!emailRegex.test(emailAddress)) {
            console.warn('FooterView: Invalid email address in mailto link:', emailAddress);
            event.preventDefault();
            
            this.notifyObservers('footer:invalidEmailLink', {
                emailAddress,
                timestamp: Date.now()
            });
        }
    }

    /**
     * @brief Sets up safety handlers for external links
     * @private
     */
    setupExternalLinkHandlers() {
        const externalLinkSelector = 'a[target="_blank"]';
        
        this.addEventListener('click', externalLinkSelector, (event, context) => {
            const link = event.currentTarget;
            
            // Verify that rel="noopener noreferrer" is set for security
            if (!link.getAttribute('rel')?.includes('noopener')) {
                console.warn('FooterView: External link missing rel="noopener noreferrer":', link.href);
                link.setAttribute('rel', 'noopener noreferrer');
            }

            this.notifyObservers('footer:externalLinkClicked', {
                href: link.href,
                timestamp: Date.now(),
                hasSecurityAttributes: !!link.getAttribute('rel')
            });
        });
    }

    /**
     * @brief Updates accessibility attributes for footer elements
     * @private
     */
    updateFooterAccessibility() {
        // Ensure container has proper role and label
        const footerContainer = this.containerElement.querySelector(`.${FOOTER_CONFIGURATION.TEMPLATE_CLASSES.container}`);
        if (footerContainer) {
            footerContainer.setAttribute('role', 'contentinfo');
            footerContainer.setAttribute('aria-label', FOOTER_CONFIGURATION.ACCESSIBILITY.footerLabel);
        }

        // Add accessible labels to social links container
        const socialLinksContainer = this.containerElement.querySelector(`.${FOOTER_CONFIGURATION.TEMPLATE_CLASSES.socialLinks}`);
        if (socialLinksContainer) {
            socialLinksContainer.setAttribute('aria-label', FOOTER_CONFIGURATION.ACCESSIBILITY.socialLinksLabel);
        }
    }

    /**
     * @brief Updates footer configuration options
     * @public
     * @param {Object} newConfiguration - New footer configuration options
     * @returns {Promise<void>} Resolves when configuration is updated and view is re-rendered if needed
     */
    async updateFooterConfiguration(newConfiguration) {
        const previousConfiguration = { ...this.footerConfiguration };
        
        this.footerConfiguration = {
            ...this.footerConfiguration,
            ...newConfiguration
        };

        // Regenerate template if configuration changed significantly
        if (this.shouldRegenerateTemplate(previousConfiguration, this.footerConfiguration)) {
            this.cachedTemplate = this.generateFooterTemplate();
            this.updateTemplate(this.cachedTemplate, false);
            
            console.debug('FooterView: Footer template regenerated due to configuration changes.');
        }

        this.notifyObservers('footer:configurationUpdated', {
            previousConfiguration,
            newConfiguration: this.footerConfiguration,
            timestamp: Date.now()
        });

        console.debug('FooterView: Footer configuration updated.');
    }

    /**
     * @brief Determines if template should be regenerated based on configuration changes
     * @private
     * @param {Object} oldConfig - Previous configuration
     * @param {Object} newConfig - New configuration
     * @returns {boolean} True if template should be regenerated
     */
    shouldRegenerateTemplate(oldConfig, newConfig) {
        return oldConfig.enableSocialLinks !== newConfig.enableSocialLinks ||
               oldConfig.showCurrentYear !== newConfig.showCurrentYear;
    }

    /**
     * @brief Gets current footer configuration
     * @public
     * @returns {Object} Current footer configuration object
     */
    getFooterConfiguration() {
        return { ...this.footerConfiguration };
    }

    /**
     * @brief Updates social media links with new URLs
     * @public
     * @param {Object} newSocialUrls - Object containing new social media URLs
     * @param {string} newSocialUrls.github - New GitHub URL
     * @param {string} newSocialUrls.linkedin - New LinkedIn URL
     * @param {string} newSocialUrls.instagram - New Instagram username
     * @param {string} newSocialUrls.email - New email address
     * @returns {Promise<void>} Resolves when social links are updated
     */
    async updateSocialLinks(newSocialUrls) {
        // This method would be used to update social links without full re-render
        // Implementation would depend on specific requirements
        console.debug('FooterView: Social links update requested:', newSocialUrls);
        
        this.notifyObservers('footer:socialLinksUpdated', {
            newSocialUrls,
            timestamp: Date.now()
        });
    }

    /**
     * @brief Handles view destruction with footer-specific cleanup
     * @public
     * @override
     */
    destroy() {
        // Perform footer-specific cleanup
        this.cleanupFooterResources();
        
        // Call parent destroy method
        super.destroy();
        
        console.info('FooterView: Footer view destroyed successfully.');
    }

    /**
     * @brief Cleans up footer-specific resources
     * @private
     */
    cleanupFooterResources() {
        // Clear any footer-specific caches or timeouts
        this.cachedTemplate = '';
        
        // Notify observers of destruction
        this.notifyObservers('footer:destroyed', {
            timestamp: Date.now(),
            finalConfiguration: this.footerConfiguration
        });
    }
}

export default FooterView;