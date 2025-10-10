/**
 * @brief Navigation view component
 * @description Handles main navigation rendering and interactive behavior
 */

/**
 * @brief Navigation configuration data
 * @constant
 * @type {Array}
 */
const navigationConfig = [
    {
        path: '/',
        label: 'Home',
        icon: 'home',
        ariaLabel: 'Go to home page'
    },
    {
        path: '/about',
        label: 'About',
        icon: 'user',
        ariaLabel: 'Learn more about me'
    },
    {
        path: '/projects',
        label: 'Projects',
        icon: 'code',
        ariaLabel: 'View my projects'
    },
    {
        path: '/research',
        label: 'Research',
        icon: 'microscope',
        ariaLabel: 'Explore my research work'
    },
    {
        path: '/contact',
        label: 'Contact',
        icon: 'envelope',
        ariaLabel: 'Get in touch with me'
    }
];

/**
 * @brief Renders the navigation component
 * @function render
 * @param {Object} data - Navigation data
 * @returns {string} HTML string of the navigation
 */
export const render = (data = {}) => {
    const { currentPath = '/', isMobileMenuOpen = false } = data;
    
    return `
        <nav class="main-navigation" role="navigation" aria-label="Main navigation">
            <div class="nav-container">
                <!-- Logo/Brand -->
                <div class="nav-brand">
                    <a href="/" class="brand-link" aria-label="Rafael Passos Domingues - Home">
                        <span class="brand-text">Rafael Passos Domingues</span>
                    </a>
                </div>

                <!-- Desktop Navigation -->
                <ul class="nav-menu desktop-menu" role="menubar">
                    ${navigationConfig.map(item => `
                        <li class="nav-item" role="none">
                            <a 
                                href="${item.path}" 
                                class="nav-link ${currentPath === item.path ? 'nav-link--active' : ''}"
                                role="menuitem"
                                aria-label="${item.ariaLabel}"
                                ${currentPath === item.path ? 'aria-current="page"' : ''}
                            >
                                <i class="fas fa-${item.icon}" aria-hidden="true"></i>
                                <span class="nav-link-text">${item.label}</span>
                            </a>
                        </li>
                    `).join('')}
                </ul>

                <!-- Mobile Menu Toggle -->
                <button 
                    class="mobile-menu-toggle"
                    aria-label="Toggle mobile menu"
                    aria-expanded="${isMobileMenuOpen}"
                    aria-controls="mobile-navigation-menu"
                >
                    <span class="hamburger-line"></span>
                    <span class="hamburger-line"></span>
                    <span class="hamburger-line"></span>
                </button>

                <!-- Mobile Navigation -->
                <div 
                    id="mobile-navigation-menu" 
                    class="mobile-menu ${isMobileMenuOpen ? 'mobile-menu--open' : ''}"
                    aria-hidden="${!isMobileMenuOpen}"
                >
                    <ul class="nav-menu mobile-nav-menu" role="menubar">
                        ${navigationConfig.map(item => `
                            <li class="nav-item" role="none">
                                <a 
                                    href="${item.path}" 
                                    class="nav-link ${currentPath === item.path ? 'nav-link--active' : ''}"
                                    role="menuitem"
                                    aria-label="${item.ariaLabel}"
                                    ${currentPath === item.path ? 'aria-current="page"' : ''}
                                >
                                    <i class="fas fa-${item.icon}" aria-hidden="true"></i>
                                    <span class="nav-link-text">${item.label}</span>
                                </a>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        </nav>
    `;
};

/**
 * @brief Initializes navigation interactivity
 * @function init
 * @param {Object} data - Initialization data
 * @returns {Promise<void>}
 */
export const init = async (data = {}) => {
    const navigationElement = document.querySelector('.main-navigation');
    if (!navigationElement) return;

    setupMobileMenuInteractions(navigationElement);
    setupKeyboardNavigation(navigationElement);
    setupScrollBehavior(navigationElement);
};

/**
 * @brief Sets up mobile menu interactions
 * @function setupMobileMenuInteractions
 * @param {HTMLElement} navigationElement - The navigation container element
 */
const setupMobileMenuInteractions = (navigationElement) => {
    const toggleButton = navigationElement.querySelector('.mobile-menu-toggle');
    const mobileMenu = navigationElement.querySelector('.mobile-menu');
    
    if (!toggleButton || !mobileMenu) return;

    const toggleMobileMenu = () => {
        const isOpen = mobileMenu.classList.contains('mobile-menu--open');
        
        // Toggle menu state
        mobileMenu.classList.toggle('mobile-menu--open');
        toggleButton.setAttribute('aria-expanded', (!isOpen).toString());
        mobileMenu.setAttribute('aria-hidden', isOpen.toString());
        
        // Prevent body scroll when menu is open
        document.body.style.overflow = isOpen ? '' : 'hidden';
    };

    // Toggle button click event
    toggleButton.addEventListener('click', toggleMobileMenu);

    // Close menu when clicking on a link
    const mobileLinks = mobileMenu.querySelectorAll('.nav-link');
    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('mobile-menu--open');
            toggleButton.setAttribute('aria-expanded', 'false');
            mobileMenu.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
        });
    });

    // Close menu when pressing Escape key
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && mobileMenu.classList.contains('mobile-menu--open')) {
            toggleMobileMenu();
        }
    });

    // Close menu when clicking outside
    document.addEventListener('click', (event) => {
        if (!navigationElement.contains(event.target) && mobileMenu.classList.contains('mobile-menu--open')) {
            toggleMobileMenu();
        }
    });
};

/**
 * @brief Sets up keyboard navigation for accessibility
 * @function setupKeyboardNavigation
 * @param {HTMLElement} navigationElement - The navigation container element
 */
const setupKeyboardNavigation = (navigationElement) => {
    const menuItems = navigationElement.querySelectorAll('.nav-link');
    
    menuItems.forEach((item, index) => {
        item.addEventListener('keydown', (event) => {
            switch (event.key) {
                case 'ArrowRight':
                case 'ArrowDown':
                    event.preventDefault();
                    focusNextMenuItem(menuItems, index);
                    break;
                    
                case 'ArrowLeft':
                case 'ArrowUp':
                    event.preventDefault();
                    focusPreviousMenuItem(menuItems, index);
                    break;
                    
                case 'Home':
                    event.preventDefault();
                    menuItems[0]?.focus();
                    break;
                    
                case 'End':
                    event.preventDefault();
                    menuItems[menuItems.length - 1]?.focus();
                    break;
            }
        });
    });
};

/**
 * @brief Focuses the next menu item in sequence
 * @function focusNextMenuItem
 * @param {NodeList} menuItems - Collection of menu item elements
 * @param {number} currentIndex - Index of the current menu item
 */
const focusNextMenuItem = (menuItems, currentIndex) => {
    const nextIndex = (currentIndex + 1) % menuItems.length;
    menuItems[nextIndex]?.focus();
};

/**
 * @brief Focuses the previous menu item in sequence
 * @function focusPreviousMenuItem
 * @param {NodeList} menuItems - Collection of menu item elements
 * @param {number} currentIndex - Index of the current menu item
 */
const focusPreviousMenuItem = (menuItems, currentIndex) => {
    const previousIndex = currentIndex > 0 ? currentIndex - 1 : menuItems.length - 1;
    menuItems[previousIndex]?.focus();
};

/**
 * @brief Sets up scroll behavior for navigation
 * @function setupScrollBehavior
 * @param {HTMLElement} navigationElement - The navigation container element
 */
const setupScrollBehavior = (navigationElement) => {
    let lastScrollY = window.scrollY;
    
    const handleScroll = () => {
        const currentScrollY = window.scrollY;
        const scrollDelta = currentScrollY - lastScrollY;
        
        if (scrollDelta > 5 && currentScrollY > 100) {
            // Scrolling down - hide navigation
            navigationElement.classList.add('nav--hidden');
        } else if (scrollDelta < -5) {
            // Scrolling up - show navigation
            navigationElement.classList.remove('nav--hidden');
        }
        
        // Add background when scrolled
        if (currentScrollY > 50) {
            navigationElement.classList.add('nav--scrolled');
        } else {
            navigationElement.classList.remove('nav--scrolled');
        }
        
        lastScrollY = currentScrollY;
    };
    
    // Throttle scroll events for performance
    let ticking = false;
    const throttledScrollHandler = () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                handleScroll();
                ticking = false;
            });
            ticking = true;
        }
    };
    
    window.addEventListener('scroll', throttledScrollHandler, { passive: true });
};

/**
 * @brief Updates navigation state based on current route
 * @function updateNavigationState
 * @param {string} currentPath - The current active path
 */
export const updateNavigationState = (currentPath) => {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const isActive = link.getAttribute('href') === currentPath;
        
        if (isActive) {
            link.classList.add('nav-link--active');
            link.setAttribute('aria-current', 'page');
        } else {
            link.classList.remove('nav-link--active');
            link.removeAttribute('aria-current');
        }
    });
};

export default {
    render,
    init,
    updateNavigationState
};