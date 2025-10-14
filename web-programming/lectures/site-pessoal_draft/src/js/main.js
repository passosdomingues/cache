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

class Application {
    constructor() {
        this.app = null;
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
            console.info('Application: All components initialized successfully.');

            // After the app is ready, set up the UI controls
            this.setupUIControls();

        } catch (error) {
            console.error('Application: Critical initialization failed.', error);
        }
    }

    /**
     * @brief Creates and manages the UI controls for theme and accessibility.
     * @description This method dynamically injects the buttons into the page,
     * relying on the modular CSS files for styling.
     */
    setupUIControls() {
        const controlsContainer = document.createElement('div');
        // We will style this class in our CSS file
        controlsContainer.className = 'app-controls';
        document.body.appendChild(controlsContainer);

        // --- Theme Toggle Button ---
        const themeManager = this.app.services.themeManager;
        const themeToggleBtn = document.createElement('button');
        // Using general .btn class and a specific one
        themeToggleBtn.className = 'btn btn--icon app-control-button theme-toggle-btn';
        themeToggleBtn.setAttribute('aria-label', 'Toggle light/dark theme');
        
        const updateThemeIcon = () => {
            // Using icons for a cleaner look
            themeToggleBtn.innerHTML = themeManager.isDarkMode() ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
        };
        
        themeToggleBtn.addEventListener('click', () => {
            themeManager.toggleTheme();
            updateThemeIcon();
        });
        
        controlsContainer.appendChild(themeToggleBtn);
        updateThemeIcon(); // Set initial icon

        // --- Accessibility Buttons ---
        const accessibilityManager = this.app.services.accessibilityManager;
        
        const increaseFontBtn = document.createElement('button');
        increaseFontBtn.className = 'btn btn--icon app-control-button';
        increaseFontBtn.setAttribute('aria-label', 'Increase font size');
        increaseFontBtn.innerHTML = 'A+';
        increaseFontBtn.addEventListener('click', () => accessibilityManager.increaseFontSize());
        controlsContainer.appendChild(increaseFontBtn);

        const decreaseFontBtn = document.createElement('button');
        decreaseFontBtn.className = 'btn btn--icon app-control-button';
        decreaseFontBtn.setAttribute('aria-label', 'Decrease font size');
        decreaseFontBtn.innerHTML = 'A-';
        decreaseFontBtn.addEventListener('click', () => accessibilityManager.decreaseFontSize());
        controlsContainer.appendChild(decreaseFontBtn);

        console.info('Application: UI Controls initialized.');
    }
}

document.addEventListener('DOMContentLoaded', () => new Application());