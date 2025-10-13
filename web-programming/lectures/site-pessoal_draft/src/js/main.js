// ===== CONTENT MODEL - COMPLETE AND DETAILED VERSION =====
class ContentModel {
    constructor() {
        this.sections = [];
        this.isInitialized = false;
    }

    async initializeContentModel() {
        try {
            this.sections = this.initializeSections();
            this.isInitialized = true;
            console.info('ContentModel: Content model initialized successfully');
        } catch (error) {
            console.error('ContentModel: Initialization failed:', error);
            throw error;
        }
    }

    initializeSections() {
        return [
            {
                id: 'about',
                title: 'About Me',
                subtitle: 'My academic and professional journey',
                type: 'timeline',
                content: this.getAboutContent(),
                metadata: { order: 1, visible: true }
            },
            {
                id: 'astrophysics-research',
                title: 'Astrophysics Research',
                subtitle: 'Work in galactic and extragalactic astrophysics',
                type: 'cards',
                content: this.getAstrophysicsContent(),
                metadata: { order: 2, visible: true }
            },
            {
                id: 'astronomical-observatory',
                title: 'Astronomical Observatory',
                subtitle: 'Scientific outreach and research at UNIFAL-MG',
                type: 'gallery',
                content: this.getObservatoryContent(),
                metadata: { order: 3, visible: true }
            },
            {
                id: 'craam-visit',
                title: 'CRAAM Visit',
                subtitle: 'Mackenzie Center for Radio Astronomy and Astrophysics',
                type: 'gallery',
                content: this.getCraamContent(),
                metadata: { order: 4, visible: true }
            },
            {
                id: 'lna-zeiss-telescope',
                title: 'LNA Zeiss Telescope Experience',
                subtitle: 'Operating a classic instrument at Pico dos Dias Observatory',
                type: 'gallery',
                content: this.getLnaTelescopeContent(),
                metadata: { order: 5, visible: true }
            },
            {
                id: 'education-experience',
                title: 'Education Experience',
                subtitle: 'Teaching and educational material development',
                type: 'timeline',
                content: this.getEducationContent(),
                metadata: { order: 6, visible: true }
            },
            {
                id: 'innovation-entrepreneurship',
                title: 'Innovation and Entrepreneurship',
                subtitle: 'NidusTec and innovation ecosystem',
                type: 'cards',
                content: this.getInnovationContent(),
                metadata: { order: 7, visible: true }
            },
            {
                id: 'deep-learning-projects',
                title: 'Deep Learning Projects',
                subtitle: 'Applying ML/DL to medical imaging and astrophysics',
                type: 'cards',
                content: this.getDeepLearningProjectsContent(),
                metadata: { order: 8, visible: true }
            },
            {
                id: 'skills',
                title: 'Skills and Competencies',
                subtitle: 'Knowledge areas and technologies',
                type: 'skills',
                content: this.getSkillsContent(),
                metadata: { order: 9, visible: true }
            }
        ];
    }

    getAboutContent() {
        return {
            timeline: [
                {
                    period: '2014-2018',
                    title: 'Bachelor\'s in Physics, UNIFAL-MG',
                    description: 'As a Physics student at UNIFAL-MG (2014-2018), I was a scholar in Galactic and Extragalactic Astrophysics, integrating the team of the UNIFAL-MG Astronomical Observatory (2016-2018), where I could work with science dissemination.',
                    highlights: ['Astrophysics', 'Scientific Initiation', 'Data Analysis']
                },
                {
                    period: '2019-2022',
                    title: 'Physics Teacher, State Department of Education of Minas Gerais',
                    description: 'I taught at SEE-MG (2019-2022) bringing scientific knowledge in theoretical, experimental and practical spheres, applying technical knowledge to the challenges that the period (2020-2022) brought, to three municipalities in Minas Gerais.',
                    highlights: ['Teaching', 'Educational Material Development', 'Remote Education']
                },
                {
                    period: '2021-2023',
                    title: 'Master\'s in Physics, UNIFEI',
                    description: 'During my Master\'s in Physics at UNIFEI (2021-2023), I had research in Active Galactic Nuclei: That\'s when I acquired a special passion for data.',
                    highlights: ['Research', 'Data Analysis', 'Active Galactic Nuclei']
                },
                {
                    period: '2023-Present',
                    title: 'Bachelor\'s in Computer Science, UNIFAL-MG',
                    description: 'In 2023 I made the career transition decision, becoming a student of the Bachelor\'s in Computer Science at UNIFAL-MG (2023-2029) and a gardener in my spare time.',
                    highlights: ['Career Transition', 'Computer Science', 'Software Development']
                },
                {
                    period: '2024-2025',
                    title: 'Innovation Ecosystem and Maker Educator, NidusTec/UNIFAL-MG',
                    description: 'I joined the team of the Technology-Based Business Incubator - NidusTec/UNIFAL-MG (2024-2025), connecting academia and market: There I developed a Maker educator side, developing Robotics projects and generalist and multidisciplinary prototyping in the spheres of teaching, research, extension, evolving to meet demands even of obsolescence of the institutional infrastructure through 3D and CNC modeling and manufacturing by the NidusLab Maker Laboratory. These challenges led me to develop another researcher side in Innovation, Entrepreneurship, Production Engineering and Industry 4.0, having developed in the period MVP prototypes for computer programs and products with market potential.',
                    highlights: ['Innovation', 'Entrepreneurship', 'Maker Education', '3D Modeling', 'CNC']
                }
            ]
        };
    }

