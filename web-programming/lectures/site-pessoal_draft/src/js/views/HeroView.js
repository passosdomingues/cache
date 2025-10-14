import { BaseView } from './BaseView.js';

/**
 * @brief Hero section view
 * @description Renders the main hero section with personal information
 */
export class HeroView extends BaseView {
    constructor(config = {}) {
        super(config);
        this.heroData = config.heroData || {};
    }

    /**
     * @brief Initialize hero view
     */
    async init() {
        await super.init();
        
        // Load default hero data if not provided
        if (Object.keys(this.heroData).length === 0) {
            this.heroData = this.getDefaultHeroData();
        }
        
        console.info('HeroView: Initialized with hero data', this.heroData);
    }

    /**
     * @brief Render hero section
     */
    async render() {
        await super.render();
        
        if (!this.container) {
            throw new Error('HeroView: Container not available');
        }

        const heroHTML = this.createHeroHTML();
        this.container.innerHTML = heroHTML;
        
        // Register main elements
        this.registerElement('heroTitle', this.container.querySelector('.hero-title'));
        this.registerElement('heroSubtitle', this.container.querySelector('.hero-subtitle'));
        this.registerElement('heroDescription', this.container.querySelector('.hero-description'));
        
        this.setupEventListeners();
        
        this.eventBus.publish('hero:rendered', { data: this.heroData });
    }

    /**
     * @brief Create hero section HTML
     * @returns {string} HTML string
     */
    createHeroHTML() {
        return `
            <section class="hero-section" id="hero-section">
                <div class="hero-content">
                    <h1 class="hero-title">${this.escapeHtml(this.heroData.title)}</h1>
                    <p class="hero-subtitle">${this.escapeHtml(this.heroData.subtitle)}</p>
                    <p class="hero-description">${this.escapeHtml(this.heroData.description)}</p>
                    ${this.heroData.cta ? this.createCTAButtons() : ''}
                </div>
                ${this.heroData.image ? this.createHeroImage() : ''}
            </section>
        `;
    }

    /**
     * @brief Create call-to-action buttons
     * @returns {string} CTA buttons HTML
     */
    createCTAButtons() {
        if (!this.heroData.cta) return '';
        
        const buttons = this.heroData.cta.map(cta => `
            <a href="${this.escapeHtml(cta.url)}" 
               class="hero-cta-button hero-cta-button--${cta.type || 'primary'}"
               ${cta.external ? 'target="_blank" rel="noopener noreferrer"' : ''}>
                ${this.escapeHtml(cta.label)}
            </a>
        `).join('');
        
        return `<div class="hero-cta-container">${buttons}</div>`;
    }

    /**
     * @brief Create hero image
     * @returns {string} Hero image HTML
     */
    createHeroImage() {
        if (!this.heroData.image) return '';
        
        return `
            <div class="hero-image-container">
                <img src="${this.escapeHtml(this.heroData.image.url)}" 
                     alt="${this.escapeHtml(this.heroData.image.alt)}" 
                     class="hero-image"
                     loading="eager">
            </div>
        `;
    }

    /**
     * @brief Set up event listeners
     */
    setupEventListeners() {
        // Add click listeners to CTA buttons
        const ctaButtons = this.container.querySelectorAll('.hero-cta-button');
        ctaButtons.forEach((button, index) => {
            this.addEventListener(button, 'click', (event) => {
                this.onCTAClick(event, this.heroData.cta[index]);
            });
        });
    }

    /**
     * @brief Handle CTA button clicks
     * @param {Event} event - Click event
     * @param {Object} cta - CTA data
     */
    onCTAClick(event, cta) {
        this.eventBus.publish('hero:cta:clicked', {
            cta,
            event
        });
        
        console.info('HeroView: CTA clicked', cta);
    }

    /**
     * @brief Update hero data
     * @param {Object} newData - New hero data
     */
    async update(newData) {
        await super.update(newData);
        
        this.heroData = { ...this.heroData, ...newData };
        
        // Re-render if already rendered
        if (this.isRendered) {
            await this.render();
        }
    }

    /**
     * @brief Get default hero data
     * @returns {Object} Default hero data
     */
    getDefaultHeroData() {
        return {
            title: 'Rafael Passos Domingues',
            subtitle: 'Physicist & Computer Scientist',
            description: 'Researcher in Astrophysics, Data Science and Technology Innovation. Combining scientific rigor with computational expertise to solve complex problems and drive innovation.',
            cta: [
                {
                    label: 'View Research',
                    url: '#astrophysics-research',
                    type: 'primary'
                },
                {
                    label: 'Contact Me',
                    url: '#contact',
                    type: 'secondary'
                }
            ]
        };
    }

    /**
     * @brief Add animation to hero elements
     */
    animateHero() {
        const title = this.getElement('heroTitle');
        const subtitle = this.getElement('heroSubtitle');
        const description = this.getElement('heroDescription');
        
        if (title) this.addClass(title, 'hero-element--animated');
        if (subtitle) this.addClass(subtitle, 'hero-element--animated');
        if (description) this.addClass(description, 'hero-element--animated');
        
        this.eventBus.publish('hero:animated');
    }
}