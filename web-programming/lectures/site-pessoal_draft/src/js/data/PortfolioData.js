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
                        { url: 'https://lnkd.in/deYnab4a', label: 'Research Paper' }
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
            type: 'cards',
            metadata: { order: 7, visible: true },
            content: [
                {
                    title: 'NidusTec - Technology-Based Business Incubator',
                    description: 'As part of the NidusTec team, I acted as a bridge between academic research and the market...',
                    links: [
                        { url: 'https://jornal.unifal-mg.edu.br/capacitacoes-promovidas-pela-agencia-de-inovacao-e-a-incubadora-de-empresas-no-mes-de-junho-estimulam-a-cultura-empreendedora-e-a-inovacao-tecnologica-junto-a-comunidade/', label: 'UNIFAL-MG News: June Training' },
                        { url: 'https://anprotec.org.br/site/2024/12/premio-nacional-anprotec-de-empreendedorismo-inovador-2024-revela-vencedores-em-sao-jose-dos-campos/', label: 'ANPROTEC Award News' }
                    ],
                    tags: ['Innovation', 'Entrepreneurship', 'Technology', 'Startups'],
                    status: 'Completed',
                    date: '2021-2023'
                }
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
                    title: 'Brain Tumor Segmentation in Magnetic Resonance Images',
                    description: 'This project used a U-Net architecture for automatic segmentation of brain tumors in magnetic resonance images...',
                    tags: ['Deep Learning', 'Computer Vision', 'Python', 'TensorFlow', 'Medicine'],
                    status: 'Completed',
                    date: '2023'
                },
                {
                    title: 'Morphological Classification of Galaxies with CNNs',
                    description: 'Using data from the Galaxy Zoo project, I developed a convolutional neural network to classify galaxies based on their morphology...',
                    tags: ['Deep Learning', 'Astrophysics', 'Python', 'PyTorch', 'Data Science'],
                    status: 'Completed',
                    date: '2022'
                }
            ]
        },
        {
            id: 'skills',
            title: 'Skills and Competencies',
            subtitle: 'Knowledge areas and technologies',
            type: 'skills',
            metadata: { order: 9, visible: true },
            content: [
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
            ]
        }
    ]
};