    getAstrophysicsContent() {
        return [
            {
                title: 'Beyond the Telescope: Diving into the Frontier of Galactic Astrophysics at UNIFAL-MG',
                description: 'Looking at the sky through the eyepiece is the first step, but what really moves me is the mystery of Galactic Astrophysics and the structure of the Universe on a large scale. This image (recorded in late 2019) marks a significant moment in my life: a lecture I had the honor of delivering at the First Cycle of Seminars in Astronomy at UNIFAL-MG. It was the opportunity to transform years of observation into theoretical rigor and cutting-edge techniques. That night, we went far beyond dissemination. My presentation focused on the core developments of my research: Stellar Orbits in the Galaxy. I shared simulations of star motion from mass distribution models applied to the Gaussian law of Gravitation and numerical solutions for accelerations, velocities and stellar positions in the Milky Way and presented the evidence that led to postulates of the existence of something invisible: Dark Matter and Modified Gravitation.',
                links: [
                    { url: 'https://lnkd.in/deYnab4a', label: 'Research Paper' }
                ],
                tags: ['Dark Matter', 'Galactic Astrophysics', 'Research', 'Stellar Orbits'],
                status: 'Completed',
                date: '2019'
            },
            {
                title: 'Testing CCC+TL Cosmology with Observed Baryon Acoustic Oscillation Features',
                description: 'A recent study published in "The Astrophysical Journal" brings a new interpretation. "The forces of the universe, in fact, become weaker on average as it expands," explained Gupta. "This weakening makes it seem like there is a mysterious force driving the accelerated expansion of the universe (which is identified as dark energy). However, on the scales of galaxies and galactic clusters, the variation of these forces in their gravitationally bound spaces results in extra gravity (which is considered attributed to dark matter)"',
                links: [
                    { url: 'https://lnkd.in/dwsKCSbM', label: 'The Astrophysical Journal' }
                ],
                tags: ['Cosmology', 'Dark Energy', 'Dark Matter', 'Research'],
                status: 'Published',
                date: '2024'
            }
        ];
    }

    getObservatoryContent() {
        return [
            { imageUrl: './images/bullet-cluster-black-matter_upscayl.png', caption: 'Bullet Cluster showing dark matter distribution' },
            { imageUrl: './images/seminario.jpg', caption: 'Astronomy seminar presentation at UNIFAL-MG' },
            { imageUrl: './images/obs1.jpg', caption: 'Main telescope at UNIFAL-MG Observatory' },
            { imageUrl: './images/obs2.jpg', caption: 'Public observation night' },
            { imageUrl: './images/obs3.jpg', caption: 'Orion Nebula (M42) recording' },
            { imageUrl: './images/escolaOBS1.png', caption: 'Scientific outreach event for schools' },
            { imageUrl: './images/escolaOBS2.jpg', caption: 'Students observing with telescope' },
            { imageUrl: './images/escolaOBS3.jpg', caption: 'Astronomy presentation for students' },
            { imageUrl: './images/escolaOBS4.jpg', caption: 'Hands-on activity during outreach event' },
            { imageUrl: './images/obsLua.jpg', caption: 'Detailed Moon observation' },
            { imageUrl: './images/obsGalaxiaSombrero.jpg', caption: 'Sombrero Galaxy (M104) astrophotography' }
        ];
    }

