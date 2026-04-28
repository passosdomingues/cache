/**
 * @brief Autocomplete component for the search input.
 *
 * Fetches term suggestions from the /v1/suggest endpoint with a debounced
 * input handler and renders a dropdown list with keyboard navigation support.
 *
 * @module autocomplete
 */
import { fetchSuggestions } from '../services/apiService.js';
import { useDebounce } from '../hooks/useDebounce.js';

export class Autocomplete {
  /**
   * @brief Initializes the autocomplete component.
   *
   * Locates DOM elements by ID and binds input, keyboard, and click
   * event listeners. Exits silently if required elements are missing.
   */
  constructor() {
    this.input = document.getElementById('search-input');
    this.dropdown = document.getElementById('autocomplete-list');
    this.form = document.getElementById('search-form');
    this.btn = document.getElementById('search-btn');
    this.currentIndex = -1;

    if (!this.input || !this.dropdown) return;
    this.init();
  }

  /**
   * @brief Binds all interaction event listeners.
   */
  init() {
    const debouncedFetch = useDebounce(this.handleInput.bind(this), 300);

    this.input.addEventListener('input', debouncedFetch);
    this.input.addEventListener('keydown', this.handleKeydown.bind(this));

    /* Close dropdown when clicking outside */
    document.addEventListener('click', (e) => {
      if (!this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
        this.closeDropdown();
      }
    });

    /* Show loading state on form submit */
    this.form?.addEventListener('submit', () => {
      if (this.input.value.trim() !== '') {
        this.btn?.classList.add('loading');
      }
    });
  }

  /**
   * @brief Handles debounced input events by fetching suggestions.
   * @param {Event} e - The input event.
   */
  async handleInput(e) {
    const query = e.target.value.trim();

    if (query.length < 2) {
      this.closeDropdown();
      return;
    }

    const suggestions = await fetchSuggestions(query);
    this.renderDropdown(suggestions);
  }

  /**
   * @brief Renders the suggestion dropdown list.
   * @param {string[]} suggestions - Array of suggestion strings.
   */
  renderDropdown(suggestions) {
    if (!suggestions || suggestions.length === 0) {
      this.closeDropdown();
      return;
    }

    this.dropdown.innerHTML = '';
    this.currentIndex = -1;

    suggestions.forEach((suggestion) => {
      const item = document.createElement('div');
      item.className = 'autocomplete-item';
      item.setAttribute('role', 'option');
      item.innerHTML = `
        <i data-lucide="search" style="width: 14px; height: 14px;"></i>
        <span>${suggestion}</span>
      `;

      item.addEventListener('click', () => {
        this.input.value = suggestion;
        this.closeDropdown();
        this.form.submit();
      });

      this.dropdown.appendChild(item);
    });

    /* Re-render Lucide icons for dynamically added elements */
    if (window.lucide) {
      window.lucide.createIcons();
    }

    this.dropdown.style.display = 'block';
    this.input.setAttribute('aria-expanded', 'true');
  }

  /**
   * @brief Hides the dropdown and resets selection state.
   */
  closeDropdown() {
    this.dropdown.style.display = 'none';
    this.dropdown.innerHTML = '';
    this.input.setAttribute('aria-expanded', 'false');
    this.currentIndex = -1;
  }

  /**
   * @brief Handles keyboard navigation within the dropdown.
   * @param {KeyboardEvent} e - The keydown event.
   */
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

  /**
   * @brief Updates the visual active state on dropdown items.
   * @param {NodeList} items - The list of autocomplete item elements.
   */
  updateActiveItem(items) {
    items.forEach(item => item.classList.remove('active'));
    if (this.currentIndex > -1) {
      items[this.currentIndex].classList.add('active');
      this.input.value = items[this.currentIndex].querySelector('span').innerText;
    }
  }
}
