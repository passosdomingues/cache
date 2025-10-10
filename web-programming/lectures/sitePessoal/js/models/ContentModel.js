/**
 * @file Modelo de conteúdo do site
 * @brief Gerencia todo o conteúdo das seções e projetos
 */

class ContentModel {
    constructor() {
        this.sections = this.initializeSections();
        this.projects = this.initializeProjects();
        this.experiences = this.initializeExperiences();
    }

    /**
     * @brief Inicializa as seções do site
     * @return {Array} Array de objetos de seção
     */
    initializeSections() {
        return [
            {
                id: "about",
                title: "Sobre Mim",
                subtitle: "Minha jornada acadêmica e profissional",
                content: this.getAboutContent(),
                type: "timeline"
            },
            {
                id: "astrophysics",
                title: "Astrofísica e Pesquisa",
                subtitle: "Trabalhos em astrofísica galáctica e extragaláctica",
                content: this.getAstrophysicsContent(),
                type: "cards"
            },
            {
                id: "observatory",
                title: "Observatório Astronômico",
                subtitle: "Divulgação científica e pesquisa na UNIFAL-MG",
                content: this.getObservatoryContent(),
                type: "gallery"
            },
            {
                id: "craam",
                title: "Visita ao CRAAM",
                subtitle: "Centro de Radioastronomia e Astrofísica Mackenzie",
                content: this.getCraamContent(),
                type: "gallery"
            },
            {
                id: "education",
                title: "Experiência em Educação",
                subtitle: "Docência e desenvolvimento de materiais didáticos",
                content: this.getEducationContent(),
                type: "timeline"
            },
            {
                id: "innovation",
                title: "Inovação e Empreendedorismo",
                subtitle: "NidusTec e ecossistema de inovação",
                content: this.getInnovationContent(),
                type: "cards"
            },
            {
                id: "projects",
                title: "Projetos e Desenvolvimento",
                subtitle: "Trabalhos técnicos e científicos",
                content: this.getProjectsContent(),
                type: "cards"
            },
            {
                id: "skills",
                title: "Habilidades e Competências",
                subtitle: "Áreas de conhecimento e tecnologias",
                content: this.getSkillsContent(),
                type: "skills"
            }
        ];
    }

    getAboutContent() {
        return `
            <div class="about-content">
                <p>Como Físico pela UNIFAL-MG (2014-2018), fui um estudioso das Áreas de Astrofísica Galáctica e Extragaláctica, integrando a equipe do Observatório Astronômico da UNIFAL-MG (2016-2018), pude atuar com divulgação da ciência. Durante o Mestrado em Física pela UNIFEI (2021-2023), tinha uma pesquisa em Núcleos Ativos de Galáxias: Foi quando adquiri uma paixão especial por dados.</p>
                
                <p>Lecionei pela SEE-MG (2019-2022) levando conhecimento científico no âmbito teórico, experimental e prático, aplicando conhecimentos técnicos aos desafios que o período (2020-2022) trouxeram, à três municípios de Minas Gerais.</p>
                
                <p>Em 2023 tomei a decisão de transição de carreira, me tornando discente do Bacharelado em Ciência da Computação na UNIFAL-MG (2023-2029) e jardineiro nas horas vagas, integrando a equipe da Incubadora de Empresas de Base Tecnológica - NidusTec/UNIFAL-MG (2024-2025), conectando academia e mercado.</p>
            </div>
        `;
    }

    getAstrophysicsContent() {
        return [
            {
                title: "Pesquisa em Matéria Escura",
                description: "Estudo das curvas de rotação galáctica e evidências de matéria escura",
                image: "assets/images/bullet-cluster-black-matter_upscayl.png",
                link: "https://lnkd.in/deYnab4a"
            },
            {
                title: "Seminário em Astronomia",
                description: "Primeiro Ciclo de Seminários em Astronomia da UNIFAL-MG",
                image: "assets/images/seminario.jpg",
                details: "Apresentação sobre órbitas estelares e matéria escura"
            }
        ];
    }

    // ... (outros métodos getContent similares para cada seção)

    /**
     * @brief Retorna todas as seções
     * @return {Array} Array de seções
     */
    getSections() {
        return this.sections;
    }

    /**
     * @brief Busca seção por ID
     * @param {string} sectionId - ID da seção
     * @return {Object} Dados da seção
     */
    getSectionById(sectionId) {
        return this.sections.find(section => section.id === sectionId);
    }

    /**
     * @brief Retorna todos os projetos
     * @return {Array} Array de projetos
     */
    getProjects() {
        return this.projects;
    }

    /**
     * @brief Retorna todas as experiências
     * @return {Array} Array de experiências
     */
    getExperiences() {
        return this.experiences;
    }
}

export default ContentModel;