    getCraamContent() {
        return [
            { imageUrl: './images/craamAntena.jpg', caption: 'Radio Polarimeter antenna at CRAAM' },
            { imageUrl: './images/craamControle.jpg', caption: 'Control room at CRAAM' },
            { imageUrl: './images/craamDomo.jpg', caption: 'Inside the CRAAM dome' },
            { imageUrl: './images/craamEscada.jpg', caption: 'Access to radio-heliograph instrumentation' }
        ];
    }

    getLnaTelescopeContent() {
        return [
            { imageUrl: './images/obs4.jpg', caption: 'LNA Observatory at sunset' },
            { imageUrl: './images/obs5.jpg', caption: 'Aerial view of National Astrophysics Laboratory (LNA)' }
        ];
    }

    getEducationContent() {
        return {
            timeline: [
                {
                    period: '2016-2018',
                    title: 'Teaching Assistant, Physics Department, UNIFAL-MG',
                    description: 'During my undergraduate studies, I served as a Teaching Assistant in the Physics Department at UNIFAL-MG, responsible for laboratory instruction, developing experimental protocols, and providing academic mentoring.',
                    highlights: ['Laboratory Instruction', 'Academic Support', 'Experimental Protocols']
                },
                {
                    period: '2017-2018',
                    title: 'Educational Material Developer, UNIFAL-MG Astronomical Observatory',
                    description: 'I led the creation of engaging astronomy education materials and played a key role in developing and coordinating public outreach programs and workshops, reaching over 500 students.',
                    highlights: ['Educational Materials', 'Public Outreach', 'Workshops']
                },
                {
                    period: '2019-2022',
                    title: 'Physics Teacher, State Department of Education of Minas Gerais',
                    description: 'I taught Physics in three municipalities, adapting scientific knowledge to diverse audiences and developing innovative teaching strategies including virtual labs and interactive online content during remote education.',
                    highlights: ['Teaching', 'Curriculum Adaptation', 'Innovative Strategies']
                }
            ]
        };
    }

    getInnovationContent() {
        return [
            {
                title: 'NidusTec - Technology-Based Business Incubator',
                description: 'As part of the NidusTec team, I acted as a bridge between academic research and the market, helping to transform innovative projects into successful startups. My role involved technical feasibility analysis of projects, product development mentoring, and the search for emerging technologies with market potential.',
                links: [
                    { url: 'https://jornal.unifal-mg.edu.br/capacitacoes-promovidas-pela-agencia-de-inovacao-e-a-incubadora-de-empresas-no-mes-de-junho-estimulam-a-cultura-empreendedora-e-a-inovacao-tecnologica-junto-a-comunidade/', label: 'UNIFAL-MG News: June Training' },
                    { url: 'https://anprotec.org.br/site/2024/12/premio-nacional-anprotec-de-empreendedorismo-inovador-2024-revela-vencedores-em-sao-jose-dos-campos/', label: 'ANPROTEC Award News' }
                ],
                tags: ['Innovation', 'Entrepreneurship', 'Technology', 'Startups'],
                status: 'Completed',
                date: '2021-2023'
            },
            {
                title: 'Development of a Data Analysis System for Precision Agriculture',
                description: 'This project, developed in partnership with a NidusTec startup, created a platform for analyzing drone and sensor data in the field. The system uses machine learning algorithms to optimize the use of resources, such as water and fertilizers, increasing productivity and sustainability in agribusiness.',
                tags: ['Machine Learning', 'Precision Agriculture', 'Python', 'Innovation'],
                status: 'Completed',
                date: '2022'
            }
        ];
    }

