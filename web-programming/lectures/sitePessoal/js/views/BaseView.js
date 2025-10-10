/**
 * @file Classe base para todas as views
 * @brief Implementa padrão Observer e métodos comuns
 */

class BaseView {
    constructor(containerId, template) {
        this.container = document.getElementById(containerId);
        this.template = template;
        this.observers = [];
    }

    /**
     * @brief Renderiza a view no container
     * @param {Object} data - Dados para renderização
     */
    render(data = {}) {
        if (this.container) {
            this.container.innerHTML = this.compileTemplate(data);
        }
    }

    /**
     * @brief Compila o template com os dados
     * @param {Object} data - Dados para interpolação
     * @return {string} HTML compilado
     */
    compileTemplate(data) {
        return this.template.replace(/\{\{(\w+)\}\}/g, (match, key) => {
            return data[key] !== undefined ? data[key] : match;
        });
    }

    /**
     * @brief Adiciona observer
     * @param {Function} observer - Função callback
     */
    addObserver(observer) {
        this.observers.push(observer);
    }

    /**
     * @brief Notifica todos os observers
     * @param {string} event - Tipo de evento
     * @param {Object} data - Dados do evento
     */
    notifyObservers(event, data) {
        this.observers.forEach(observer => observer(event, data));
    }

    /**
     * @brief Adiciona evento ao elemento
     * @param {string} eventType - Tipo de evento
     * @param {string} selector - Seletor do elemento
     * @param {Function} handler - Manipulador do evento
     */
    addEvent(eventType, selector, handler) {
        const element = this.container.querySelector(selector);
        if (element) {
            element.addEventListener(eventType, handler);
        }
    }
}

export default BaseView;