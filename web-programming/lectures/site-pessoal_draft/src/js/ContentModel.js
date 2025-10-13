/**
 * @file ContentModel.js
 * @author Rafael Passos Domingues
 * @version 3.0.0
 * @brief Model responsible for managing all dynamic content of the website.
 * @description Centralized content management system handling sections, projects,
 * experiences, and data consumed by views with caching, validation, and extensible architecture.
 */

/**
 * @constant {Object} CONTENT_TYPES
 * @brief Defines available content display types and their configurations
 * @description Maps content type identifiers to their display characteristics and validation rules
 */
const CONTENT_TYPES = {
    TIMELINE: {
        identifier: 'timeline',
        displayName: 'Timeline',
        supportsPagination: false,
        maxItems: null,
        layout: 'vertical'
    },
    CARDS: {
        identifier: 'cards',
        displayName: 'Card Grid',
        supportsPagination: true,
        maxItems: 12,
        layout: 'grid'
    },
    GALLERY: {
        identifier: 'gallery',
        displayName: 'Image Gallery',
        supportsPagination: true,
        maxItems: 24,
        layout: 'masonry'
    },
    SKILLS: {
        identifier: 'skills',
        displayName: 'Skills Matrix',
        supportsPagination: false,
        maxItems: null,
        layout: 'matrix'
    }
};

/**
 * @constant {Object} VALIDATION_RULES
 * @brief Validation rules for content structure and data integrity
 * @description Defines required fields, data types, and constraints for different content types
 */
const VALIDATION_RULES = {
    SECTION: {
        requiredFields: ['id', 'title', 'type'],
        idPattern: /^[a-z-]+$/,
        maxTitleLength: 100,
        maxSubtitleLength: 200
    },
    PROJECT: {
        requiredFields: ['id', 'title', 'description'],
        maxTitleLength: 80,
        maxDescriptionLength: 300
    },
    EXPERIENCE: {
        requiredFields: ['id', 'title', 'period', 'description'],
        maxTitleLength: 80,
        maxDescriptionLength: 500
    }
};

/**
 * @class ContentModel
 * @brief Centralized content management system for the application
 * @description Handles all dynamic content including sections, projects, experiences,
 * with caching, validation, and extensible architecture for scalable content management
 */
class ContentModel {
    /**
     * @brief Creates an instance of ContentModel
     * @constructor
     * @param {Object} options - Configuration options for content model
     * @param {boolean} options.enableCaching - Whether to enable content caching
     * @param {number} options.cacheTimeout - Cache timeout in milliseconds
     * @param {boolean} options.enableValidation - Whether to validate content structure
     */
    constructor(options = {}) {
        const {
            enableCaching = true,
            cacheTimeout = 300000, // 5 minutes
            enableValidation = true
        } = options;

        /**
         * @private
         * @type {Array}
         * @brief Collection of website sections with their content and configuration
         */
        this.sections = [];

        /**
         * @private
         * @type {Array}
         * @brief Collection of project items with metadata and content
         */
        this.projects = [];

        /**
         * @private
         * @type {Array}
         * @brief Collection of experience items with timeline and details
         */
        this.experiences = [];

        /**
         * @private
         * @type {Object}
         * @brief Cache storage for optimized content retrieval
         */
        this.contentCache = new Map();

        /**
         * @private
         * @type {Object}
         * @brief Configuration options for content management
         */
        this.configuration = {
            enableCaching,
            cacheTimeout,
            enableValidation,
            maxCacheSize: 100
        };

        /**
         * @private
         * @type {boolean}
         * @brief Tracks whether content has been initialized
         */
        this.isInitialized = false;

        this.initializeContentModel();
    }

    /**
     * @brief Initializes the content model with all required data
     * @private
     * @returns {Promise<void>} Resolves when content model is fully initialized
     */
    async initializeContentModel() {
        try {
            await this.loadAllContent();
            this.isInitialized = true;
            console.info('ContentModel: Content model successfully initialized.');
        } catch (error) {
            console.error('ContentModel: Failed to initialize content model:', error);
            throw error;
        }
    }

    /**
     * @brief Loads all content types in parallel for optimal performance
     * @private
     * @returns {Promise<void>} Resolves when all content is loaded
     */
    async loadAllContent() {
        const contentLoadingPromises = [
            this.loadSectionsContent(),
            this.loadProjectsContent(),
            this.loadExperiencesContent()
        ];

        await Promise.all(contentLoadingPromises);
    }

    /**
     * @brief Loads and initializes section content with validation
     * @private
     * @returns {Promise<void>} Resolves when sections are loaded and validated
     */
    async loadSectionsContent() {
        try {
            const rawSections = this.initializeSections();
            
            if (this.configuration.enableValidation) {
                this.validateSectionsContent(rawSections);
            }

            this.sections = rawSections;
            this.cacheContent('sections', this.sections);
            
            console.debug(`ContentModel: Loaded ${this.sections.length} sections.`);
        } catch (error) {
            console.error('ContentModel: Failed to load sections content:', error);
            throw error;
        }
    }

    /**
     * @brief Initializes the website sections with content and configuration
     * @private
     * @returns {Array} Array of section objects with complete content
     */
    initializeSections() {
        return [
            {
                id: 'about',
                title: 'About Me',
                subtitle: 'My academic and professional journey',
                content: this.getAboutContent(),
                type: CONTENT_TYPES.TIMELINE.identifier,
                metadata: {
                    priority: 1,
                    visible: true,
                    order: 1,
                    icon: 'atom', // Replace with a suitable icon from Noun Project for 'user' or 'profile'
                    backgroundColor: 'var(--color-surface)'
                }
            },
            {
                id: 'astrophysics-research',
                title: 'Astrophysics Research',
                subtitle: 'Work in galactic and extragalactic astrophysics',
                content: this.getAstrophysicsContent(),
                type: CONTENT_TYPES.CARDS.identifier,
                metadata: {
                    priority: 2,
                    visible: true,
                    order: 2,
                    icon: 'galaxy', // Icon for Astrophysics Research
                    backgroundColor: 'var(--color-gray-50)'
                }
            },
            {
                id: 'astronomical-observatory',
                title: 'Astronomical Observatory',
                subtitle: 'Scientific outreach and research at UNIFAL-MG',
                content: this.getObservatoryContent(),
                type: CONTENT_TYPES.GALLERY.identifier,
                metadata: {
                    priority: 2,
                    visible: true,
                    order: 3,
                    icon: 'telescope-outline', // Icon for Astronomical Observatory
                    backgroundColor: 'var(--color-surface)'
                }
            },
            {
                id: 'craam-visit',
                title: 'CRAAM Visit',
                subtitle: 'Mackenzie Center for Radioastronomy and Astrophysics',
                content: this.getCraamContent(),
                type: CONTENT_TYPES.GALLERY.identifier,
                metadata: {
                    priority: 3,
                    visible: true,
                    order: 4,
                    icon: 'satellite-dish', // Icon for CRAAM Visit
                    backgroundColor: 'var(--color-gray-50)'
                }
            },
            {
                id: 'lna-zeiss-telescope',
                title: 'LNA Zeiss Telescope Experience',
                subtitle: 'Operating a classic instrument at Pico dos Dias Observatory',
                content: this.getLNATelescopeContent(),
                type: CONTENT_TYPES.GALLERY.identifier,
                metadata: {
                    priority: 3,
                    visible: true,
                    order: 5,
                    icon: 'telescope-solid', // Icon for LNA Zeiss Telescope Experience
                    backgroundColor: 'var(--color-surface)'
                }
            },
            {
                id: 'education-experience',
                title: 'Education Experience',
                subtitle: 'Teaching and educational material development',
                content: this.getEducationContent(),
                type: CONTENT_TYPES.TIMELINE.identifier,
                metadata: {
                    priority: 2,
                    visible: true,
                    order: 6,
                    icon: 'graduation-hat', // Icon for Education Experience
                    backgroundColor: 'var(--color-gray-50)'
                }
            },
            {
                id: 'innovation-entrepreneurship',
                title: 'Innovation and Entrepreneurship',
                subtitle: 'NidusTec and innovation ecosystem',
                content: this.getInnovationContent(),
                type: CONTENT_TYPES.CARDS.identifier,
                metadata: {
                    priority: 2,
                    visible: true,
                    order: 7,
                    icon: 'idea', // Icon for Innovation and Entrepreneurship
                    backgroundColor: 'var(--color-surface)'
                }
            },
            {
                id: 'deep-learning-projects',
                title: 'Deep Learning Projects',
                subtitle: 'Applying ML/DL to medical imaging and astrophysics',
                content: this.getDeepLearningProjectsContent(),
                type: CONTENT_TYPES.CARDS.identifier,
                metadata: {
                    priority: 1,
                    visible: true,
                    order: 8,
                    icon: 'brain-outline', // Icon for Deep Learning Projects
                    backgroundColor: 'var(--color-gray-50)'
                }
            },
            {
                id: 'skills',
                title: 'Skills and Competencies',
                subtitle: 'Knowledge areas and technologies',
                content: this.getSkillsContent(),
                type: CONTENT_TYPES.SKILLS.identifier,
                metadata: {
                    priority: 2,
                    visible: true,
                    order: 9,
                    icon: 'gears', // Icon for Skills and Competencies
                    backgroundColor: 'var(--color-surface)'
                }
            },
            {
                id: 'hobbies',
                title: 'Hobbies and Interests',
                subtitle: 'Activities that inspire and recharge me',
                content: this.getHobbiesContent(),
                type: CONTENT_TYPES.CARDS.identifier,
                metadata: {
                    priority: 4,
                    visible: true,
                    order: 10,
                    icon: 'puzzle-piece', // Icon for Hobbies and Interests
                    backgroundColor: 'var(--color-gray-50)'
                }
            }
        ];
    }

