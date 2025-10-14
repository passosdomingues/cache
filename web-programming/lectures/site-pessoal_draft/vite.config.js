import { defineConfig } from 'vite';

/**
 * @brief Vite configuration for MVC framework
 * @description Build configuration optimized for modular JavaScript and GitHub Pages
 */
export default defineConfig({
    base: '/site/', // repository name
    root: '.',
    publicDir: 'public',
    build: {
        outDir: 'dist',
        assetsDir: 'public/images',
        sourcemap: true,
        rollupOptions: {
            input: {
                main: './index.html'
            },
            output: {
                manualChunks: {
                    'mvc-data': [
                        './src/js/data/PortfolioData.js',
                        './src/js/data/UserData.js'
                    ],
                    'mvc-core': [
                        './src/js/core/App.js',
                        './src/js/core/EventBus.js',
                        './src/js/core/Router.js'
                    ],
                    'mvc-models': [
                        './src/js/models/ContentModel.js',
                        './src/js/models/UserModel.js'
                    ],
                    'mvc-controllers': [
                        './src/js/controllers/MainController.js',
                        './src/js/controllers/NavigationController.js',
                        './src/js/controllers/SectionController.js'
                    ],
                    'mvc-views': [
                        './src/js/views/BaseView.js',
                        './src/js/views/FooterView.js',
                        './src/js/views/HeroView.js',
                        './src/js/views/NavigationView.js',
                        './src/js/views/ViewManager.js'
                    ],
                    'mvc-services': [
                        './src/js/services/AccessibilityManager.js',
                        './src/js/services/ErrorReporter.js',
                        './src/js/services/PerformanceMonitor.js',
                        './src/js/services/ThemeManager.js'
                    ]
                },
                chunkFileNames: 'public/images/js/[name]-[hash].js',
                entryFileNames: 'public/images/js/[name]-[hash].js',
                assetFileNames: 'public/images/[ext]/[name]-[hash].[ext]'
            }
        }
    },
    server: {
        port: 3000,
        open: true,
        cors: true
    },
    optimizeDeps: {
        include: ['src/js/core/*.js', 'src/js/models/*.js']
    }
});