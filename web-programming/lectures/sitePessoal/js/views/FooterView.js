/**
 * @file View do footer
 * @brief Renderiza o rodapé do site
 */

import BaseView from './BaseView.js';

class FooterView extends BaseView {
    constructor() {
        const template = `
            <div class="container">
                <div class="footer-content">
                    <div class="social-links">
                        <a href="{{github}}" class="social-link" target="_blank">
                            <i class="fab fa-github"></i>
                        </a>
                        <a href="{{linkedin}}" class="social-link" target="_blank">
                            <i class="fab fa-linkedin-in"></i>
                        </a>
                        <a href="https://instagram.com/{{instagram}}" class="social-link" target="_blank">
                            <i class="fab fa-instagram"></i>
                        </a>
                        <a href="mailto:{{email}}" class="social-link">
                            <i class="fas fa-envelope"></i>
                        </a>
                    </div>
                    <p>&copy; 2024 {{name}}. Todos os direitos reservados.</p>
                    <p><a href="{{site}}" target="_blank">Site de Professor - Pandefísica</a></p>
                </div>
            </div>
        `;
        super('footer', template);
    }
}

export default FooterView;