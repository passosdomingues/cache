/**
 * @file Controlador principal da aplicação
 * @brief Coordena todos os modelos e views (Singleton)
 */

import NavigationView from '../views/NavigationView.js';
import HeroView from '../views/HeroView.js';
import SectionView from '../views/SectionView.js';
import FooterView from '../views/FooterView.js';
import NavigationController from './NavigationController.js';
import SectionController from './SectionController.js';

class MainController {
    constructor(models) {
        if (MainController.instance) {
            return MainController.instance;
        }

        this.models = models;
        this.views = {};
        this.controllers = {};
        
        this.init();
        MainController.instance = this;
    }

    /**
     * @brief Inicializa a aplicação
     */
    init() {
        this.initViews();
        this.initControllers();
        this.render();
        this.setupEventHandlers();
    }

    /**
     * @brief Inicializa todas as views
     */
    initViews() {
        this.views.navigation = new NavigationView();
        this.views.hero = new HeroView();
        this.views.section = new SectionView();
        this.views.footer = new FooterView();
    }

    /**
     * @brief Inicializa todos os controladores
     */
    initControllers() {
        this.controllers.navigation = new NavigationController();
        this.controllers.section = new SectionController(this.models, this.views);
    }

    /**
     * @brief Renderiza toda a aplicação
     */
    render() {
        const userData = this.models.user.getUserData();
        const sections = this.models.content.getSections();

        // Renderizar views com dados
        this.views.navigation.render({
            name: userData.name,
            sections: sections
        });

        this.views.hero.render(userData);
        this.views.section.renderSections(sections);
        this.views.footer.render(userData);
    }

    /**
     * @brief Configura handlers de eventos globais
     */
    setupEventHandlers() {
        // Observer para navegação
        this.views.navigation.addObserver((event, data) => {
            if (event === 'navigateToSection') {
                this.controllers.navigation.navigateToSection(data.sectionId);
            }
        });

        // Observer para scroll
        this.views.hero.addObserver((event, data) => {
            if (event === 'scrollToSection') {
                this.controllers.navigation.scrollToSection(data.sectionId);
            }
        });
    }
}

export default MainController;