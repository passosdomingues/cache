/**
 * @file View da navegação
 * @brief Renderiza o menu de navegação
 */

import BaseView from './BaseView.js';

class NavigationView extends BaseView {
    constructor() {
        const template = `
            <nav class="nav">
                <div class="nav-brand">
                    <h1>{{name}}</h1>
                </div>
                <ul class="nav-links">
                    {{#each sections}}
                    <li><a href="#{{id}}" data-section="{{id}}">{{title}}</a></li>
                    {{/each}}
                </ul>
                <div class="nav-toggle">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </nav>
        `;
        super('header', template);
    }

    /**
     * @brief Renderiza a navegação
     * @param {Object} data - Dados para renderização
     */
    render(data) {
        // Implementação simples de template engine para arrays
        const compiledTemplate = this.template.replace(/\{\{#each sections\}\}(.*?)\{\{\/each\}\}/s, (match, content) => {
            return data.sections.map(section => {
                return content.replace(/\{\{id\}\}/g, section.id)
                             .replace(/\{\{title\}\}/g, section.title);
            }).join('');
        }).replace(/\{\{name\}\}/g, data.name);

        this.container.innerHTML = compiledTemplate;
        this.setupEventListeners();
    }

    /**
     * @brief Configura os event listeners
     */
    setupEventListeners() {
        // Navegação suave
        this.addEvent('click', '.nav-links a', (e) => {
            e.preventDefault();
            const sectionId = e.target.getAttribute('data-section');
            this.notifyObservers('navigateToSection', { sectionId });
        });

        // Menu mobile
        this.addEvent('click', '.nav-toggle', () => {
            this.toggleMobileMenu();
        });
    }

    /**
     * @brief Alterna menu mobile
     */
    toggleMobileMenu() {
        const navLinks = this.container.querySelector('.nav-links');
        const navToggle = this.container.querySelector('.nav-toggle');
        
        navLinks.classList.toggle('active');
        navToggle.classList.toggle('active');
    }

    /**
     * @brief Atualiza navegação ativa
     * @param {string} activeSection - ID da seção ativa
     */
    setActiveSection(activeSection) {
        const links = this.container.querySelectorAll('.nav-links a');
        links.forEach(link => {
            link.classList.toggle('active', link.getAttribute('data-section') === activeSection);
        });
    }
}

export default NavigationView;