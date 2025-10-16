/**
 * @brief Main application entry point.
 * @description Initializes and coordinates all MVC components, including UI controls for theme and accessibility.
 */
import { App } from './core/App.js';
import { MainController } from './controllers/MainController.js';
import { NavigationController } from './controllers/NavigationController.js';
import { ContentModel } from './models/ContentModel.js';
import { UserModel } from './models/UserModel.js';
import { ThemeManager } from './services/ThemeManager.js';
import { AccessibilityManager } from './services/AccessibilityManager.js';
import { PerformanceMonitor } from './services/PerformanceMonitor.js';

// Importando a FooterView e os dados do usuário.
import { FooterView } from './views/FooterView.js';
import { USER_DATA } from './data/UserData.js';

class Application {
    constructor() {
        this.app = null;
        this.isInitialized = false;
        this.initializeApplication();
    }

    /**
     * @brief Initializes the core application and then sets up UI controls.
     */
    async initializeApplication() {
        try {
            console.info('Application: Starting initialization...');
            
            const appConfig = {
                services: {
                    contentModel: ContentModel,
                    userModel: UserModel,
                    themeManager: ThemeManager,
                    accessibilityManager: AccessibilityManager,
                    performanceMonitor: PerformanceMonitor
                },
                controllers: {
                    mainController: MainController,
                    navigationController: NavigationController
                }
            };
            
            this.app = new App(appConfig);
            await this.app.initialize();
            
            await this.setupGlobalUIControls();
            await this.initializeFooter();

            this.isInitialized = true;
            console.info('Application: Initialized successfully');

        } catch (error) {
            console.error('Application: Failed to initialize.', error);
            this.showErrorMessage('Failed to load application. Please refresh the page.');
        } finally {
            this.hideLoadingOverlay();
        }
    }

    /**
     * @brief Hides the loading overlay
     */
    hideLoadingOverlay() {
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.opacity = '0';
            setTimeout(() => {
                loadingOverlay.style.display = 'none';
            }, 500);
        }
    }

    /**
     * @brief Shows error message to user
     */
    showErrorMessage(message) {
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #e74c3c;
            color: white;
            padding: 20px;
            border-radius: 8px;
            z-index: 10000;
            text-align: center;
        `;
        errorDiv.innerHTML = `
            <h3>Error</h3>
            <p>${message}</p>
            <button onclick="this.parentElement.remove()" style="margin-top: 10px; padding: 5px 10px;">Dismiss</button>
        `;
        document.body.appendChild(errorDiv);
    }
    
    /**
     * @brief Initializes and renders the footer view.
     */
    async initializeFooter() {
        const footerContainer = document.getElementById('footer-container');
        if (!footerContainer) {
            console.warn('Application: Footer container not found.');
            return;
        }

        try {
            const footerView = new FooterView({
                container: footerContainer,
                footerData: USER_DATA
            });

            await footerView.render();
            console.info('Application: Footer initialized.');
        } catch (error) {
            console.error('Application: Error initializing footer.', error);
        }
    }

    /**
     * @brief Sets up global UI controls (theme toggle, accessibility buttons).
     */
    async setupGlobalUIControls() {
        // Verifica se os controles já existem
        if (document.querySelector('.app-controls')) {
            return;
        }

        const controlsContainer = document.createElement('div');
        controlsContainer.className = 'app-controls';
        document.body.appendChild(controlsContainer);

        // --- Theme Toggle Button ---
        const themeManager = this.app.getService('themeManager');
        if (themeManager) {
            this.createThemeToggle(themeManager, controlsContainer);
        }

        // --- Accessibility Controls ---
        const accessibilityManager = this.app.getService('accessibilityManager');
        if (accessibilityManager) {
            this.createAccessibilityControls(accessibilityManager, controlsContainer);
        }

        console.info('Application: UI Controls initialized.');
    }

    /**
     * @brief Creates theme toggle button
     */
    createThemeToggle(themeManager, container) {
        const themeToggleBtn = document.createElement('button');
        themeToggleBtn.className = 'app-control-button theme-toggle-btn';
        themeToggleBtn.setAttribute('aria-label', 'Toggle theme');
        
        const updateThemeIcon = () => {
            const isDark = themeManager.isDarkMode();
            themeToggleBtn.innerHTML = isDark ? '☀️' : '🌙';
            themeToggleBtn.setAttribute('aria-label', `Switch to ${isDark ? 'light' : 'dark'} theme`);
        };
        
        themeToggleBtn.addEventListener('click', () => {
            themeManager.toggleTheme();
            // A atualização do ícone será feita pelo evento do ThemeManager
        });

        // Atualiza o ícone quando o tema mudar
        this.app.eventBus.subscribe('theme:changed', updateThemeIcon);
        
        container.appendChild(themeToggleBtn);
        updateThemeIcon(); // Define o ícone inicial
    }

    /**
     * @brief Creates accessibility controls
     */
    createAccessibilityControls(accessibilityManager, container) {
        // Container principal de acessibilidade
        const accessibilityContainer = document.createElement('div');
        accessibilityContainer.className = 'accessibility-container';
        
        // Botão hamburguer para menu de acessibilidade
        const menuToggle = document.createElement('button');
        menuToggle.className = 'app-control-button accessibility-menu-toggle';
        menuToggle.setAttribute('aria-label', 'Accessibility options');
        menuToggle.innerHTML = '👁️';
        menuToggle.setAttribute('aria-expanded', 'false');
        
        // Menu de acessibilidade (inicialmente escondido)
        const menu = document.createElement('div');
        menu.className = 'accessibility-menu';
        menu.style.display = 'none';
        
        // Itens do menu
        const menuItems = [
            {
                label: 'Increase Font Size',
                action: () => accessibilityManager.increaseFontSize(),
                icon: 'A+'
            },
            {
                label: 'Decrease Font Size', 
                action: () => accessibilityManager.decreaseFontSize(),
                icon: 'A-'
            },
            {
                label: 'High Contrast',
                action: () => {
                    const current = document.body.classList.contains('high-contrast');
                    accessibilityManager.toggleHighContrast(!current);
                },
                icon: '⚫'
            },
            {
                label: 'Reduced Motion',
                action: () => {
                    const current = document.body.classList.contains('reduced-motion');
                    accessibilityManager.toggleReducedMotion(!current);
                },
                icon: '🌀'
            }
        ];

        menuItems.forEach(item => {
            const button = document.createElement('button');
            button.className = 'accessibility-menu-item';
            button.setAttribute('aria-label', item.label);
            button.innerHTML = `<span class="menu-item-icon">${item.icon}</span><span class="menu-item-label">${item.label}</span>`;
            button.addEventListener('click', item.action);
            menu.appendChild(button);
        });

        // Toggle do menu
        menuToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
            menu.style.display = isExpanded ? 'none' : 'block';
            menuToggle.setAttribute('aria-expanded', (!isExpanded).toString());
        });

        // Fechar menu quando clicar fora
        document.addEventListener('click', () => {
            menu.style.display = 'none';
            menuToggle.setAttribute('aria-expanded', 'false');
        });

        accessibilityContainer.appendChild(menuToggle);
        accessibilityContainer.appendChild(menu);
        container.appendChild(accessibilityContainer);
    }

    /**
     * @brief Destroy application
     */
    async destroy() {
        if (this.app && typeof this.app.shutdown === 'function') {
            await this.app.shutdown();
        }
        this.isInitialized = false;
    }
}

// Inicialização segura
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new Application();
    });
} else {
    new Application();
}