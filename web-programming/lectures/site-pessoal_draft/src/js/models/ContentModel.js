/**
 * @file ContentModel.js
 * @brief Model responsible for managing the website's portfolio content.
 */

import { PORTFOLIO_DATA } from '../data/PortfolioData.js';

class ContentModel {
    constructor() {
        this.sections = [];
        this.isInitialized = false;
    }

    async initializeContentModel() {
        try {
            // Use os dados do PORTFOLIO_DATA diretamente
            this.sections = PORTFOLIO_DATA.sections || [];
            this.isInitialized = true;
            console.info('ContentModel: Content model initialized successfully');
        } catch (error) {
            console.error('ContentModel: Initialization failed:', error);
            throw error;
        }
    }

    getAllSections() {
        return [...this.sections].sort((a, b) => a.metadata.order - b.metadata.order);
    }

    getSection(sectionId) {
        return this.sections.find(section => section.id === sectionId);
    }
}

export { ContentModel };