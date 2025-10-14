import eventBus from '../core/EventBus.js';

/**
 * @brief Navigation view
 * @description Renders and manages navigation UI
 */
export class NavigationView {
    constructor(config = {}) {
        this.container = config.container;
        this.eventBus = config.eventBus || eventBus;
        
        this.isMobileMenuOpen = false;
        
        this.handleNavClick = this.handleNavClick.bind(this);
        this.setupEventListeners();
    }

    /**
     * @brief Set up event listeners
     */
    setupEventListeners() {
        this.container.addEventListener('click', this.handleNavClick);
        
        // Handle window resize for mobile menu
        window.addEventListener('resize', this.handleResize.bind(this));
    }

    /**
     * @brief Handle navigation click events
     * @param {Event} event - Click event
     */
    handleNavClick(event) {
        const link = event.target.closest('.nav-link');
        if (!link) return;

        event.preventDefault();
        
        const sectionId = link.getAttribute('href')?.replace('#', '');
        if (sectionId) {
            this.eventBus.publish('navigation:clicked', { sectionId });
            
            // Close mobile menu if open
            if (this.isMobileMenuOpen) {
                this.toggleMobileMenu();
            }
        }
    }

    /**
     * @brief Handle window resize
     */
    handleResize() {
        // Close mobile menu on large screens
        if (window.innerWidth > 768 && this.isMobileMenuOpen) {
            this.toggleMobileMenu(false);
        }
    }

    /**
     * @brief Render navigation menu
     * @param {Array} sections - Array of section objects
     */
    renderNavigation(sections) {
        if (!this.container) return;

        const visibleSections = sections.filter(section => section.metadata.visible);
        
        const navHTML = visibleSections.map(section => `
            <li class="nav-item">
                <a href="#${section.id}" 
                   class="nav-link" 
                   data-section-id="${section.id}">
                    ${this.escapeHtml(section.title)}
                </a>
            </li>
        `).join('');

        this.container.innerHTML = navHTML;
        
        this.eventBus.publish('navigation:view:rendered', { sections: visibleSections });
    }

    /**
     * @brief Set active section in navigation
     * @param {string} sectionId - ID of the active section
     */
    setActiveSection(sectionId) {
        // Remove active class from all links
        this.container.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Add active class to current section link
        const activeLink = this.container.querySelector(`[data-section-id="${sectionId}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }
    }

    /**
     * @brief Toggle mobile menu
     * @param {boolean} [force] - Force open/close state
     */
    toggleMobileMenu(force) {
        this.isMobileMenuOpen = force !== undefined ? force : !this.isMobileMenuOpen;
        
        const navContainer = this.container.closest('.main-navigation-container');
        if (navContainer) {
            navContainer.classList.toggle('nav-mobile-open', this.isMobileMenuOpen);
        }
        
        this.eventBus.publish('navigation:mobile:toggled', { isOpen: this.isMobileMenuOpen });
    }

    /**
     * @brief Update navigation item
     * @param {string} sectionId - Section identifier
     * @param {Object} updates - Update data
     */
    updateNavigationItem(sectionId, updates) {
        const navItem = this.container.querySelector(`[data-section-id="${sectionId}"]`);
        if (navItem && updates.title) {
            navItem.textContent = updates.title;
        }
    }

    /**
     * @brief Escape HTML to prevent XSS
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        if (!text) return '';
        
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * @brief Destroy navigation view
     */
    destroy() {
        this.container.removeEventListener('click', this.handleNavClick);
        window.removeEventListener('resize', this.handleResize);
        
        console.info('NavigationView: Destroyed');
    }
}