    /**
     * @brief Validates sections content against defined rules
     * @private
     * @param {Array} sections - Array of section objects to validate
     * @throws {Error} When section validation fails
     */
    validateSectionsContent(sections) {
        if (!Array.isArray(sections)) {
            throw new Error('Sections content must be an array');
        }

        sections.forEach((section, index) => {
            // Check required fields
            VALIDATION_RULES.SECTION.requiredFields.forEach(field => {
                if (!section[field]) {
                    throw new Error(`Section at index ${index} missing required field: ${field}`);
                }
            });

            // Validate ID pattern
            if (!VALIDATION_RULES.SECTION.idPattern.test(section.id)) {
                throw new Error(`Section ID '${section.id}' must contain only lowercase letters and hyphens`);
            }

            // Validate title length
            if (section.title.length > VALIDATION_RULES.SECTION.maxTitleLength) {
                throw new Error(`Section title '${section.title}' exceeds maximum length of ${VALIDATION_RULES.SECTION.maxTitleLength} characters`);
            }

            // Validate content type
            const validTypes = Object.values(CONTENT_TYPES).map(type => type.identifier);
            if (!validTypes.includes(section.type)) {
                throw new Error(`Invalid content type '${section.type}' for section '${section.id}'. Valid types: ${validTypes.join(', ')}`);
            }
        });
    }

    /**
     * @brief Generates comprehensive about section content
     * @private
     * @returns {Object} Structured about content with multiple data points
     */
    getAboutContent() {
        return {
            introduction: 'Físico e Cientista da Computação apaixonado por pesquisa em astrofísica, análise de dados e inovação tecnológica. Minha jornada é uma mistura de pesquisa acadêmica e aplicação prática, sempre impulsionada pela curiosidade sobre como o universo funciona e como podemos usar a tecnologia para resolver problemas do mundo real.',
            timeline: [
                {
                    period: '2014-2018',
                    title: 'Bacharelado em Física, UNIFAL-MG',
                    description: 'Minha jornada acadêmica começou com o Bacharelado em Física na UNIFAL-MG. Durante este período, mergulhei no fascinante mundo da Astrofísica Galáctica e Extragaláctica, participando de pesquisas e contribuindo para a divulgação científica no Observatório Astronômico da UNIFAL-MG. Esta experiência acendeu minha paixão por compreender o cosmos e comunicar conceitos científicos complexos.',
                    highlights: ['Astrofísica Galáctica e Extragaláctica', 'Divulgação Científica', 'Observação Astronômica']
                },
                {
                    period: '2019-2022',
                    title: 'Professor de Física, Secretaria de Estado de Educação de Minas Gerais',
                    description: 'Após a graduação, dediquei-me à educação, lecionando Física em três municípios de Minas Gerais. Este papel me desafiou a adaptar o conhecimento científico a diversas audiências, especialmente durante o período sem precedentes de 2020-2022, onde apliquei expertise técnica para superar obstáculos educacionais.',
                    highlights: ['Educação Científica', 'Física Experimental', 'Inovação Pedagógica']
                },
                {
                    period: '2021-2023',
                    title: 'Mestrado em Física, UNIFEI',
                    description: 'Meu Mestrado em Física na UNIFEI focou em Núcleos Ativos de Galáxias, um campo onde desenvolvi uma profunda apreciação pela análise de dados. Esta experiência de pesquisa solidificou meu interesse em extrair insights de conjuntos de dados complexos, lançando as bases para meus futuros empreendimentos em ciência de dados.',
                    highlights: ['Pesquisa em AGN', 'Análise Avançada de Dados', 'Computação Científica']
                },
                {
                    period: '2023-Presente',
                    title: 'Bacharelado em Ciência da Computação, UNIFAL-MG',
                    description: 'Em 2023, embarquei em um novo caminho acadêmico, cursando Bacharelado em Ciência da Computação na UNIFAL-MG. Esta transição reflete meu compromisso em preencher a lacuna entre a física teórica e as soluções tecnológicas práticas. Concomitantemente, juntei-me à Incubadora de Empresas de Base Tecnológica NidusTec/UNIFAL-MG, conectando a academia com o mercado e fomentando a inovação.',
                    highlights: ['Desenvolvimento de Software', 'Ciência de Dados', 'Aprendizado de Máquina', 'Conexão Academia-Indústria']
                },
                {
                    period: '2024-2025',
                    title: 'Ecossistema de Inovação e Educador Maker, Incubadora NidusTec/UNIFAL-MG',
                    description: 'Na NidusTec, abracei o papel de educador Maker, liderando projetos de robótica, modelagem 3D e oficinas de CNC. Esta experiência me permitiu aplicar técnicas de computação gráfica e processamento de imagens em protótipos multidisciplinares, abordando necessidades de infraestrutura institucional e explorando pesquisas em Inovação, Empreendedorismo, Engenharia de Produção e Indústria 4.0. Desenvolvi MVPs com potencial de mercado, demonstrando minha capacidade de transformar ideias em soluções tangíveis.',
                    highlights: ['Empreendedorismo', 'Transferência de Tecnologia', 'Educação Maker', 'Modelagem 3D e CNC', 'Robótica', 'Gestão da Inovação']
                }
            ],
            currentFocus: 'Currently, I am a Computer Science student, specializing in image processing and computer graphics. My focus is on applying my knowledge in multidisciplinary interfaces that combine Machine Learning, Deep Learning, Natural Language Processing (NLP), Convolutional Neural Networks (CNNs), and Large Language Models (LLMs), with a keen interest in exploring their integration with Smart Contracts and blockchain technologies.',
            reflection: 'My journey, seemingly disparate at first glance, is a testament to the power of interdisciplinary thinking. The convergence of physics, astrophysics, education, and computer science has equipped me with a unique perspective. I see myself not just as a Physicist or a Developer, but as a problem-solver who leverages diverse knowledge to create impactful solutions. This trajectory has shaped me into an applicator of knowledge, constantly seeking to unite science and technology to meet the evolving demands of the world.',
            summary: 'A unique blend of academic rigor in physics and astrophysics with practical expertise in computer science, driving innovation through data analysis, machine learning, and entrepreneurial initiatives.'
        };
    }