    getDeepLearningProjectsContent() {
        return [
            {
                title: 'Brain Tumor Segmentation in Magnetic Resonance Images',
                description: 'This project used a U-Net architecture for automatic segmentation of brain tumors in magnetic resonance images. The goal was to create a tool to support medical diagnosis, increasing the accuracy and speed of analysis. The model was trained on a large dataset of medical images and achieved high performance.',
                tags: ['Deep Learning', 'Computer Vision', 'Python', 'TensorFlow', 'Medicine'],
                status: 'Completed',
                date: '2023'
            },
            {
                title: 'Morphological Classification of Galaxies with CNNs',
                description: 'Using data from the Galaxy Zoo project, I developed a convolutional neural network to classify galaxies based on their morphology (spiral, elliptical, etc.). The project demonstrated how deep learning can automate classification tasks in large astronomical surveys, accelerating scientific research.',
                tags: ['Deep Learning', 'Astrophysics', 'Python', 'PyTorch', 'Data Science'],
                status: 'Completed',
                date: '2022'
            }
        ];
    }

    getSkillsContent() {
        return [
            {
                category: 'Programming Languages',
                skills: [
                    { name: 'Python', proficiency: 95, description: 'Data analysis, ML/DL, automation, web.' },
                    { name: 'JavaScript / TypeScript', proficiency: 85, description: 'Front-end and back-end web development (Node.js).' },
                    { name: 'C/C++', proficiency: 70, description: 'Systems programming and high-performance computing.' },
                    { name: 'SQL', proficiency: 80, description: 'Manipulation and querying of relational databases.' }
                ]
            },
            {
                category: 'Data Science & Machine Learning',
                skills: [
                    { name: 'TensorFlow / PyTorch', proficiency: 90, description: 'Deep Learning frameworks for computer vision and NLP.' },
                    { name: 'Scikit-learn', proficiency: 95, description: 'Classical Machine Learning models.' },
                    { name: 'Pandas / NumPy / Matplotlib', proficiency: 98, description: 'Essential tools for data analysis and visualization.' },
                    { name: 'Image Processing (OpenCV)', proficiency: 85, description: 'Image analysis and manipulation for scientific applications.' }
                ]
            },
            {
                category: 'Tools and Technologies',
                skills: [
                    { name: 'Git / GitHub', proficiency: 95, description: 'Code versioning and collaboration.' },
                    { name: 'Docker', proficiency: 75, description: 'Application containerization for portability and deployment.' },
                    { name: 'Linux / Shell Scripting', proficiency: 85, description: 'System administration and task automation.' },
                    { name: 'Cloud Computing (AWS/GCP)', proficiency: 60, description: 'Basic knowledge of cloud services for computing and storage.' }
                ]
            }
        ];
    }

    getAllSections() {
        return [...this.sections].sort((a, b) => a.metadata.order - b.metadata.order);
    }
}

// ===== VIEW MANAGER - RESPONSIBLE FOR RENDERING =====
class ViewManager {
    constructor(sectionsContainer) {
        if (!sectionsContainer) {
            throw new Error("ViewManager: Sections container is required.");
        }
        this.container = sectionsContainer;
        this.renderMap = {
            timeline: this.renderTimeline,
            cards: this.renderCards,
            skills: this.renderSkills,
            gallery: this.renderGallery,
        };
    }

    renderSection(section) {
        const sectionElement = document.createElement('section');
        sectionElement.id = section.id;
        sectionElement.className = `section section--${section.type}`;

        const renderer = this.renderMap[section.type];
        if (typeof renderer !== 'function') {
            console.warn(`ViewManager: No rendering method for type "${section.type}".`);
            return;
        }

        const sectionContent = renderer.call(this, section.content);
        
        sectionElement.innerHTML = `
            <div class="section-container">
                <header class="section-header">
                    <h2 class="section-title">${section.title}</h2>
                    <p class="section-subtitle">${section.subtitle}</p>
                </header>
                ${sectionContent}
            </div>
        `;

        this.container.appendChild(sectionElement);
    }

    renderTimeline(content) {
        const timelineItems = content.timeline.map(item => `
            <div class="timeline-item">
                <div class="timeline-period">${item.period}</div>
                <div class="timeline-content">
                    <h3 class="timeline-title">${item.title}</h3>
                    <p class="timeline-description">${item.description}</p>
                    <div class="highlights-list">
                        ${item.highlights.map(h => `<span class="highlight-tag">${h}</span>`).join('')}
                    </div>
                </div>
            </div>
        `).join('');

        return `<div class="timeline">${timelineItems}</div>`;
    }

