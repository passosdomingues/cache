/**
 * Autocomplete module — debounced, quote-aware, keyboard-navigable.
 *
 * Behaviour:
 *  - Triggers after 2+ chars with 200ms debounce
 *  - Suppressed while the cursor is inside a quoted phrase
 *  - Arrow keys navigate, Enter selects, Escape closes
 *  - Each item shows a search icon for visual consistency
 */
export function initAutocomplete(endpoint) {
    const input    = document.getElementById('search-input');
    const dropdown = document.getElementById('autocomplete-list');
    if (!input || !dropdown) return;

    let debounceTimer = null;
    let activeIndex   = -1;
    let currentItems  = [];

    input.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        const val = input.value.trim();

        // Suppress autocomplete inside a quoted phrase
        if (isInsideQuotes(input.value, input.selectionStart)) {
            closeDropdown();
            return;
        }

        if (val.length < 2) { closeDropdown(); return; }

        debounceTimer = setTimeout(() => fetchSuggestions(val), 200);
    });

    // Keyboard navigation
    input.addEventListener('keydown', (e) => {
        if (!currentItems.length) return;
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            activeIndex = Math.min(activeIndex + 1, currentItems.length - 1);
            renderActive();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            activeIndex = Math.max(activeIndex - 1, -1);
            renderActive();
        } else if (e.key === 'Enter' && activeIndex >= 0) {
            e.preventDefault();
            selectItem(currentItems[activeIndex]);
        } else if (e.key === 'Escape') {
            closeDropdown();
            input.focus();
        }
    });

    // Click outside closes
    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            closeDropdown();
        }
    });

    async function fetchSuggestions(q) {
        try {
            const resp = await fetch(`${endpoint}?q=${encodeURIComponent(q)}&size=6`);
            if (!resp.ok) return;
            const titles = await resp.json();
            renderDropdown(titles);
        } catch (_) { /* network error — fail silently */ }
    }

    function renderDropdown(titles) {
        dropdown.innerHTML = '';
        currentItems = titles;
        activeIndex  = -1;

        if (!titles.length) { closeDropdown(); return; }

        titles.forEach((title, i) => {
            const item = document.createElement('div');
            item.className = 'autocomplete-item';
            item.setAttribute('role', 'option');
            item.setAttribute('id', `autocomplete-item-${i}`);

            // Search icon + label
            const icon = document.createElement('i');
            icon.setAttribute('data-lucide', 'search');
            icon.setAttribute('aria-hidden', 'true');
            icon.style.cssText = 'width:13px;height:13px;flex-shrink:0;color:var(--text-muted)';

            const label = document.createElement('span');
            label.textContent = title;

            item.appendChild(icon);
            item.appendChild(label);

            item.addEventListener('mouseenter', () => { activeIndex = i; renderActive(); });
            item.addEventListener('click', () => selectItem(title));
            dropdown.appendChild(item);
        });

        // Re-render Lucide icons inside the new items
        if (window.lucide) window.lucide.createIcons({ elements: [dropdown] });

        dropdown.style.display = 'block';
        input.setAttribute('aria-expanded', 'true');
    }

    function selectItem(title) {
        input.value = title;
        closeDropdown();
        input.closest('form').submit();
    }

    function renderActive() {
        Array.from(dropdown.children).forEach((el, i) => {
            el.classList.toggle('active', i === activeIndex);
            if (i === activeIndex) {
                el.scrollIntoView({ block: 'nearest' });
            }
        });
        input.setAttribute(
            'aria-activedescendant',
            activeIndex >= 0 ? `autocomplete-item-${activeIndex}` : ''
        );
    }

    function closeDropdown() {
        dropdown.style.display = 'none';
        dropdown.innerHTML     = '';
        currentItems           = [];
        activeIndex            = -1;
        input.setAttribute('aria-expanded', 'false');
        input.removeAttribute('aria-activedescendant');
    }

    /**
     * Returns true when cursor is inside an open double-quoted segment.
     * Prevents autocomplete from firing during exact-phrase typing.
     */
    function isInsideQuotes(text, cursorPos) {
        const before = text.substring(0, cursorPos);
        return ((before.match(/"/g) || []).length % 2) === 1;
    }
}