    /**
     * @brief Generates astrophysics research content
     * @private
     * @returns {Array} Array of research project cards
     */
    getAstrophysicsContent() {
        return [
            {
                id: 'dark-matter-research',
                title: 'Desvendando o Invisível: Minha Jornada na Pesquisa de Matéria Escura',
                description: 'Minha pesquisa em Matéria Escura começou com um mergulho profundo nas curvas de rotação galácticas. As velocidades anômalas das estrelas nos halos galácticos apresentaram um enigma profundo: ou as leis da gravidade precisavam de revisão, ou uma vasta quantidade de matéria invisível estava em jogo. Isso me levou a explorar o conceito de Matéria Escura, uma substância misteriosa que interage gravitacionalmente, mas não eletromagneticamente. Um momento crucial em minha compreensão veio do estudo do Aglomerado Bala, uma colisão cósmica onde o lenteamento gravitacional revelou uma distribuição de massa muito superior à matéria visível. A separação da matéria comum e escura durante esta colisão forneceu evidências visuais convincentes para a existência da Matéria Escura. Tive o privilégio de apresentar essas descobertas no Primeiro Ciclo de Seminários de Astronomia da UNIFAL-MG, transformando anos de observação em rigor teórico e compartilhando as fronteiras da cosmologia com uma audiência cativada. Esta experiência reforçou minha crença na educação superior como um motor vital para pesquisa e extensão, preenchendo a lacuna entre o fascínio telescópico e a astrofísica teórica.',
                image: {
                    src: 'bullet-cluster-black-matter_upscayl.png',
                    alt: 'Aglomerado Bala mostrando a distribuição de matéria escura, uma evidência chave para a matéria escura',
                    caption: 'Aglomerado Bala: Evidência visual de Matéria Escura (Crédito: NASA/CXC/M.Weiss)'
                },
                links: [
                    { url: 'https://lnkd.in/deYnab4a', label: 'Publicação de Pesquisa Relacionada', type: 'external' }
                ],
                tags: ['Matéria Escura', 'Dinâmica Galáctica', 'Cosmologia', 'Lenteamento Gravitacional', 'Comunicação Científica'],
                status: 'published',
                date: '2018-03-15'
            },
            {
                id: 'astronomy-seminar',
                title: 'Série de Seminários de Astronomia: Órbitas Estelares e o Universo Escuro',
                description: 'Esta imagem captura um momento significativo: uma palestra que proferi no Primeiro Ciclo de Seminários de Astronomia da UNIFAL-MG. Minha apresentação focou em Órbitas Estelares na Galáxia, onde compartilhei simulações de movimentos estelares baseadas em modelos de distribuição de massa e soluções numéricas para acelerações, velocidades e posições estelares na Via Láctea. Discuti as evidências que levaram aos postulados de Matéria Escura e Gravidade Modificada, destacando particularmente as Curvas de Rotação de galáxias. Esta anomalia, onde as estrelas no halo galáctico se movem muito rápido, sugere que a maior parte da massa da Via Láctea é invisível. Compartilhar essas ideias complexas e desafiar a audiência com os mistérios do cosmos foi uma experiência profunda, reforçando o papel do ensino superior em impulsionar tanto a pesquisa quanto o engajamento público.',
                image: {
                    src: 'seminario.jpg',
                    alt: 'Apresentação de seminário de astronomia sobre órbitas estelares e matéria escura',
                    caption: 'Apresentação sobre Órbitas Estelares e Matéria Escura no Seminário da UNIFAL-MG (2019)'
                },
                links: [],
                tags: ['Scientific Outreach', 'Academic Events', 'Stellar Dynamics', 'Dark Matter', 'Public Speaking'],
                status: 'completed',
                date: '2019-11-20' // Adjusted date to reflect the lecture event more accurately
            },
            {
                id: 'ccc-tl-cosmology',
                title: 'Exploring Alternative Cosmologies: CCC+TL and Baryon Acoustic Oscillations',
                description: 'Beyond Dark Matter, my curiosity extends to alternative cosmological models. A recent study in \"The Astrophysical Journal\" on \"Testing CCC+TL Cosmology with Baryon Acoustic Oscillation Features\" offers a fascinating perspective. It proposes that the universe\´s forces weaken as it expands, creating an illusion of dark energy driving accelerated expansion. On galactic scales, this variation in forces within gravitationally bound systems could explain the \"extra gravity\" attributed to dark matter. This research highlights the ongoing quest to understand the fundamental forces shaping our universe and the intricate interplay between theory and observation in modern cosmology.',
                links: [
                    { url: 'https://lnkd.in/dwsKCSbM', label: 'The Astrophysical Journal Publication', type: 'external' }
                ],
                tags: ['Cosmology', 'Dark Energy', 'Dark Matter', 'Baryon Acoustic Oscillation', 'Theoretical Physics'],
                status: 'published',
                date: '2024-01-01' // Assuming a recent publication date
            }
        ];
    }

    /**
     * @brief Generates observatory content with research and outreach activities
     * @private
     * @returns {Array} Array of observatory activity items
     */
    getObservatoryContent() {
        return [
            {
                id: 'unifal-observatory-outreach',
                title: 'Uma Janela para o Universo: Extensão Científica e Pesquisa na UNIFAL-MG',
                description: 'Durante meu tempo como membro da equipe do Observatório Astronômico da UNIFAL-MG (2015 a 2018), tive o privilégio de conectar mais de 2.000 visitantes de Alfenas e região às maravilhas do cosmos. Como divulgador científico, utilizei nosso magnífico telescópio Cassegrain de 380mm para revelar as impressionantes crateras da Lua, os majestosos anéis de Saturno, as luas galileanas de Júpiter e a beleza dos aglomerados estelares. Essas experiências, compartilhadas com colegas como José Carlos da Silva e o Professor Artur Justiniano, reforçaram minha crença na ciência aberta e na educação não formal. Era mais do que apenas observar; era sobre inspirar curiosidade, reflexão e pensamento crítico em todas as idades, desde crianças fascinadas até membros da comunidade acadêmica e idosos. Este período foi fundamental para moldar meu compromisso em tornar a ciência acessível e envolvente.',
                image: {
                    src: 'observatorio-unifal.jpg',
                    alt: 'Observatório Astronômico da UNIFAL-MG com um telescópio Cassegrain',
                    caption: 'Observatório Astronômico da UNIFAL-MG: Inspirando a próxima geração de cientistas'
                },
                links: [],
                tags: ['Extensão Científica', 'Astronomia', 'Educação', 'Engajamento Público', 'Telescópio Cassegrain'],
                status: 'completed',
                date: '2018-12-01'
            },
            {
                id: 'observatory-astrophotography',
                title: 'Astrofotografia e Pesquisa de Exoplanetas no Observatório da UNIFAL-MG',
                description: 'Além da extensão pública, o Observatório da UNIFAL-MG foi um centro de pesquisa e astrofotografia. Testemunhei e contribuí para conquistas significativas, incluindo o trabalho pioneiro do meu colega José Carlos na detecção do trânsito do exoplaneta WASP-76b. Meus próprios esforços em astrofotografia me levaram a capturar imagens impressionantes, como a Galáxia do Sombreiro (M104/NGC 4594) em uma exposição de 34 minutos e os braços espirais da Galáxia do Catavento do Sul (M83/NGC 5236). Também tive a oportunidade única de guiar minha primeira turma, o 3º EJA de Divisa Nova - MG, através de uma sessão prática de observação no observatório. Mesmo após o término do meu envolvimento institucional, minha paixão pela observação continuou, culminando na experiência emocionante de contemplar o cometa de longo período C/2020 F3 (NEOWISE) em 2020. Essas experiências solidificaram minhas habilidades em aquisição de dados, processamento de imagens e análise científica.',
                image: {
                    src: 'obsLua.jpg',
                    alt: 'Observação da Lua', 
                    caption: 'Vista detalhada da Lua capturada no Observatório da UNIFAL-MG'
                },
                image: {
                    src: 'obsGalaxiaSombrero.jpg',
                    alt: 'Galáxia do Sombreiro', 
                    caption: 'Galáxia do Sombreiro (M104/NGC 4594) capturada por astrofotografia'
                },
                highlights: [
                    'Contribuição para a detecção de trânsito de exoplanetas (WASP-76b)',
                    'Realização de astrofotografia de objetos de céu profundo (Galáxia do Sombreiro, Galáxia do Catavento do Sul)',
                    'Condução de aulas práticas de astronomia e observação do Cometa C/2020 F3 (NEOWISE)'
                ],
                date: '2015-2020'
            }
        ];
    }

