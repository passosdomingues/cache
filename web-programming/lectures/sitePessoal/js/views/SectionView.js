/**
 * @file View das seções de conteúdo
 * @brief Renderiza seções dinâmicas do site
 */

import BaseView from './BaseView.js';

class SectionView extends BaseView {
    constructor() {
        super('main-content', '');
    }

    /**
     * @brief Renderiza todas as seções
     * @param {Array} sections - Array de seções
     */
    renderSections(sections) {
        const sectionsHTML = sections.map(section => this.createSectionHTML(section)).join('');
        this.container.innerHTML = sectionsHTML;
        this.setupSectionInteractions();
    }

    /**
     * @brief Cria HTML para uma seção
     * @param {Object} section - Dados da seção
     * @return {string} HTML da seção
     */
    createSectionHTML(section) {
        return `
            <section id="${section.id}" class="section">
                <div class="container">
                    <h2 class="section-title">${section.title}</h2>
                    <p class="section-subtitle">${section.subtitle}</p>
                    ${this.renderSectionContent(section)}
                </div>
            </section>
        `;
    }

    /**
     * @brief Renderiza conteúdo específico da seção
     * @param {Object} section - Dados da seção
     * @return {string} HTML do conteúdo
     */
    renderSectionContent(section) {
        switch (section.type) {
            case 'cards':
                return this.renderCards(section.content);
            case 'timeline':
                return this.renderTimeline(section.content);
            case 'gallery':
                return this.renderGallery(section.content);
            case 'skills':
                return this.renderSkills(section.content);
            default:
                return section.content;
        }
    }

    /**
     * @brief Renderiza cards
     * @param {Array} items - Array de itens
     * @return {string} HTML dos cards
     */
    renderCards(items) {
        return `
            <div class="card-grid">
                ${items.map(item => `
                    <div class="card">
                        ${item.image ? `<img src="${item.image}" alt="${item.title}" class="card-image">` : ''}
                        <div class="card-content">
                            <h3 class="card-title">${item.title}</h3>
                            <p class="card-description">${item.description}</p>
                            ${item.link ? `<a href="${item.link}" target="_blank" class="btn">Ver Mais</a>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    /**
     * @brief Configura interações das seções
     */
    setupSectionInteractions() {
        // Observador de interseção para animações
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    this.notifyObservers('sectionVisible', { sectionId: entry.target.id });
                }
            });
        }, { threshold: 0.1 });

        // Observar todas as seções
        document.querySelectorAll('.section').forEach(section => {
            observer.observe(section);
        });
    }
}

export default SectionView;