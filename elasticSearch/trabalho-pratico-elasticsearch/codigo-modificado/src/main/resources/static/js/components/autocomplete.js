import { fetchSuggestions } from '../services/apiService.js';
import { useDebounce } from '../hooks/useDebounce.js';

export class Autocomplete {
    constructor() {
        this.input = document.getElementById('search-input');
        this.dropdown = document.getElementById('autocomplete-list');
        this.form = document.getElementById('search-form');
        this.btn = document.getElementById('search-btn');
        this.currentIndex = -1;
        
        if (!this.input || !this.dropdown) return;
        
        this.init();
    }

    init() {
        // Usa o hook de debounce para evitar requests excessivos (300ms)
        const debouncedFetch = useDebounce(this.handleInput.bind(this), 300);
        
        this.input.addEventListener('input', debouncedFetch);
        this.input.addEventListener('keydown', this.handleKeydown.bind(this));
        
        // Clica fora fecha o dropdown
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
                this.closeDropdown();
            }
        });
        
        // Loader do botão ao fazer submit
        this.form.addEventListener('submit', () => {
            if (this.input.value.trim() !== '') {
                this.btn.classList.add('loading');
            }
        });
    }

    async handleInput(e) {
        const query = e.target.value.trim();
        
        if (query.length < 2) {
            this.closeDropdown();
            return;
        }

        const suggestions = await fetchSuggestions(query);
        this.renderDropdown(suggestions);
    }

    renderDropdown(suggestions) {
        if (!suggestions || suggestions.length === 0) {
            this.closeDropdown();
            return;
        }

        this.dropdown.innerHTML = '';
        this.currentIndex = -1;

        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.setAttribute('role', 'option');
            item.innerHTML = `
                <i data-lucide="search" style="width: 14px; height: 14px;"></i>
                <span>${suggestion}</span>
            `;
            
            // Navegação por click
            item.addEventListener('click', () => {
                this.input.value = suggestion;
                this.closeDropdown();
                this.form.submit();
            });

            this.dropdown.appendChild(item);
        });

        // Re-renderiza icones (Lucide não observa o DOM automaticamente sem config)
        if (window.lucide) {
            window.lucide.createIcons();
        }
        
        this.dropdown.style.display = 'block';
        this.input.setAttribute('aria-expanded', 'true');
    }

    closeDropdown() {
        this.dropdown.style.display = 'none';
        this.dropdown.innerHTML = '';
        this.input.setAttribute('aria-expanded', 'false');
        this.currentIndex = -1;
    }

    handleKeydown(e) {
        const items = this.dropdown.querySelectorAll('.autocomplete-item');
        if (items.length === 0 || this.dropdown.style.display === 'none') return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.currentIndex = Math.min(this.currentIndex + 1, items.length - 1);
            this.updateActiveItem(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.currentIndex = Math.max(this.currentIndex - 1, -1);
            this.updateActiveItem(items);
        } else if (e.key === 'Enter' && this.currentIndex > -1) {
            e.preventDefault();
            this.input.value = items[this.currentIndex].querySelector('span').innerText;
            this.closeDropdown();
            this.form.submit();
        } else if (e.key === 'Escape') {
            this.closeDropdown();
        }
    }

    updateActiveItem(items) {
        items.forEach(item => item.classList.remove('active'));
        if (this.currentIndex > -1) {
            items[this.currentIndex].classList.add('active');
            this.input.value = items[this.currentIndex].querySelector('span').innerText;
        }
    }
}