    /**
     * @brief Generates CRAAM visit content
     * @private
     * @returns {Array} Array of CRAAM visit items
     */
    getCraamContent() {
        return [
            {
                id: 'craam-radio-polarimeter',
                title: 'Explorando a Radioastronomia Solar no CRAAM: Um Mergulho Profundo na Instrumentação',
                description: 'Em 2019, pouco depois de concluir meu curso de Física na UNIFAL-MG, tive a distinta honra de visitar o CRAAM (Centro de Rádio Astronomia e Astrofísica Mackenzie), uma instituição de pesquisa pioneira no Brasil desde 1960. O ponto alto desta visita foi a oportunidade de aprender e operar o Polarímetro Solar de Rádio de 7 GHz, um instrumento crítico para monitorar nossa estrela hospedeira. Guiado pelo colega Raphael Cesar Pimenta e pelo engenheiro Amauri Shossei Kudaka, obtive insights inestimáveis sobre os intrincados sistemas eletrônicos e computacionais que processam dados solares. A engenharia de precisão necessária para a aquisição e análise de dados foi realmente impressionante. Subindo ao local de instalação do polarímetro, protegido por sua cúpula, testemunhei em primeira mão a escala da infraestrutura de pesquisa. A antena de 1,5 metro, posicionada em direção ao céu, capta emissões de rádio polarizadas circularmente do Sol. Este equipamento, operando a 7 GHz, é crucial para a pesquisa do CRAAM, que se concentra no monitoramento da atividade solar, detecção de fenômenos energéticos como explosões solares e revelação das propriedades magnéticas da atmosfera solar. Esta experiência foi uma lição profunda em Instrumentação e Radioastronomia, reforçando minha paixão pela Física Solar e destacando as significativas contribuições da pesquisa brasileira no cenário internacional. As colaborações do CRAAM com instituições como o INPE e seu envolvimento em projetos como o voo do balão estratosférico Solar-T na Antártica são verdadeiramente inspiradoras.',
                images: [
                    { src: 'craamAntena.jpg', alt: 'Antena do Polarímetro Solar de Rádio no CRAAM', caption: 'Polarímetro Solar de Rádio de 7 GHz (CRAAM)' },
                    { src: 'craamControle.jpg', alt: 'Sala de controle do CRAAM', caption: 'Sala de Controle do CRAAM: Inspecionando sistemas eletrônicos e computacionais' },
                    { src: 'craamDomo.jpg', alt: 'Interior da cúpula do CRAAM', caption: 'Dentro da Cúpula do CRAAM: Antena de 1,5 metro' },
                    { src: 'craamEscada.jpg', alt: 'Escada externa do CRAAM', caption: 'Escada externa para o deck de observação' }
                ],
                highlights: [
                    'Operou o Polarímetro Solar de Rádio de 7 GHz',
                    'Obteve insights sobre o monitoramento da atividade solar e análise de propriedades magnéticas',
                    'Explorou a aquisição e processamento complexo de dados em radioastronomia'
                ],
                date: '2019'
            }
        ];
    }

    /**
     * @brief Generates content about the LNA Zeiss Telescope experience
     * @private
     * @returns {Array} Array of LNA Zeiss Telescope experience items
     */
    getLNATelescopeContent() {
        return [
            {
                id: 'lna-zeiss-operation',
                title: 'Operando o Histórico Telescópio Zeiss no LNA: Uma Jornada Através do Tempo e da Ciência',
                description: 'Durante meu curso de Física na UNIFAL-MG (2014-2018), tive a extraordinária oportunidade de operar, por duas noites em 2016, um instrumento verdadeiramente especial no Laboratório Nacional de Astrofísica (LNA/OPD). Este não era um telescópio comum; era um Zeiss histórico, adquirido da antiga Alemanha Oriental nas décadas de 1960/70 através de uma fascinante negociação envolvendo café. Após anos em armazenamento, foi finalmente montado em 1983 no Observatório do Pico dos Dias. Este clássico telescópio Cassegrain, com sua primária parabólica e secundária hiperbólica, apresenta uma razão focal de f/12.5 no foco Cassegrain e requer apontamento manual. É exclusivamente dedicado à fotometria e polarimetria, permitindo estudos precisos da luz de estrelas e galáxias, revelando detalhes intrincados que apenas instrumentos meticulosamente calibrados podem capturar. Operar o Zeiss foi uma experiência profunda: desde a preparação das observações e coleta de dados até a calibração do instrumento, cada detalhe e ajuste ressaltou a busca essencial pelo conhecimento. Mais do que apenas habilidade técnica, foi uma imersão no rico legado científico que ele incorpora, um poderoso lembrete de que a ciência prospera com paciência, precisão e curiosidade insaciável. Esta experiência não apenas aprofundou minha paixão por dados e por observar o universo, mas também permanece como uma das memórias mais queridas da minha jornada acadêmica, destacando o fascínio duradouro da exploração astronômica.',
                images: [
                    { src: 'obs4.jpg', alt: 'Observatório do LNA ao pôr do sol', caption: 'Observatório do Pico dos Dias (LNA) ao pôr do sol, um cenário sereno para a descoberta científica' },
                    { src: 'obs5.jpg', alt: 'Vista aérea do Observatório do LNA', caption: 'Vista aérea do Laboratório Nacional de Astrofísica (LNA), mostrando sua impressionante infraestrutura' }
                ],
                highlights: [
                    'Operou um telescópio Cassegrain Zeiss histórico para fotometria e polarimetria',
                    'Adquiriu experiência prática na coleta de dados astronômicos e calibração de instrumentos',
                    'Imersão no legado científico de um dos principais observatórios do Brasil'
                ],
                date: '2016'
            }
        ];
    }

