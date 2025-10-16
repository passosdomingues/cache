import eventBus from '../core/EventBus.js';

/**
 * @brief View manager for rendering sections
 * @description Handles rendering of different section types with template methods
 */
class ViewManager {
    /**
     * @brief Create a new ViewManager instance
     * @param {Object} config - Configuration object
     * @param {HTMLElement} config.container - Container element for sections
     * @param {Object} config.eventBus - Event bus instance
     */
    constructor(config = {}) {
        this.container = config.container;
        this.eventBus = config.eventBus || eventBus;
        
        this.renderMethods = {
            timeline: this.renderTimeline.bind(this),
            cards: this.renderCards.bind(this),
            skills: this.renderSkills.bind(this),
            gallery: this.renderGallery.bind(this),
        };

        this.setupEventListeners();
    }

    /**
     * @brief Set up event listeners
     */
    setupEventListeners() {
        this.eventBus.subscribe('section:updated', this.onSectionUpdated.bind(this));
    }

    /**
     * @brief Handle section updates
     * @param {Object} data - Update data with sectionId and newContent
     */
    onSectionUpdated(data) {
        this.renderSection(data.sectionId, data.newContent);
    }

    /**
     * @brief Render a section
     * @param {Object} section - Section data object
     */
    renderSection(section) {
        if (!this.container) {
            console.error('ViewManager: Container not available');
            return;
        }

        try {
            const sectionElement = document.createElement('section');
            sectionElement.id = section.id;
            sectionElement.className = `section section--${section.type}`;

            const renderMethod = this.renderMethods[section.type];
            if (typeof renderMethod !== 'function') {
                console.warn(`ViewManager: No render method for type "${section.type}"`);
                return;
            }

            const sectionContent = renderMethod(section.content);
            
            sectionElement.innerHTML = `
                <div class="section-container">
                    <header class="section-header">
                        <h2 class="section-title">${this.escapeHtml(section.title)}</h2>
                        <p class="section-subtitle">${this.escapeHtml(section.subtitle)}</p>
                    </header>
                    ${sectionContent}
                </div>
            `;

            this.container.appendChild(sectionElement);
            
            this.eventBus.publish('view:section:rendered', { 
                sectionId: section.id,
                element: sectionElement 
            });

        } catch (error) {
            console.error(`ViewManager: Error rendering section ${section.id}`, error);
            this.eventBus.publish('view:render:error', { sectionId: section.id, error });
        }
    }

    /**
     * @brief Render timeline content
     * @param {Object} content - Timeline content data
     * @returns {string} HTML string
     */
    renderTimeline(content) {
        if (!content.timeline) return '';

        const timelineItems = content.timeline.map(item => `
            <div class="timeline-item">
                <div class="timeline-period">${this.escapeHtml(item.period)}</div>
                <div class="timeline-content">
                    <h3 class="timeline-title">${this.escapeHtml(item.title)}</h3>
                    <p class="timeline-description">${this.escapeHtml(item.description)}</p>
                    <div class="highlights-list">
                        ${item.highlights.map(h => 
                            `<span class="highlight-tag">${this.escapeHtml(h)}</span>`
                        ).join('')}
                    </div>
                </div>
            </div>
        `).join('');

        return `<div class="timeline">${timelineItems}</div>`;
    }

    /**
     * @brief Render cards content
     * @param {Array} content - Cards content array
     * @returns {string} HTML string
     */
    renderCards(content) {
        if (!Array.isArray(content)) return '';

        const cards = content.map(item => `
            <div class="card">
                <h3 class="card-title">${this.escapeHtml(item.title)}</h3>
                <p class="card-description">${this.escapeHtml(item.description)}</p>
                ${item.links && item.links.length > 0 ? `
                    <div class="card-links">
                        ${item.links.map(link => 
                            `<a href="${this.escapeHtml(link.url)}" target="_blank" rel="noopener noreferrer" class="card-link">
                                ${this.escapeHtml(link.label)}
                            </a>`
                        ).join('')}
                    </div>
                ` : ''}
                <div class="tags-container">
                    ${item.tags.map(tag => 
                        `<span class="tag">${this.escapeHtml(tag)}</span>`
                    ).join('')}
                </div>
                <div class="card-meta">
                    <span class="card-date">${this.escapeHtml(item.date)}</span>
                    <span class="card-status card-status--${item.status?.toLowerCase()}">
                        ${this.escapeHtml(item.status)}
                    </span>
                </div>
            </div>
        `).join('');

        return `<div class="cards-grid">${cards}</div>`;
    }

