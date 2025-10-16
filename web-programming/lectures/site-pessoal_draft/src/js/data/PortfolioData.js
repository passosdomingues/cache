/**
 * @file PortfolioData.js
 * @author Rafael Passos Domingues
 * @brief Centralized data source with ORIGINAL working structure
 */

export const PORTFOLIO_DATA = {
    user: {
        name: "Rafael Passos Domingues",
        title: "Physicist | Computer Scientist | Tech Innovator"
    },
    sections: [
        {
            id: 'about',
            title: 'About Me',
            subtitle: 'My academic and professional journey',
            type: 'timeline',
            metadata: { order: 1, visible: true },
            content: {
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
                        description: 'I joined the team of the Technology-Based Business Incubator - NidusTec/UNIFAL-MG (2024-2025), connecting academia and market...',
                        highlights: ['Innovation', 'Entrepreneurship', 'Maker Education', '3D Modeling', 'CNC']
                    }
                ]
            }
        },
        {
            id: 'lna-zeiss-telescope',
            title: 'LNA Zeiss Telescope Experience',
            subtitle: 'Operating a classic instrument at Pico dos Dias Observatory',
            type: 'gallery',
            metadata: { order: 5, visible: true },
            content: [
                { imageUrl: './images/obs4.jpg', caption: 'LNA Observatory at sunset' },
                { imageUrl: './images/obs5.jpg', caption: 'Aerial view of National Astrophysics Laboratory (LNA)' }
            ]
        },
        {
            id: 'astrophysics-research',
            title: 'Astrophysics Research',
            subtitle: 'Work in galactic and extragalactic astrophysics',
            type: 'cards',
            metadata: { order: 2, visible: true },
            content: [
                {
                    title: 'Beyond the Telescope: Diving into the Frontier of Galactic Astrophysics at UNIFAL-MG',
                    description: 'Looking at the sky through the eyepiece is the first step, but what really moves me is the mystery of Galactic Astrophysics...',
                    links: [
                        { url: 'https://sciforum.net/paper/view/5868', label: 'Research Paper' }
                    ],
                    tags: ['Dark Matter', 'Galactic Astrophysics', 'Research', 'Stellar Orbits'],
                    status: 'Completed',
                    date: '2019'
                },
                {
                    title: 'Testing CCC+TL Cosmology with Observed Baryon Acoustic Oscillation Features',
                    description: 'A recent study published in "The Astrophysical Journal" brings a new interpretation...',
                    links: [
                        { url: 'https://lnkd.in/dwsKCSbM', label: 'The Astrophysical Journal' }
                    ],
                    tags: ['Cosmology', 'Dark Energy', 'Dark Matter', 'Research'],
                    status: 'Published',
                    date: '2024'
                }
            ]
        },
        {
            id: 'astronomical-observatory',
            title: 'Astronomical Observatory',
            subtitle: 'Scientific outreach and research at UNIFAL-MG',
            type: 'gallery',
            metadata: { order: 3, visible: true },
            content: [
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
            ]
        },
        {
            id: 'craam-visit',
            title: 'CRAAM Visit',
            subtitle: 'Mackenzie Center for Radio Astronomy and Astrophysics',
            type: 'gallery',
            metadata: { order: 4, visible: true },
            content: [
                { imageUrl: './images/craamAntena.jpg', caption: 'Radio Polarimeter antenna at CRAAM' },
                { imageUrl: './images/craamControle.jpg', caption: 'Control room at CRAAM' },
                { imageUrl: './images/craamDomo.jpg', caption: 'Inside the CRAAM dome' },
                { imageUrl: './images/craamEscada.jpg', caption: 'Access to radio-heliograph instrumentation' }
            ]
        },
        {
            id: 'education-experience',
            title: 'Education Experience',
            subtitle: 'Teaching and educational material development',
            type: 'timeline',
            metadata: { order: 6, visible: true },
            content: {
                timeline: [
                    {
                        period: '2016-2018',
                        title: 'Teaching Assistant, Physics Department, UNIFAL-MG',
                        description: 'During my undergraduate studies, I served as a Teaching Assistant in the Physics Department at UNIFAL-MG...',
                        highlights: ['Laboratory Instruction', 'Academic Support', 'Experimental Protocols']
                    },
                    {
                        period: '2017-2018',
                        title: 'Educational Material Developer, UNIFAL-MG Astronomical Observatory',
                        description: 'I led the creation of engaging astronomy education materials and played a key role in developing and coordinating public outreach programs...',
                        highlights: ['Educational Materials', 'Public Outreach', 'Workshops']
                    },
                    {
                        period: '2019-2022',
                        title: 'Physics Teacher, State Department of Education of Minas Gerais',
                        description: 'I taught Physics in three municipalities, adapting scientific knowledge to diverse audiences...',
                        highlights: ['Teaching', 'Curriculum Adaptation', 'Innovative Strategies']
                    }
                ]
            }
        },
        {
            id: 'innovation-entrepreneurship',
            title: 'Innovation and Entrepreneurship',
            subtitle: 'NidusTec and innovation ecosystem',
            type: 'gallery',
            metadata: { order: 7, visible: true },
            content: [
                {
                    imageUrl: './images/nidus.jpg',
                    caption: 'NidusTec - Technology-Based Business Incubator',
                    description: 'As part of the NidusTec team, I acted as a bridge between academic research and the market...',
                    links: [
                        { url: 'https://www.unifal-mg.edu.br/i9unifal/maratona-de-ideias-senac-alfenas-i9-em-parceria-com-o-unis-cefet-varginha-e-cesullab/', label: 'Maratona de Ideias Senac Alfenas' },
                        { url: 'https://jornal.unifal-mg.edu.br/comunidade-academica-do-campus-varginha-adquire-habilidades-praticas-e-teoricas-na-area-da-cultura-maker-em-capacitacao-promovida-no-niduslab/', label: 'Capacitação em Cultura Maker - Campus Varginha' },
                        { url: 'https://jornal.unifal-mg.edu.br/agencia-de-inovacao-de-empreendedorismo-da-unifal-mg-realiza-segunda-oficina-de-capacitacao-para-corte-a-laser-nos-laboratorios-maker-dos-campi-alfenas-e-pocos-de-caldas/', label: 'Oficina de Corte a Laser - Alfenas e Poços de Caldas' },
                        { url: 'https://jornal.unifal-mg.edu.br/calouros-vivenciam-inovacao-em-visitas-ao-laboratorio-maker-na-unifal-mg/', label: 'Calouros Visitam Laboratório Maker' },
                        { url: 'https://jornal.unifal-mg.edu.br/agencia-de-inovacao-e-empreendedorismo-da-unifal-mg-promove-visita-tecnica-no-espaco-maker-a-calouros-do-bacharelado-em-quimica-da-instituicao/', label: 'Visita Técnica ao Espaço Maker - Calouros de Química' },
                        { url: 'https://jornal.unifal-mg.edu.br/capacitacoes-promovidas-pela-agencia-de-inovacao-e-incubadora-de-empresas-de-base-tecnologica-impulsionam-a-criatividade-e-o-empreendedorismo/', label: 'Capacitações Impulsionam Criatividade e Empreendedorismo' },
                        { url: 'https://jornal.unifal-mg.edu.br/capacitacoes-promovidas-pela-agencia-de-inovacao-e-a-incubadora-de-empresas-no-mes-de-junho-estimulam-a-cultura-empreendedora-e-a-inovacao-tecnologica-junto-a-comunidade/', label: 'Capacitações de Junho - Cultura Empreendedora' },
                        { url: 'https://anprotec.org.br/site/2024/12/premio-nacional-anprotec-de-empreendedorismo-inovador-2024-revela-vencedores-em-sao-jose-dos-campos/', label: 'ANPROTEC Award News' }
                    ],
                    tags: ['Innovation', 'Entrepreneurship', 'Technology', 'Startups'],
                    status: 'Completed',
                    date: '2021-2023'
                },
                { imageUrl: './images/nidus2.jpg', caption: 'NidusTec Activities' },
                { imageUrl: './images/nidus3.jpg', caption: 'Innovation Workshop' },
                { imageUrl: './images/nidus4.jpg', caption: 'Maker Space Equipment' },
                { imageUrl: './images/nidus5.jpg', caption: 'Team Collaboration' },
                { imageUrl: './images/nidus6.jpg', caption: 'Project Development' },
                { imageUrl: './images/nidus7.jpg', caption: 'Technology Prototyping' },
                { imageUrl: './images/nidus8.jpg', caption: 'Entrepreneurship Training' },
                { imageUrl: './images/nidus9.jpg', caption: 'Innovation Ecosystem' },
                { imageUrl: './images/nidus10.jpg', caption: 'Startup Incubation' },
                { imageUrl: './images/nidus11.jpg', caption: 'Maker Culture' }
            ]
        },
        {
            id: 'deep-learning-projects',
            title: 'Deep Learning Projects',
            subtitle: 'Applying ML/DL to medical imaging and astrophysics',
            type: 'cards',
            metadata: { order: 8, visible: true },
            content: [
                {
                    title: 'WebApp Showcase - Browser-Based Utilities and Prototypes',
                    description: 'A curated collection of lightweight web applications focused on privacy and simplicity. Each webapp operates entirely client-side, storing data only in the user\'s browser. The project includes completed utilities for personal and professional workflows, experimental prototypes for potential solutions, and tools with WhatsApp export functionality. This evolving repository represents my approach to solving everyday problems through minimal, accessible web technologies.',
                    links: [
                        { url: 'https://passosdomingues.github.io/webappshowcase/site/main.html', label: 'WebApp Showcase - Live Demo' }
                    ],
                    tags: ['Web Development', 'JavaScript', 'HTML5', 'CSS3', 'Prototyping', 'Utilities', 'Client-Side'],
                    status: 'Ongoing',
                    date: '2023-2024'
                },
                {
                    title: 'Brain Tumor Segmentation in Magnetic Resonance Images',
                    description: 'This project used a U-Net architecture for automatic segmentation of brain tumors in magnetic resonance images...',
                    links: [
                        { url: 'https://youtu.be/Sdd98HDahPA', label: 'Machine Learning Fundamentals: Dimensionality Reduction - A Physical and Mathematical Perspective' },
                        { url: 'https://youtu.be/11ahe2JBN5c', label: 'Building a Complete Machine Learning Pipeline for Breast Cancer Diagnosis | End-to-End Project' },
                        { url: 'https://youtu.be/4R1Z92z-zNs', label: 'Materializing Pixels: From Photons to Matter with CO₂ Laser CNC and Computational Vision Horizons' }
                    ],
                    tags: ['Deep Learning', 'Computer Vision', 'Python', 'TensorFlow', 'Medicine'],
                    status: 'Completed',
                    date: '2023'
                },
                {
                    title: 'Morphological Classification of Galaxies with CNNs',
                    description: 'Using data from the Galaxy Zoo project, I developed a convolutional neural network to classify galaxies based on their morphology...',
                    links: [
                        { url: 'https://youtu.be/naBvOJhUAH4', label: 'Are We Living in a Simulation? How M/M/1 Queues Could Reveal the Universe (Stochastic Experiment)' }
                    ],
                    tags: ['Deep Learning', 'Astrophysics', 'Python', 'PyTorch', 'Data Science'],
                    status: 'Completed',
                    date: '2022'
                }
            ]
        },
        {
            id: 'skills',
            title: 'Skills and Competencies',
            subtitle: 'From data to value: A journey through technology and education',
            type: 'skills',
            metadata: { order: 9, visible: true },
            content: [
                {
                    category: 'Programming Languages & Data Transformation',
                    skills: [
                        { name: 'Python', proficiency: 95, description: 'Started with scientific simulations and data analysis in astrophysics, now focused on transforming raw data into actionable insights and value.' },
                        { name: 'Java', proficiency: 85, description: 'Currently developing enterprise solutions for Industry 5.0 and innovation management, applying MVC principles and modern frameworks.' },
                        { name: 'JavaScript / TypeScript', proficiency: 85, description: 'Building practical web applications and this portfolio site, learning MVC architecture through hands-on experience.' },
                        { name: 'C/C++', proficiency: 70, description: 'Foundation in astronomical instrumentation and robotics, understanding low-level system programming.' },
                        { name: 'SQL', proficiency: 80, description: 'Currently deepening knowledge with Java integration, JDBC, JPA, and database design patterns.' }
                    ]
                },
                {
                    category: 'Data Science & Machine Learning',
                    skills: [
                        { name: 'TensorFlow / PyTorch', proficiency: 90, description: 'Applied to medical imaging and astrophysics, focusing on practical problem-solving rather than theoretical perfection.' },
                        { name: 'Neo4j', proficiency: 88, description: 'Specializing in graph databases for complex relationship mapping in innovation ecosystems and manufacturing systems.' },
                        { name: 'Scikit-learn', proficiency: 95, description: 'Reliable companion for classical ML models, from academic research to industrial applications.' },
                        { name: 'Pandas / NumPy / Matplotlib', proficiency: 98, description: 'Essential toolkit honed through years of exploratory data analysis and astronomical data reduction.' },
                        { name: 'Image Processing (OpenCV)', proficiency: 85, description: 'Bridging scientific applications with practical computer vision solutions.' }
                    ]
                },
                {
                    category: 'Tools and Technologies',
                    skills: [
                        { name: 'Git / GitHub', proficiency: 95, description: 'Essential for collaborative development and learning through practical projects like this portfolio.' },
                        { name: 'Docker', proficiency: 75, description: 'Simplifying deployment and ensuring consistency across development environments.' },
                        { name: 'Linux / Shell Scripting', proficiency: 85, description: 'Daily driver for development, from simple automation to complex system administration.' },
                        { name: 'Vite & GitHub Actions', proficiency: 80, description: 'Modern tools embraced while building this portfolio, representing ongoing learning journey.' },
                        { name: 'Cloud Computing (AWS/GCP)', proficiency: 60, description: 'Exploring cloud solutions for scalable applications and data processing.' }
                    ]
                },
                {
                    category: 'Educational Technology & Practical Solutions',
                    skills: [
                        { name: 'LaTeX', proficiency: 90, description: 'Extensive experience in academic documentation and teaching materials during teaching career.' },
                        { name: 'HTML/CSS', proficiency: 88, description: 'Evolved from simple WordPress sites to complex MVC-based applications like this portfolio.' },
                        { name: 'WordPress', proficiency: 75, description: 'Practical experience developing school platforms during pandemic, focusing on accessibility.' },
                        { name: 'IRAF & Astronomical Data Reduction', proficiency: 80, description: 'Specialized skills in astronomical data processing from research background.' },
                        { name: 'Teaching Platform Development', proficiency: 85, description: 'Proven ability to create educational solutions under constraints, serving 640+ students.' }
                    ]
                },
                {
                    category: 'Educational Impact Projects',
                    skills: [
                        { 
                            name: 'Integrated Physics Teaching Platform - Pandemic Response', 
                            proficiency: 100, 
                            description: 'During COVID-19, transformed limited resources into a comprehensive remote learning platform for 640+ students, maintaining educational continuity through synchronous and asynchronous resources.',
                            links: [
                                { url: 'https://sites.google.com/view/pandefisica/', label: 'Physics Teaching Platform' }
                            ]
                        },
                        { 
                            name: 'Digital School Management Platform', 
                            proficiency: 100, 
                            description: 'Developed a unified communication platform during pandemic crisis, centralizing essential information and pedagogical content. Recognized by State Education Department as best practice.',
                            links: [
                                { url: 'https://sites.google.com/view/piccinini-virtual/p%C3%A1gina-inicial', label: 'School Management Platform' }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
};