    /**
     * @brief Generates education and teaching experience content
     * @private
     * @returns {Array} Array of education timeline items
     */
    getEducationContent() {
        return [
            {
                period: '2016-2018',
                role: 'Monitor de Ensino, Departamento de Física da UNIFAL-MG',
                description: 'Durante meus estudos de graduação, atuei como Monitor de Ensino no Departamento de Física da UNIFAL-MG. Este papel foi fundamental para o desenvolvimento das minhas habilidades pedagógicas, pois fui responsável pela instrução laboratorial para cursos de física de graduação, desenvolvimento de protocolos experimentais e fornecimento de mentoria e apoio acadêmico aos alunos. Encontrei imensa satisfação em ajudar os alunos a compreender conceitos complexos através de experimentos práticos, e contribuí para a criação de novos e envolventes materiais de laboratório. Esta experiência solidificou minha compreensão dos princípios fundamentais da física e minha capacidade de comunicá-los de forma eficaz.',
                highlights: [
                    'Forneceu instrução laboratorial e apoio acadêmico a estudantes de física de graduação',
                    'Desenvolveu e refinou protocolos experimentais para cursos de física',
                    'Orientou estudantes, promovendo uma compreensão mais profunda de conceitos científicos'
                ]
            },
            {
                period: '2017-2018',
                role: 'Desenvolvedor de Material Educacional, Observatório Astronômico da UNIFAL-MG',
                description: 'Minha paixão pela astronomia se estendeu à extensão educacional no Observatório Astronômico da UNIFAL-MG. Como Desenvolvedor de Material Educacional, liderei a criação de materiais envolventes de educação em astronomia e desempenhei um papel fundamental no desenvolvimento e coordenação de programas e workshops de extensão pública. Através dessas iniciativas, alcancei mais de 500 estudantes, fomentando a curiosidade científica e desenvolvendo metodologias de ensino inovadoras que tornaram fenômenos astronômicos complexos acessíveis e emocionantes. Esta experiência destacou a importância da comunicação científica e seu poder de inspirar a próxima geração.',
                highlights: [
                    'Criou e implementou materiais de educação em astronomia para extensão pública',
                    'Desenvolveu e coordenou programas e workshops de extensão pública bem-sucedidos',
                    'Alcançou mais de 500 estudantes, fomentando a curiosidade científica e metodologias de ensino inovadoras'
                ]
            },
            {
                period: '2019-2022',
                role: 'Professor de Física, Secretaria de Estado de Educação de Minas Gerais',
                description: 'Após meus estudos de graduação, dediquei-me à educação, lecionando Física em três municípios de Minas Gerais. Este papel me desafiou a adaptar o conhecimento científico a diversas audiências, especialmente durante o período sem precedentes de 2020-2022, onde apliquei expertise técnica para superar obstáculos educacionais. Desenvolvi estratégias de ensino inovadoras, incluindo laboratórios virtuais e conteúdo online interativo, para garantir a aprendizagem contínua durante a educação remota. Esta experiência aprimorou significativamente minha capacidade de comunicar conceitos científicos complexos de forma acessível e envolvente, promovendo o pensamento crítico e habilidades de resolução de problemas entre meus alunos.',
                highlights: [
                    'Lecionou Física em três municípios, adaptando o currículo às diversas necessidades dos alunos',
                    'Desenvolveu estratégias de ensino inovadoras, incluindo laboratórios virtuais e conteúdo online interativo',
                    'Navegou com sucesso os desafios da educação remota durante 2020-2022, garantindo a aprendizagem contínua'
                ]
            }
        ];
    }

    /**
     * @brief Generates innovation and entrepreneurship content
     * @private
     * @returns {Array} Array of innovation project cards
     */
getInnovationContent() {
        return [
            {
                id: 'nidustec-incubator-experience',
                title: 'Incubadora de Empresas NidusTec: Conectando Academia e Empreendedorismo',
                description: 'Em 2023, iniciei uma nova jornada acadêmica, cursando Bacharelado em Ciência da Computação na UNIFAL-MG (2023–2029). Concomitantemente, tive a inestimável oportunidade de integrar a equipe da Incubadora de Empresas de Base Tecnológica NidusTec/UNIFAL-MG (2024–2025). Este período foi transformador, permitindo-me transitar de tarefas operacionais para contribuições estratégicas. Como generalista Maker, liderei projetos de Robótica, Modelagem 3D e oficinas de CNC, aplicando técnicas de Computação Gráfica e Processamento de Imagens para desenvolver protótipos multidisciplinares. Esses projetos não apenas enriqueceram as atividades de ensino, pesquisa e extensão, mas também atenderam às necessidades de infraestrutura institucional nos três campi da UNIFAL-MG. Esta experiência ampliou meus horizontes em Propriedade Intelectual, Empreendedorismo, dinâmica Universidade-Mercado, Inovação Aberta e Transferência de Tecnologia. Monitorei ativamente startups incubadas, apoiei estratégias de mobilização de recursos e contribuí para o alinhamento da incubadora com o modelo CERNE (Centro de Referência para Apoio a Novos Empreendimentos), gerenciando 29 procedimentos. Esta trajetória me moldou como um aplicador de conhecimento, unindo ciência e tecnologia para atender às demandas contemporâneas, fomentando novos negócios e iniciativas de inovação.',
                image: {
                    src: 'nidus.jpg',
                    alt: 'Rafael no Laboratório NidusTec', 
                    caption: 'Trabalhando como generalista Maker na NidusTec, fomentando inovação e empreendedorismo'
                },
                focusAreas: [
                    'Transferência de Tecnologia',
                    'Mentoria de Startups',
                    'Ecossistemas de Inovação',
                    'Educação Maker',
                    'Modelagem 3D e CNC',
                    'Propriedade Intelectual',
                    'Empreendedorismo'
                ],
                impact: {
                    startupsSupported: 'Monitorou e apoiou startups incubadas',
                    projects: 'Desenvolveu protótipos de Robótica, Modelagem 3D e CNC para aplicações multidisciplinares',
                    partnerships: 'Gerenciou 29 procedimentos do modelo CERNE, alinhando a incubadora com os objetivos de inovação'
                },
                links: [
                    { url: 'https://jornal.unifal-mg.edu.br/capacitacoes-promovidas-pela-agencia-de-inovacao-e-a-incubadora-de-empresas-no-mes-de-junho-estimulam-a-cultura-empreendedora-e-a-inovacao-tecnologica-junto-a-comunidade/', label: 'Notícias UNIFAL-MG: Capacitações Junho', type: 'external' },
                    { url: 'https://jornal.unifal-mg.edu.br/capacitacoes-promovidas-pela-agencia-de-inovacao-e-incubadora-de-empresas-de-base-tecnologica-impulsionam-a-criatividade-e-o-empreendedorismo/', label: 'Notícias UNIFAL-MG: Criatividade e Empreendedorismo', type: 'external' },
                    { url: 'https://jornal.unifal-mg.edu.br/agencia-de-inovacao-e-empreendedorismo-da-unifal-mg-promove-visita-tecnica-no-espaco-maker-a-calouros-do-bacharelado-em-quimica-da-instituicao/', label: 'Notícias UNIFAL-MG: Visita ao Espaço Maker', type: 'external' },
                    { url: 'https://jornal.unifal-mg.edu.br/calouros-vivenciam-inovacao-em-visitas-ao-laboratorio-maker-na-unifal-mg/', label: 'UNIFAL-MG News: Freshmen Innovation', type: 'external' },
                    { url: 'https://jornal.unifal-mg.edu.br/agencia-de-inovacao-de-empreendedorismo-da-unifal-mg-realiza-segunda-oficina-de-capacitacao-para-corte-a-laser-nos-laboratorios-maker-dos-campi-alfenas-e-pocos-de-caldas/', label: 'UNIFAL-MG News: Laser Cutting Workshop', type: 'external' },
                    { url: 'https://jornal.unifal-mg.edu.br/unifal-mg-realiza-workshop-de-empreendedorismo-e-inovacao-em-enfermagem-evento-e-promovido-pelo-programa-de-pos-graduacao-em-enfermagem-e-pela-liga-academica-de-enfermagem-neonatal-e-pediatrica-da-un/', label: 'UNIFAL-MG News: Nursing Entrepreneurship Workshop', type: 'external' },
                    { url: 'https://jornal.unifal-mg.edu.br/comunidade-academica-do-campus-varginha-adquire-habilidades-praticas-e-teoricas-na-area-da-cultura-maker-em-capacitacao-promovida-no-niduslab/', label: 'UNIFAL-MG News: Varginha Maker Culture', type: 'external' },
                    { url: 'https://www.unifal-mg.edu.br/i9unifal/maratona-de-ideias-senac-alfenas-i9-em-parceria-com-o-unis-cefet-varginha-e-cesullab/', label: 'UNIFAL-MG News: Idea Marathon', type: 'external' },
                    { url: 'https://jornal.unifal-mg.edu.br/unifal-mg-aprova-criacao-do-centro-de-inovacao-e-empreendedorismo-universitario-cieu/', label: 'UNIFAL-MG News: CIEU Creation', type: 'external' }
                ],
                date: '2024-2025'
            },
            {
                id: 'anprotec-award',
                title: 'ANPROTEC National Award for Innovative Entrepreneurship: Recognizing Excellence',
                description: 'A significant highlight of my involvement with NidusTec was the recognition received at the ANPROTEC National Award for Innovative Entrepreneurship. This prestigious award, specifically the Adelino Medeiros Trophy for \"Incubator of Companies,\" celebrates programs that successfully foster new innovative ventures. It acknowledges effective strategies in incubation, pre-incubation, pre-acceleration, and the selection and attraction of promising startups. This accolade underscores the impact of our collective efforts in building a robust innovation ecosystem and validates the innovative practices implemented at NidusTec during my tenure.',
                links: [
                    { url: 'https://anprotec.org.br/site/2024/12/premio-nacional-anprotec-de-empreendedorismo-inovador-2024-revela-vencedores-em-sao-jose-dos-campos/', label: 'ANPROTEC Award News', type: 'external' }
                ],
                tags: ['Award', 'ANPROTEC', 'Entrepreneurship', 'Innovation', 'Ecosystem Development'],
                status: 'awarded',
                date: '2024-12-04' // Assuming the award date is the same as the conference
            },
            {
                id: 'anprotec-publication',
                title: 'Publication: Methodology for Impact Measurement and CERNE Model Validation',
                description: 'My contributions to the innovation ecosystem also extended to academic publication. I co-authored a paper titled \"Development of Methodology for Measuring the Impacts and Validating the Implementation of the CERNE Model in Technology-Based Business Incubators.\" This research, presented at the 34th ANPROTEC Conference on December 4, 2024, in São José dos Campos, focused on refining metrics and validating the effectiveness of the CERNE model in fostering technology-based startups. Collaborating with Izabella Carneiro Bastos, Leonardo Contreras Pereira, and Laura de Bom Maimone dos Santos, this publication reflects my commitment to both practical application and theoretical understanding of innovation and entrepreneurship.',
                links: [
                    { url: 'https://anprotec.org.br/site/2024/12/premio-nacional-anprotec-de-empreendedorismo-inovador-2024-revela-vencedores-em-sao-jose-dos-campos/', label: 'ANPROTEC Award News', type: 'external' } // Link to the news article about the award/conference
                ],
                tags: ['Publication', 'ANPROTEC', 'CERNE Model', 'Incubators', 'Entrepreneurship', 'Research'],
                status: 'published',
                date: '2024-12-04'
            }
        ];
    }

