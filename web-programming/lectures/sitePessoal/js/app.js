/**
 * @file Arquivo principal da aplicação
 * @brief Inicializa todos os módulos e coordena a aplicação MVC
 */

import UserModel from './models/UserModel.js';
import ContentModel from './models/ContentModel.js';
import MainController from './controllers/MainController.js';

class App {
    constructor() {
        this.models = {};
        this.controllers = {};
        this.views = {};
        
        this.init();
    }

    /**
     * @brief Inicializa a aplicação
     */
    init() {
        // Inicializar modelos
        this.models.user = new UserModel();
        this.models.content = new ContentModel();

        // Inicializar controlador principal
        this.controllers.main = new MainController(this.models);
        
        console.log('🚀 Aplicação inicializada com sucesso!');
    }
}

// Inicializar aplicação quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    new App();
});