    renderCards(content) {
        const cards = content.map(item => `
            <div class="card">
                <h3 class="card-title">${item.title}</h3>
                <p class="card-description">${item.description}</p>
                ${item.links && item.links.length > 0 ? `
                    <div class="card-links">
                        ${item.links.map(link => `<a href="${link.url}" target="_blank" rel="noopener">${link.label}</a>`).join('')}
                    </div>
                ` : ''}
                <div class="tags-container">
                    ${item.tags.map(t => `<span class="tag">${t}</span>`).join('')}
                </div>
                <div class="card-meta">
                    <span class="card-date">${item.date}</span>
                    <span class="card-status">${item.status}</span>
                </div>
            </div>
        `).join('');

        return `<div class="cards-grid">${cards}</div>`;
    }

    renderSkills(content) {
        const categories = content.map(category => `
            <div class="skill-category">
                <h3 class="category-title">${category.category}</h3>
                <div class="skills-list">
                    ${category.skills.map(skill => `
                        <div class="skill-item">
                            <div class="skill-header">
                                <span class="skill-name">${skill.name}</span>
                                <span class="skill-proficiency">${skill.proficiency}%</span>
                            </div>
                            <div class="skill-bar">
                                <div class="skill-progress" style="width: ${skill.proficiency}%;"></div>
                            </div>
                            <p class="skill-description">${skill.description}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
        
        return `<div class="skills-categories">${categories}</div>`;
    }
    
    renderGallery(content) {
        const items = content.map(item => `
            <div class="gallery-item">
                <img src="${item.imageUrl}" alt="${item.caption}" class="gallery-image" loading="lazy">
                <div class="gallery-caption">${item.caption}</div>
            </div>
        `).join('');

        return `<div class="gallery-grid">${items}</div>`;
    }
}

// ===== RENDER ENGINE - MAIN ORCHESTRATOR =====
class RenderEngine {
    constructor() {
        this.contentModel = new ContentModel();
        
        const sectionsContainer = document.getElementById('sections-container');
        if (!sectionsContainer) {
            throw new Error("RenderEngine: 'sections-container' element not found in DOM.");
        }
        this.viewManager = new ViewManager(sectionsContainer);
        
        this.navContainer = document.getElementById('nav-list');
    }

    async initialize() {
        await this.contentModel.initializeContentModel();
        this.renderAll();
        this.setupEventListeners();
        this.hideLoadingOverlay();
    }

    renderAll() {
        this.renderNavigation();
        const sections = this.contentModel.getAllSections();
        sections.forEach(section => {
            if (section.metadata.visible) {
                this.viewManager.renderSection(section);
            }
        });
    }

    renderNavigation() {
        if (!this.navContainer) return;
        
        const sections = this.contentModel.getAllSections();
        const navLinks = sections
            .filter(s => s.metadata.visible)
            .map(section => `
                <li>
                    <a href="#${section.id}" class="nav-link" data-nav-id="${section.id}">
                        ${section.title}
                    </a>
                </li>
            `);
        this.navContainer.innerHTML = navLinks.join('');
    }

    setupEventListeners() {
        window.addEventListener('scroll', () => this.updateActiveNavLink());
    }

    updateActiveNavLink() {
        if (!this.navContainer) return;

        const scrollPosition = window.scrollY + 150; // Offset
        const sections = this.contentModel.getAllSections();
        
        let activeSectionId = null;

        for (const section of sections) {
            const sectionElement = document.getElementById(section.id);
            if (sectionElement && scrollPosition >= sectionElement.offsetTop) {
                activeSectionId = section.id;
            }
        }
        
        const links = this.navContainer.querySelectorAll('.nav-link');
        links.forEach(link => {
            link.classList.remove('active');
            if (link.dataset.navId === activeSectionId) {
                link.classList.add('active');
            }
        });
    }

    hideLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.opacity = '0';
            setTimeout(() => {
                overlay.style.display = 'none';
            }, 500);
        }
    }
}

// ===== APPLICATION INITIALIZATION =====
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const app = new RenderEngine();
        await app.initialize();
        
        // For debugging
        window.app = app;
        
        console.log('Portfolio loaded successfully!');
    } catch (error) {
        console.error('Error initializing application:', error);
        document.getElementById('loading-overlay').innerHTML = `
            <div style="text-align: center; color: white;">
                <h2>Loading error</h2>
                <p>Please reload the page.</p>
                <button onclick="window.location.reload()" style="padding: 10px 20px; margin-top: 20px;">
                    Reload
                </button>
            </div>
        `;
    }
});