    /**
     * @brief Generates deep learning projects content
     * @private
     * @returns {Array} Array of deep learning project cards
     */
getDeepLearningProjectsContent() {
        return [
            {
                id: 'elliptical-galaxy-brightness-profiles',
                title: 'Perfis de Brilho de Galáxias Elípticas: Desvendando Estruturas Galácticas com o Modelo de De Vaucouleurs',
                description: 'Em 2021, durante meu Mestrado em Física na UNIFEI, tive a enriquecedora oportunidade de aprofundar na Astrofísica Extragaláctica. Um projeto significativo envolveu o ajuste de perfis de brilho de galáxias elípticas utilizando o clássico perfil de De Vaucouleurs (1991). Selecionei as galáxias NGC 3522 e NGC 5628 a partir de dados do VizieR (Université de Strasbourg / CNRS), aplicando filtros específicos para declinação, magnitude, redshift e classificação morfológica. As imagens foram obtidas do Sloan Digital Sky Survey (SDSS). Minha metodologia abrangeu o recorte de campo, utilizando rotinas de isófotas do Astropy (integrando a rotina ellipse do IRAF), convertendo intensidades de nanomaggies para Jansky, e transformando semieixos de pixels para segundos de arco. Este processo me permitiu estimar parâmetros físicos cruciais como raio efetivo, brilho superficial e luminosidade, que apresentaram excelente concordância com o NASA/IPAC Extragalactic Database (NED). Este projeto marcou minha primeira experiência prática com VizieR, rotinas IRAF do Astropy, Python para análise de dados astronômicos e visualização DS9. Foi realmente fascinante testemunhar como o ajuste de isófotas poderia revelar detalhes sutis, mas profundos, dentro de galáxias elípticas, aprofundando minha apreciação pela pesquisa astronômica baseada em dados.',
                tags: ['Astrofísica', 'Astrofísica Extragaláctica', 'Morfologia de Galáxias', 'Análise de Dados', 'Python', 'Astropy', 'SDSS', 'VizieR'],
                status: 'completed',
                date: '2021'
            },
            {
                id: 'medical-image-diagnosis',
                title: 'Deep Learning para Diagnóstico de Imagens Médicas: Uma Jornada na Detecção de Câncer de Pele',
                description: 'Minha exploração em Machine Learning e Deep Learning me levou a uma aplicação convincente: o diagnóstico de câncer de pele a partir de imagens médicas. Utilizando conjuntos de dados de referência como ISIC 2018 Challenge e HAM10000 (Tschandl, Rosendahl & Kittler, 2018), desenvolvi um pipeline abrangente. Este pipeline integrou Astropy e Photutils para extração de brilho radial, t-SNE para redução de dimensionalidade, Random Forest como linha de base e CNNs em Keras/TensorFlow para combinar imagens com perfis radiais. O conjunto de dados inicial compreendia 10.015 imagens dermatoscópicas, servindo como um robusto conjunto de treinamento para aprendizado de máquina acadêmico. Os casos cobriam um amplo espectro de lesões pigmentadas, incluindo ceratoses actínicas, carcinoma basocelular, lesões benignas tipo ceratose, dermatofibroma, melanoma, nevos melanocíticos e lesões vasculares. \n\nInicialmente, os resultados não foram promissores, com precisão em torno de 0.498, F1-score (ponderado) ~0.334 e ROC AUC ~0.499, indicando que a rede aprendeu principalmente apenas uma classe. Este experimento fascinante, embora não imediatamente bem-sucedido, forneceu lições inestimáveis sobre integração de bibliotecas, limites de generalização e o processo científico de explorar o improvável. \n\n**Correção e Refatoração:**\nRefletindo sobre os desafios iniciais, percebi o erro em reduzir excessivamente a dimensionalidade do conjunto de dados sem agrupamento prévio. Isso levou o modelo a ignorar metadados cruciais de contexto clínico (7 características por imagem) e a reforçar o viés em relação à classe majoritária (nevos melanocíticos). Uma refatoração completa da arquitetura de treinamento foi necessária. Ao combinar tensores extraídos de isófotas (capturando perfis radiais de cor, textura de borda e intensidade) com metadados de contexto clínico, gerei quase 24 milhões de pontos de dados treináveis. Apesar das limitações de hardware (Intel© Core™ i7-8565U CPU @ 1.80GHz × 4, 8 GB RAM), otimizei o processamento em 50 épocas com 439 lotes cada, totalizando aproximadamente 25 horas de treinamento mais 11 horas de ajuste fino para validação. Ignorar temporariamente casos benignos forçou o modelo a aprender padrões de classes minoritárias (malignas). No final, alcancei um recall convergindo entre 82% e 85% para melanomas (casos malignos) e 95% a 98% para nevos (casos benignos). Embora muito ainda precise ser feito — incluindo a revisão da análise exploratória de dados, ajuste da arquitetura e exploração de novas estratégias de balanceamento de conjuntos de dados — este projeto continua sendo uma profunda experiência de aprendizado na construção de modelos de deep learning confiáveis e robustos para diagnóstico médico.',
                links: [
                    { url: 'https://lnkd.in/dcUAP2gw', label: 'Notebook Kaggle [Código]', type: 'external' },
                    { url: 'https://lnkd.in/d5jSmE2H', label: 'Referência do Conjunto de Dados [Artigo]', type: 'external' },
                    { url: 'https://lnkd.in/dp4ubfGD', label: 'Contexto de Redução de Dimensionalidade', type: 'external' }
                ],
                tags: ['Deep Learning', 'Imagens Médicas', 'Diagnóstico de Câncer de Pele', 'Machine Learning', 'CNNs', 'Ciência de Dados', 'Astropy', 'Photutils', 'Keras', 'TensorFlow'],
                status: 'ongoing',
                date: '2021-Presente'
            }
        ];
    }