    /**
     * @brief Render skills content
     * @param {Array} content - Skills content array (array of categories from PortfolioData.js)
     * @returns {string} HTML string
     */
    renderSkills(content) {
        // Corrigido: O 'content' é o próprio array de categorias
        if (!Array.isArray(content)) return '';

        const categories = content.map(category => {
            const skills = category.skills.map(skill => {
                
                // Adicionado: Renderiza links se existirem
                const linksHtml = (skill.links && Array.isArray(skill.links) && skill.links.length > 0)
                    ? `<div class="skill-links">
                        ${skill.links.map(link => 
                            `<a href="${this.escapeHtml(link.url)}" target="_blank" rel="noopener noreferrer" class="skill-link">
                                ${this.escapeHtml(link.label)}
                            </a>`
                        ).join('')}
                    </div>`
                    : '';
                
                // Adicionado: Verifica se 'proficiency' existe para renderizar a barra
                const hasProficiency = typeof skill.proficiency === 'number';

                return `
                    <div class="skill-item">
                        <div class="skill-header">
                            <span class="skill-name">${this.escapeHtml(skill.name)}</span>
                            ${hasProficiency ?
                                `<span class="skill-proficiency">${skill.proficiency}%</span>` : ''
                            }
                        </div>
                        ${hasProficiency ?
                            `<div class="skill-bar">
                                <div class="skill-progress" 
                                     style="width: ${skill.proficiency}%;"
                                     data-proficiency="${skill.proficiency}">
                                </div>
                            </div>` : ''
                        }
                        <p class="skill-description">${this.escapeHtml(skill.description)}</p>
                        ${linksHtml}
                    </div>
                `;
            }).join('');

            return `
                <div class="skill-category">
                    <h3 class="category-title">${this.escapeHtml(category.category)}</h3>
                    <div class="skills-list">
                        ${skills}
                    </div>
                </div>
            `;
        }).join('');
        
        return `<div class="skills-categories">${categories}</div>`;
    }
    
    /**
     * @brief Render gallery content compatible with PortfolioData.js
     * @param {Array} content - Gallery content array
     * @returns {string} HTML string
     */
    renderGallery(content) {
        if (!Array.isArray(content)) return '';

        const items = content.map(item => {
            const src = item.imageUrl || (item.image && item.image.src) || (item.images && item.images[0]?.src) || '';
            const alt = item.alt || item.caption || item.title || 'Gallery image';
            const caption = item.caption || (item.image && item.image.caption) || '';

            // Se houver várias imagens em um mesmo item
            const multipleImages = item.images?.length > 1 ? item.images.map(img => `
                <div class="gallery-subitem">
                    <img src="${this.escapeHtml(img.src)}"
                        alt="${this.escapeHtml(img.alt || alt)}"
                        class="gallery-image"
                        loading="lazy">
                    ${img.caption ? `<div class="gallery-caption">${this.escapeHtml(img.caption)}</div>` : ''}
                </div>
            `).join('') : '';

            return `
                <div class="gallery-item">
                    ${src ? `
                        <img src="${this.escapeHtml(src)}"
                            alt="${this.escapeHtml(alt)}"
                            class="gallery-image"
                            loading="lazy">
                    ` : ''}
                    ${multipleImages}
                    ${caption ? `<div class="gallery-caption">${this.escapeHtml(caption)}</div>` : ''}
                </div>
            `;
        }).join('');

        return `<div class="gallery-grid">${items}</div>`;
    }

    /**
     * @brief Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        if (!text) return '';
        
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * @brief Clear all rendered content
     */
    clear() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }

    /**
     * @brief Destroy view manager and clean up resources
     */
    destroy() {
        this.eventBus.unsubscribe('section:updated', this.onSectionUpdated);
        this.clear();
        console.info('ViewManager: Destroyed');
    }
}

export { ViewManager };