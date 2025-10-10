/**
 * @file Controlador de seções
 * @brief Gerencia lógica de conteúdo das seções
 */

class SectionController {
    constructor(models, views) {
        this.models = models;
        this.views = views;
        this.init();
    }

    /**
     * @brief Inicializa o controlador
     */
    init() {
        this.setupSectionEvents();
        this.loadDynamicContent();
    }

    /**
     * @brief Configura eventos das seções
     */
    setupSectionEvents() {
        // Ouvir mudanças de seção ativa
        document.addEventListener('sectionChange', (e) => {
            this.onSectionChange(e.detail.sectionId);
        });

        // Ouvir visibilidade de seções
        this.views.section.addObserver((event, data) => {
            if (event === 'sectionVisible') {
                this.onSectionVisible(data.sectionId);
            }
        });
    }

    /**
     * @brief Handler de mudança de seção
     * @param {string} sectionId - ID da seção ativa
     */
    onSectionChange(sectionId) {
        // Atualizar navegação ativa
        if (this.views.navigation.setActiveSection) {
            this.views.navigation.setActiveSection(sectionId);
        }

        // Carregar conteúdo lazy se necessário
        this.loadLazyContent(sectionId);
    }

    /**
     * @brief Handler de seção visível
     * @param {string} sectionId - ID da seção visível
     */
    onSectionVisible(sectionId) {
        console.log(`Seção ${sectionId} está visível`);
        // Implementar animações ou carregamentos adicionais
    }

    /**
     * @brief Carrega conteúdo dinâmico
     */
    loadDynamicContent() {
        // Implementar carregamento de conteúdo via API se necessário
        console.log('Carregando conteúdo dinâmico...');
    }

    /**
     * @brief Carrega conteúdo lazy para seção específica
     * @param {string} sectionId - ID da seção
     */
    loadLazyContent(sectionId) {
        // Implementar lazy loading para imagens ou conteúdo pesado
        const section = document.getElementById(sectionId);
        if (section) {
            const images = section.querySelectorAll('img[data-src]');
            images.forEach(img => {
                img.src = img.getAttribute('data-src');
                img.removeAttribute('data-src');
            });
        }
    }

    /**
     * @brief Filtra conteúdo por categoria
     * @param {string} category - Categoria para filtrar
     * @return {Array} Conteúdo filtrado
     */
    filterContentByCategory(category) {
        const allContent = this.models.content.getProjects().concat(this.models.content.getExperiences());
        return allContent.filter(item => item.category === category);
    }

    /**
     * @brief Busca conteúdo por termo
     * @param {string} searchTerm - Termo de busca
     * @return {Array} Resultados da busca
     */
    searchContent(searchTerm) {
        const allContent = this.models.content.getProjects().concat(this.models.content.getExperiences());
        return allContent.filter(item => 
            item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.description.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }
}

export default SectionController;