    /**
     * @brief Generates technical and scientific projects content
     * @private
     * @returns {Array} Array of project cards with technical details
     */
    getHobbiesContent() {
        return {
            description: 'Além das minhas atividades acadêmicas e profissionais, cultivo uma variedade de hobbies que enriquecem minha vida e proporcionam novas perspectivas. Essas atividades não são apenas passatempos, mas partes integrantes de quem eu sou.',
            items: [
                {
                    id: 'gardening',
                    title: 'Jardinagem',
                    description: 'Encontro imensa alegria em cultivar uma horta, uma prática que me conecta com a natureza e me ensina paciência e resiliência. É uma forma tangível de ver os resultados do cuidado e da dedicação.',
                    icon: 'leaf',
                    image: '.hobbies/gardening.jpg'
                },
                {
                    id: 'reading',
                    title: 'Leitura',
                    description: 'Sou um ávido leitor de ficção científica, fantasia e ciência popular. Livros são minha porta de entrada para novos mundos e ideias, alimentando minha imaginação e minha paixão por aprender.',
                    icon: 'book-open',
                    image: '.reading.jpg'
                },
                {
                    id: 'tinkering',
                    title: 'Projetos DIY e Eletrônica',
                    description: 'Como uma pessoa prática, adoro mexer com eletrônica, construir circuitos e trabalhar em projetos DIY. Esse espírito maker é uma fonte constante de criatividade e resolução de problemas.',
                    icon: 'tools',
                    image: '.tinkering.jpg'
                },
                {
                    id: 'astrophotography',
                    title: 'Astrofotografia',
                    description: 'Combinando meu amor pela astronomia e tecnologia, gosto de capturar imagens do céu noturno. É um hobby desafiador, mas recompensador, que me permite compartilhar a beleza do cosmos com outras pessoas.',
                    icon: 'camera',
                    image: '.astrophotography.jpg'
                }
            ]
        };
    }

    getProjectsContent() {
        return [
            {
                id: 'interactive-portfolio-website',
                title: 'Site de Portfólio Interativo: Uma Reflexão Digital',
                description: 'Este site de portfólio pessoal é um testemunho da minha jornada e habilidades, construído com uma filosofia de design moderna, minimalista e responsiva. Ele utiliza JavaScript puro, aderindo estritamente ao padrão de arquitetura MVC, para garantir modularidade, manutenibilidade e entrega de conteúdo dinâmico. O site é projetado para contar minha história, destacando minhas diversas experiências em física, ciência da computação, astrofísica, educação, empreendedorismo e vários hobbies. Ele incorpora tipografia clássica, elementos sutis de computação retrô e transições suaves para criar uma experiência de usuário intuitiva e envolvente. A população dinâmica de conteúdo, incluindo texto rico e imagens, garante uma abordagem de contar histórias que conecta minha linha do tempo linearmente, permitindo uma exploração mais profunda de eventos específicos.',
                technologies: ['JavaScript', 'CSS3', 'HTML5', 'Arquitetura MVC', 'Vite (Ferramenta de Build)', 'GitHub Pages (Implantação)'],
                status: 'concluído',
                repository: 'https://github.com/rafaelpassosdomingues/rafaelpassosdomingues.github.io',
                liveDemo: 'https://rafaelpassosdomingues.github.io',
                features: [
                    'Design Responsivo em todos os dispositivos',
                    'Desempenho Otimizado para tempos de carregamento rápidos',
                    'Conformidade com Acessibilidade para experiência de usuário inclusiva',
                    'Carregamento Dinâmico de Conteúdo com abordagem de contar histórias',
                    'Arquitetura MVC Modular para escalabilidade e manutenibilidade',
                    'Elementos de UI/UX retro-futuristas com tipografia clássica'
                ]
            }
        ];
    }

    /**
     * @brief Generates skills and competencies matrix
     * @private
     * @returns {Object} Structured skills data by categories and proficiency levels
     */
    getSkillsContent() {
        return {
            categories: [
                {
                    category: 'Habilidades Técnicas',
                    skills: [
                        { name: 'Física e Astrofísica', proficiency: 95, years: 8, description: 'Profundo entendimento das leis físicas e fenômenos astronômicos.' },
                        { name: 'Ciência e Análise de Dados', proficiency: 90, years: 6, description: 'Expertise em análise estatística, modelagem de dados e extração de insights de conjuntos de dados complexos.' },
                        { name: 'Python (NumPy, Pandas, Scikit-learn)', proficiency: 88, years: 5, description: 'Proficiência avançada em Python para computação científica, manipulação de dados e aprendizado de máquina.' },
                        { name: 'Machine Learning e Deep Learning', proficiency: 85, years: 4, description: 'Experiência no desenvolvimento e aplicação de modelos de ML/DL para tarefas como classificação de imagens e análise preditiva.' },
                        { name: 'JavaScript (ES6+)', proficiency: 80, years: 3, description: 'Sólidas habilidades em JavaScript moderno para construir aplicações web interativas.' },
                        { name: 'Modelagem 3D e CNC', proficiency: 78, years: 2, description: 'Proficiente na criação de modelos 3D para impressão e usinagem CNC.' },
                        { name: 'Robótica e Prototipagem', proficiency: 75, years: 2, description: 'Experiência prática na construção e programação de sistemas robóticos e protótipos eletrônicos.' }
                    ]
                },
                {
                    category: 'Habilidades Interpessoais e Criativas',
                    skills: [
                        { name: 'Pensamento Analítico e Conceitual', proficiency: 96, years: 8, description: 'Capacidade de desconstruir problemas complexos e desenvolver soluções inovadoras e conceituais.' },
                        { name: 'Ideação Criativa e Ambição', proficiency: 91, years: 7, description: 'Impulsionado a gerar novas ideias e perseguir metas ambiciosas com determinação.' },
                        { name: 'Estabilidade Emocional e Reflexão', proficiency: 89, years: 8, description: 'Mantém a compostura sob pressão e se envolve em autorreflexão ponderada para melhoria contínua.' },
                        { name: 'Resolução de Problemas e Iniciativa', proficiency: 88, years: 7, description: 'Identifica proativamente desafios e toma a iniciativa para implementar soluções eficazes.' },
                        { name: 'Arquitetura de Soluções', proficiency: 85, years: 4, description: 'Habilidoso em projetar e arquitetar soluções abrangentes que atendam aos requisitos técnicos e de negócios.' },
                        { name: 'Flexibilidade e Adaptabilidade', proficiency: 80, years: 6, description: 'Adapta-se rapidamente a novos desafios e ambientes em mudança, demonstrando alta flexibilidade.' }
                    ]
                }
            ]
        };

    }

    /**
     * @brief Loads and initializes projects content
     * @private
     * @returns {Promise<void>} Resolves when projects are loaded
     */
    async loadProjectsContent() {
        try {
            // Projects are now primarily handled within specific section content getters (e.g., getDeepLearningProjectsContent)
            // This method can be used for general projects not tied to a specific narrative section.
            this.projects = this.getProjectsContent(); // Call the getter to populate projects if needed
            this.cacheContent('projects', this.projects);
            console.debug(`ContentModel: Loaded ${this.projects.length} projects.`);
        } catch (error) {
            console.error('ContentModel: Failed to load projects content:', error);
            throw error;
        }
    }

    /**
     * @brief Loads and initializes experiences content
     * @private
     * @returns {Promise<void>} Resolves when experiences are loaded
     */
    async loadExperiencesContent() {
        try {
            // Experiences are now primarily handled within specific section content getters (e.g., getAboutContent timeline)
            // This method can be used for general experiences not tied to a specific narrative section.
            this.experiences = []; // No general experiences, all are in sections
            this.cacheContent('experiences', this.experiences);
            console.debug(`ContentModel: Loaded ${this.experiences.length} experiences.`);
        } catch (error) {
            console.error('ContentModel: Failed to load experiences content:', error);
            throw error;
        }
    }

