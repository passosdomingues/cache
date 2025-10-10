/**
 * @file Controlador de navegação
 * @brief Gerencia navegação e scroll
 */

class NavigationController {
    constructor() {
        this.currentSection = '';
        this.init();
    }

    /**
     * @brief Inicializa o controlador
     */
    init() {
        this.setupScrollHandler();
        this.setupHashChangeHandler();
    }

    /**
     * @brief Navega para uma seção
     * @param {string} sectionId - ID da seção
     */
    navigateToSection(sectionId) {
        this.scrollToSection(sectionId);
        this.updateURLHash(sectionId);
    }

    /**
     * @brief Scroll suave para seção
     * @param {string} sectionId - ID da seção
     */
    scrollToSection(sectionId) {
        const element = document.getElementById(sectionId);
        if (element) {
            const headerHeight = document.querySelector('header').offsetHeight;
            const targetPosition = element.offsetTop - headerHeight;

            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });

            this.currentSection = sectionId;
        }
    }

    /**
     * @brief Atualiza hash na URL
     * @param {string} sectionId - ID da seção
     */
    updateURLHash(sectionId) {
        window.history.pushState(null, null, `#${sectionId}`);
    }

    /**
     * @brief Configura handler de scroll
     */
    setupScrollHandler() {
        let ticking = false;

        const updateActiveSection = () => {
            const sections = document.querySelectorAll('.section');
            const scrollPosition = window.scrollY + 100;

            sections.forEach(section => {
                const sectionTop = section.offsetTop;
                const sectionHeight = section.offsetHeight;
                
                if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                    this.currentSection = section.id;
                    // Notificar views sobre mudança de seção
                    this.dispatchEvent('sectionChange', { sectionId: section.id });
                }
            });

            ticking = false;
        };

        window.addEventListener('scroll', () => {
            if (!ticking) {
                requestAnimationFrame(updateActiveSection);
                ticking = true;
            }
        });
    }

    /**
     * @brief Configura handler de mudança de hash
     */
    setupHashChangeHandler() {
        window.addEventListener('hashchange', () => {
            const sectionId = window.location.hash.substring(1);
            if (sectionId) {
                this.scrollToSection(sectionId);
            }
        });
    }

    /**
     * @brief Dispara evento personalizado
     * @param {string} eventType - Tipo de evento
     * @param {Object} detail - Detalhes do evento
     */
    dispatchEvent(eventType, detail) {
        const event = new CustomEvent(eventType, { detail });
        document.dispatchEvent(event);
    }
}

export default NavigationController;