/**
 * @file View da seção Hero
 * @brief Renderiza a seção principal do site
 */

import BaseView from './BaseView.js';

class HeroView extends BaseView {
    constructor() {
        const template = `
            <div class="container">
                <div class="hero-content">
                    <div class="hero-text">
                        <h1>{{name}}</h1>
                        <p class="hero-subtitle">{{title}}</p>
                        <p class="hero-description">{{summary}}</p>
                        <div class="hero-buttons">
                            <a href="#projects" class="btn btn-primary">Ver Projetos</a>
                            <a href="#contact" class="btn btn-secondary">Entrar em Contato</a>
                        </div>
                    </div>
                    <div class="hero-image">
                        <img src="{{profileImage}}" alt="{{name}}" class="profile-image">
                    </div>
                </div>
            </div>
        `;
        super('hero', template);
    }

    /**
     * @brief Renderiza a seção hero com dados do usuário
     * @param {Object} userData - Dados do usuário
     */
    render(userData) {
        super.render(userData);
        this.addScrollAnimation();
    }

    /**
     * @brief Adiciona animação de scroll suave
     */
    addScrollAnimation() {
        this.addEvent('click', '.hero-buttons a', (e) => {
            e.preventDefault();
            const targetId = e.target.getAttribute('href').substring(1);
            this.notifyObservers('scrollToSection', { sectionId: targetId });
        });
    }
}

export default HeroView;