    /**
     * @brief Caches content for optimized retrieval
     * @private
     * @param {string} cacheKey - Unique identifier for the cached content
     * @param {*} content - Content to be cached
     */
    cacheContent(cacheKey, content) {
        if (!this.configuration.enableCaching) return;

        // Manage cache size
        if (this.contentCache.size >= this.configuration.maxCacheSize) {
            const firstKey = this.contentCache.keys().next().value;
            this.contentCache.delete(firstKey);
        }

        const cacheEntry = {
            data: content,
            timestamp: Date.now(),
            expires: Date.now() + this.configuration.cacheTimeout
        };

        this.contentCache.set(cacheKey, cacheEntry);
    }

    /**
     * @brief Retrieves cached content if valid
     * @private
     * @param {string} cacheKey - Key of the content to retrieve
     * @returns {*|null} Cached content or null if not found/expired
     */
    getCachedContent(cacheKey) {
        if (!this.configuration.enableCaching) return null;

        const cacheEntry = this.contentCache.get(cacheKey);
        if (!cacheEntry) return null;

        if (Date.now() > cacheEntry.expires) {
            this.contentCache.delete(cacheKey);
            return null;
        }

        return cacheEntry.data;
    }

    /**
     * @brief Retrieves all sections with optional filtering
     * @public
     * @param {Object} filters - Optional filters for section retrieval
     * @param {string} filters.type - Filter by content type
     * @param {boolean} filters.visible - Filter by visibility
     * @returns {Array} Array of section objects
     */
    getSections(filters = {}) {
        const cacheKey = `sections-${JSON.stringify(filters)}`;
        const cachedResult = this.getCachedContent(cacheKey);
        
        if (cachedResult) {
            return cachedResult;
        }

        let filteredSections = [...this.sections];

        if (filters.type) {
            filteredSections = filteredSections.filter(section => section.type === filters.type);
        }

        if (filters.visible !== undefined) {
            filteredSections = filteredSections.filter(section => 
                section.metadata.visible === filters.visible
            );
        }

        // Sort by priority and order
        filteredSections.sort((a, b) => {
            if (a.metadata.priority !== b.metadata.priority) {
                return a.metadata.priority - b.metadata.priority;
            }
            return a.metadata.order - b.metadata.order;
        });

        this.cacheContent(cacheKey, filteredSections);
        return filteredSections;
    }

    /**
     * @brief Retrieves a specific section by its identifier
     * @public
     * @param {string} sectionId - Unique identifier of the section
     * @returns {Object|undefined} Section object or undefined if not found
     */
    getSectionById(sectionId) {
        const cacheKey = `section-${sectionId}`;
        const cachedResult = this.getCachedContent(cacheKey);
        
        if (cachedResult) {
            return cachedResult;
        }

        const section = this.sections.find(sec => sec.id === sectionId);
        this.cacheContent(cacheKey, section);
        
        return section;
    }

    /**
     * @brief Retrieves all projects with optional filtering
     * @public
     * @param {Object} filters - Optional filters for project retrieval
     * @param {string} filters.category - Filter by project category
     * @param {string} filters.status - Filter by project status
     * @returns {Array} Array of project objects
     */
    getProjects(filters = {}) {
        let filteredProjects = [...this.projects];

        if (filters.category) {
            filteredProjects = filteredProjects.filter(project => 
                project.category === filters.category
            );
        }

        if (filters.status) {
            filteredProjects = filteredProjects.filter(project => 
                project.status === filters.status
            );
        }

        return filteredProjects;
    }

    /**
     * @brief Retrieves all experiences with optional filtering
     * @public
     * @param {Object} filters - Optional filters for experience retrieval
     * @param {string} filters.institution - Filter by institution
     * @returns {Array} Array of experience objects
     */
    getExperiences(filters = {}) {
        let filteredExperiences = [...this.experiences];

        if (filters.institution) {
            filteredExperiences = filteredExperiences.filter(experience => 
                experience.institution === filters.institution
            );
        }

        return filteredExperiences;
    }

    /**
     * @brief Gets all content data for initial rendering
     * @public
     * @returns {Object} Object containing all content data
     */
    getAllContent() {
        return {
            sections: this.getSections(),
            projects: this.getProjects(),
            experiences: this.getExperiences()
        };
    }

    /**
     * @brief Gets basic content for graceful degradation
     * @public
     * @returns {Object} Basic content data
     */
    getBasicContent() {
        return {
            introduction: 'Physicist and Computer Scientist passionate about astrophysics research, data analysis, and technology innovation. My journey is a blend of academic research and hands-on application, always driven by a curiosity for how the universe works and how we can use technology to solve real-world problems.',
            sections: this.getSections().slice(0, 3) // Only first 3 sections for fallback
        };
    }

    /**
     * @brief Searches content across all content types
     * @public
     * @param {string} searchTerm - Term to search for
     * @param {Object} options - Search options
     * @param {Array} options.contentTypes - Types of content to search
     * @param {number} options.maxResults - Maximum number of results to return
     * @returns {Object} Search results organized by content type
     */
    searchContent(searchTerm, options = {}) {
        const {
            contentTypes = ['sections', 'projects', 'experiences'],
            maxResults = 10
        } = options;

        if (!searchTerm || searchTerm.trim().length < 2) {
            return { sections: [], projects: [], experiences: [] };
        }

        const normalizedSearchTerm = searchTerm.toLowerCase().trim();
        const searchResults = {
            sections: [],
            projects: [],
            experiences: []
        };

        if (contentTypes.includes('sections')) {
            searchResults.sections = this.sections.filter(section =>
                section.title.toLowerCase().includes(normalizedSearchTerm) ||
                section.subtitle.toLowerCase().includes(normalizedSearchTerm) ||
                JSON.stringify(section.content).toLowerCase().includes(normalizedSearchTerm)
            ).slice(0, maxResults);
        }

        if (contentTypes.includes('projects')) {
            searchResults.projects = this.projects.filter(project =>
                project.title.toLowerCase().includes(normalizedSearchTerm) ||
                project.description.toLowerCase().includes(normalizedSearchTerm) ||
                project.technologies?.some(tech => 
                    tech.toLowerCase().includes(normalizedSearchTerm)
                )
            ).slice(0, maxResults);
        }

        if (contentTypes.includes('experiences')) {
            searchResults.experiences = this.experiences.filter(experience =>
                experience.title.toLowerCase().includes(normalizedSearchTerm) ||
                experience.institution.toLowerCase().includes(normalizedSearchTerm) ||
                experience.description.toLowerCase().includes(normalizedSearchTerm)
            ).slice(0, maxResults);
        }

        return searchResults;
    }

    /**
     * @brief Groups content by a specific property
     * @private
     * @param {Array} contentArray - Array of content items to group
     * @param {string} property - Property to group by
     * @returns {Object} Grouped content counts
     */
    groupContentByType(contentArray, property) {
        return contentArray.reduce((groups, item) => {
            const key = item[property] || 'unknown';
            groups[key] = (groups[key] || 0) + 1;
            return groups;
        }, {});
    }

    /**
     * @brief Calculates cache hit rate for performance monitoring
     * @private
     * @returns {number} Cache hit rate percentage
     */
    calculateCacheHitRate() {
        // Implementation for cache hit rate calculation
        // This would track cache hits/misses over time
        return 0.85; // Example value
    }

    /**
     * @brief Clears content cache
     * @public
     * @returns {number} Number of items cleared from cache
     */
    clearCache() {
        const cacheSize = this.contentCache.size;
        this.contentCache.clear();
        console.info(`ContentModel: Cleared ${cacheSize} items from cache.`);
        return cacheSize;
    }

    /**
     * @brief Updates configuration options
     * @public
     * @param {Object} newConfiguration - New configuration options
     */
    updateConfiguration(newConfiguration) {
        this.configuration = {
            ...this.configuration,
            ...newConfiguration
        };
        console.debug('ContentModel: Configuration updated.', this.configuration);
    }

    /**
     * @brief Destroys the content model and cleans up resources
     * @public
     */
    destroy() {
        this.clearCache();
        this.isInitialized = false;
        console.info('ContentModel: Content model destroyed and resources cleaned up.');
    }
}

export default ContentModel;

