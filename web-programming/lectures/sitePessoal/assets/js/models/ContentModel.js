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
                    icon: 'user',
                    backgroundColor: 'var(--color-surface)'
                }
            },
            {
                id: 'astrophysics',
                title: 'Astrophysics Research',
                subtitle: 'Work in galactic and extragalactic astrophysics',
                content: this.getAstrophysicsContent(),
                type: CONTENT_TYPES.CARDS.identifier,
                metadata: {
                    priority: 2,
                    visible: true,
                    order: 2,
                    icon: 'star',
                    backgroundColor: 'var(--color-gray-50)'
                }
            },
            {
                id: 'observatory',
                title: 'Astronomical Observatory',
                subtitle: 'Scientific outreach and research at UNIFAL-MG',
                content: this.getObservatoryContent(),
                type: CONTENT_TYPES.GALLERY.identifier,
                metadata: {
                    priority: 2,
                    visible: true,
                    order: 3,
                    icon: 'telescope',
                    backgroundColor: 'var(--color-surface)'
                }
            },
            {
                id: 'craam',
                title: 'CRAAM Visit',
                subtitle: 'Mackenzie Center for Radioastronomy and Astrophysics',
                content: this.getCraamContent(),
                type: CONTENT_TYPES.GALLERY.identifier,
                metadata: {
                    priority: 3,
                    visible: true,
                    order: 4,
                    icon: 'satellite',
                    backgroundColor: 'var(--color-gray-50)'
                }
            },
            {
                id: 'education',
                title: 'Education Experience',
                subtitle: 'Teaching and educational material development',
                content: this.getEducationContent(),
                type: CONTENT_TYPES.TIMELINE.identifier,
                metadata: {
                    priority: 2,
                    visible: true,
                    order: 5,
                    icon: 'graduation-cap',
                    backgroundColor: 'var(--color-surface)'
                }
            },
            {
                id: 'innovation',
                title: 'Innovation and Entrepreneurship',
                subtitle: 'NidusTec and innovation ecosystem',
                content: this.getInnovationContent(),
                type: CONTENT_TYPES.CARDS.identifier,
                metadata: {
                    priority: 2,
                    visible: true,
                    order: 6,
                    icon: 'lightbulb',
                    backgroundColor: 'var(--color-gray-50)'
                }
            },
            {
                id: 'projects',
                title: 'Projects and Development',
                subtitle: 'Technical and scientific works',
                content: this.getProjectsContent(),
                type: CONTENT_TYPES.CARDS.identifier,
                metadata: {
                    priority: 1,
                    visible: true,
                    order: 7,
                    icon: 'code',
                    backgroundColor: 'var(--color-surface)'
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
                    order: 8,
                    icon: 'cogs',
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
            introduction: 'Physicist and Computer Scientist passionate about astrophysics research, data analysis, and technology innovation.',
            timeline: [
                {
                    period: '2014-2018',
                    title: 'Bachelor of Physics',
                    institution: 'UNIFAL-MG',
                    description: 'Graduated with focus on astrophysics and scientific research',
                    highlights: ['Galactic and Extragalactic Astrophysics', 'Scientific Outreach']
                },
                {
                    period: '2016-2018',
                    title: 'Astrophysics Researcher',
                    institution: 'UNIFAL-MG Astronomical Observatory',
                    description: 'Research in galactic dynamics and dark matter studies',
                    highlights: ['Galactic Rotation Curves', 'Scientific Communication']
                },
                {
                    period: '2021-2023',
                    title: 'Master of Physics',
                    institution: 'UNIFEI',
                    description: 'Research in Active Galactic Nuclei and data analysis',
                    highlights: ['AGN Research', 'Advanced Data Analysis', 'Scientific Computing']
                },
                {
                    period: '2023-Present',
                    title: 'Computer Science Bachelor',
                    institution: 'UNIFAL-MG',
                    description: 'Integrating physics background with computer science expertise',
                    highlights: ['Software Development', 'Data Science', 'Machine Learning']
                },
                {
                    period: '2023-Present',
                    title: 'Innovation Ecosystem',
                    institution: 'NidusTec/UNIFAL-MG',
                    description: 'Bridging academia and market through technology innovation',
                    highlights: ['Entrepreneurship', 'Technology Transfer', 'Startup Ecosystem']
                }
            ],
            summary: 'Combining strong background in physics and astrophysics research with emerging expertise in computer science to solve complex problems through data-driven approaches and technological innovation.'
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
                title: 'Dark Matter Research',
                description: 'Study of galactic rotation curves and dark matter evidence through velocity dispersion analysis and gravitational lensing observations.',
                image: {
                    src: 'assets/images/bullet-cluster-black-matter_upscayl.png',
                    alt: 'Bullet Cluster showing dark matter distribution',
                    caption: 'Bullet Cluster - Dark Matter Evidence'
                },
                links: [
                    {
                        url: 'https://lnkd.in/deYnab4a',
                        label: 'Research Publication',
                        type: 'external'
                    }
                ],
                tags: ['Dark Matter', 'Galactic Dynamics', 'Gravitational Lensing'],
                status: 'published',
                date: '2018-03-15'
            },
            {
                id: 'astronomy-seminar',
                title: 'Astronomy Seminar Series',
                description: 'First Cycle of Astronomy Seminars at UNIFAL-MG featuring presentations on stellar orbits and dark matter research methodologies.',
                image: {
                    src: 'assets/images/seminario.jpg',
                    alt: 'Astronomy seminar presentation',
                    caption: 'Astronomy Seminar Presentation'
                },
                links: [],
                tags: ['Scientific Outreach', 'Academic Events', 'Stellar Dynamics'],
                status: 'completed',
                date: '2017-08-22'
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
                id: 'public-observing',
                title: 'Public Observing Sessions',
                description: 'Regular public astronomy nights with telescope observations and educational activities for community engagement.',
                images: [
                    {
                        src: 'assets/images/observatory-public-1.jpg',
                        alt: 'Public observing session at UNIFAL-MG observatory',
                        caption: 'Community Astronomy Night'
                    }
                ],
                statistics: {
                    participants: 500,
                    sessions: 24,
                    period: '2016-2018'
                }
            },
            {
                id: 'student-research',
                title: 'Student Research Projects',
                description: 'Undergraduate research projects in observational astronomy and data analysis techniques.',
                images: [
                    {
                        src: 'assets/images/student-research-1.jpg',
                        alt: 'Student research project presentation',
                        caption: 'Undergraduate Research'
                    }
                ],
                statistics: {
                    projects: 8,
                    students: 12,
                    publications: 2
                }
            }
        ];
    }

    /**
     * @brief Generates CRAAM visit content and experiences
     * @private
     * @returns {Array} Array of CRAAM visit experiences
     */
    getCraamContent() {
        return [
            {
                id: 'craam-tour',
                title: 'Research Facility Tour',
                description: 'Comprehensive tour of Mackenzie Center for Radioastronomy and Astrophysics research facilities and instrumentation.',
                images: [
                    {
                        src: 'assets/images/craam-tour-1.jpg',
                        alt: 'CRAAM research facility tour',
                        caption: 'Research Facility Exploration'
                    }
                ],
                highlights: [
                    'Radio telescope instrumentation',
                    'Data processing systems',
                    'Research methodologies'
                ]
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
                role: 'Teaching Assistant',
                institution: 'UNIFAL-MG Physics Department',
                responsibilities: [
                    'Laboratory instruction for undergraduate physics courses',
                    'Development of experimental protocols',
                    'Student mentoring and academic support'
                ],
                achievements: [
                    'Improved student comprehension through hands-on experiments',
                    'Developed new laboratory materials'
                ]
            },
            {
                period: '2017-2018',
                role: 'Educational Material Developer',
                institution: 'UNIFAL-MG Astronomical Observatory',
                responsibilities: [
                    'Creation of astronomy education materials',
                    'Public outreach program development',
                    'Workshop coordination and delivery'
                ],
                achievements: [
                    'Reached 500+ students through outreach programs',
                    'Developed innovative teaching methodologies'
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
                id: 'nidustec-incubator',
                title: 'NidusTec Business Incubator',
                description: 'Working at the intersection of academia and industry to foster technology innovation and startup development.',
                image: {
                    src: 'assets/images/nidustec-innovation.jpg',
                    alt: 'NidusTec innovation ecosystem',
                    caption: 'Innovation Ecosystem Development'
                },
                focusAreas: [
                    'Technology Transfer',
                    'Startup Mentoring',
                    'Innovation Ecosystems'
                ],
                impact: {
                    startupsSupported: 15,
                    projects: 8,
                    partnerships: 12
                }
            }
        ];
    }

    /**
     * @brief Generates technical and scientific projects content
     * @private
     * @returns {Array} Array of project cards with technical details
     */
    getProjectsContent() {
        return [
            {
                id: 'portfolio-website',
                title: 'Interactive Portfolio Website',
                description: 'Modern, responsive portfolio website built with vanilla JavaScript implementing MVC architecture and modern UX patterns.',
                technologies: ['JavaScript', 'CSS3', 'HTML5', 'MVC Architecture'],
                status: 'completed',
                repository: 'https://github.com/username/portfolio',
                liveDemo: 'https://rafaeldomain.com',
                features: [
                    'Responsive Design',
                    'Performance Optimized',
                    'Accessibility Compliant'
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
            technical: [
                {
                    category: 'Programming Languages',
                    skills: [
                        { name: 'Python', proficiency: 85, years: 4 },
                        { name: 'JavaScript', proficiency: 80, years: 3 },
                        { name: 'R', proficiency: 75, years: 3 },
                        { name: 'MATLAB', proficiency: 70, years: 2 }
                    ]
                },
                {
                    category: 'Data Analysis',
                    skills: [
                        { name: 'Pandas/Numpy', proficiency: 85, years: 4 },
                        { name: 'Statistical Analysis', proficiency: 80, years: 4 },
                        { name: 'Data Visualization', proficiency: 75, years: 3 },
                        { name: 'Machine Learning', proficiency: 70, years: 2 }
                    ]
                }
            ],
            scientific: [
                {
                    category: 'Astrophysics',
                    skills: [
                        { name: 'Galactic Dynamics', proficiency: 85, years: 4 },
                        { name: 'Data Reduction', proficiency: 80, years: 3 },
                        { name: 'Spectral Analysis', proficiency: 75, years: 3 }
                    ]
                }
            ],
            professional: [
                {
                    category: 'Research & Development',
                    skills: [
                        { name: 'Scientific Writing', proficiency: 85, years: 5 },
                        { name: 'Experimental Design', proficiency: 80, years: 4 },
                        { name: 'Project Management', proficiency: 75, years: 3 }
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
            this.projects = this.initializeProjects();
            this.cacheContent('projects', this.projects);
            console.debug(`ContentModel: Loaded ${this.projects.length} projects.`);
        } catch (error) {
            console.error('ContentModel: Failed to load projects content:', error);
            throw error;
        }
    }

    /**
     * @brief Initializes projects array with sample data
     * @private
     * @returns {Array} Array of project objects
     */
    initializeProjects() {
        return [
            {
                id: 'agn-research',
                title: 'Active Galactic Nuclei Research',
                description: 'Comprehensive analysis of AGN characteristics and emission patterns using spectroscopic data.',
                category: 'astrophysics',
                status: 'completed',
                technologies: ['Python', 'Astropy', 'Matplotlib'],
                repository: 'https://github.com/username/agn-research',
                date: '2023-06-15'
            }
        ];
    }

    /**
     * @brief Loads and initializes experiences content
     * @private
     * @returns {Promise<void>} Resolves when experiences are loaded
     */
    async loadExperiencesContent() {
        try {
            this.experiences = this.initializeExperiences();
            this.cacheContent('experiences', this.experiences);
            console.debug(`ContentModel: Loaded ${this.experiences.length} experiences.`);
        } catch (error) {
            console.error('ContentModel: Failed to load experiences content:', error);
            throw error;
        }
    }

    /**
     * @brief Initializes experiences array with sample data
     * @private
     * @returns {Array} Array of experience objects
     */
    initializeExperiences() {
        return [
            {
                id: 'unifal-observatory',
                title: 'Research Assistant - Astronomical Observatory',
                institution: 'UNIFAL-MG',
                period: '2016-2018',
                description: 'Conducted research in galactic astrophysics and participated in scientific outreach programs.',
                achievements: [
                    'Published research on galactic rotation curves',
                    'Organized public astronomy events'
                ]
            }
        ];
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
     * @brief Gets available content types and their configurations
     * @public
     * @returns {Object} Object containing all content type configurations
     */
    getContentTypes() {
        return { ...CONTENT_TYPES };
    }

    /**
     * @brief Checks if content model is fully initialized
     * @public
     * @returns {boolean} True if content model is initialized and ready
     */
    isContentModelReady() {
        return this.isInitialized;
    }

    /**
     * @brief Gets content statistics for monitoring and analytics
     * @public
     * @returns {Object} Object containing content statistics
     */
    getContentStatistics() {
        return {
            sections: {
                total: this.sections.length,
                byType: this.groupContentByType(this.sections, 'type')
            },
            projects: {
                total: this.projects.length,
                byCategory: this.groupContentByType(this.projects, 'category')
            },
            experiences: {
                total: this.experiences.length,
                byInstitution: this.groupContentByType(this.experiences, 'institution')
            },
            cache: {
                size: this.contentCache.size,
                hits: this.calculateCacheHitRate()
            }
        };
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