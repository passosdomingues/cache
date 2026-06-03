/**
 * Theme (dark / light) with localStorage persistence.
 * Toggle button lives in the header (was previously inside the a11y panel).
 */
export function initTheme() {
    const saved = localStorage.getItem('theme') || 'dark';
    applyTheme(saved);

    document.getElementById('theme-toggle-btn')
        ?.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme') || 'dark';
            applyTheme(current === 'dark' ? 'light' : 'dark');
        });

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);

        const dark  = document.getElementById('theme-icon-dark');
        const light = document.getElementById('theme-icon-light');

        if (dark)  dark.style.display  = theme === 'dark'  ? 'inline' : 'none';
        if (light) light.style.display = theme === 'light' ? 'inline' : 'none';

        if (window.lucide) window.lucide.createIcons();
    }
}
