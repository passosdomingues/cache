/**
 * Search UX enhancements — loading state, keyboard shortcut, form guards,
 * clear button, and example query suggestion chips.
 *
 * UX CHANGE: chips now populate the search input and focus it,
 * letting the user edit before pressing Search. The old behaviour
 * (auto-submit on click) was surprising and didn't allow editing.
 */
export function initSearch() {
    const form     = document.getElementById('search-form');
    const btn      = document.getElementById('search-btn');
    const input    = document.getElementById('search-input');
    const clearBtn = document.getElementById('search-clear-btn');

    if (!form || !btn || !input) return;

    // ── Clear button visibility ──────────────────────────────────────────
    function updateClearBtn() {
        if (!clearBtn) return;
        clearBtn.classList.toggle('is-visible', input.value.length > 0);
    }
    input.addEventListener('input', updateClearBtn);
    updateClearBtn(); // init on page load

    clearBtn?.addEventListener('click', () => {
        input.value = '';
        input.focus();
        updateClearBtn();
    });

    // ── Loading state on submit ──────────────────────────────────────────
    form.addEventListener('submit', (e) => {
        const q = input.value.trim();
        if (!q || q.length < 2) { e.preventDefault(); return; }
        btn.disabled = true;
        btn.classList.add('loading');
    });

    // ── "/" shortcut focuses the search bar ─────────────────────────────
    document.addEventListener('keydown', (e) => {
        if (e.key === '/' && document.activeElement !== input
            && document.activeElement.tagName !== 'INPUT'
            && document.activeElement.tagName !== 'TEXTAREA') {
            e.preventDefault();
            input.focus();
            input.select();
        }
    });

    // ── Example query chips ──────────────────────────────────────────────
    // Clicking a chip populates the input and focuses it — no auto-submit.
    // The user can review/edit the query, then press Enter or click Search.
    document.querySelectorAll('.query-chip[data-query]').forEach(chip => {
        chip.addEventListener('click', () => {
            const q = chip.dataset.query;
            if (!q) return;
            input.value = q;
            input.focus();
            input.setSelectionRange(q.length, q.length);
            updateClearBtn();
            // Visual feedback
            chip.classList.add('chip--active');
            setTimeout(() => chip.classList.remove('chip--active'), 600);
        });
    });
}
