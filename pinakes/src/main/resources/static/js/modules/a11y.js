/**
 * Accessibility panel — font size and high contrast.
 * Theme toggle was moved to header/theme.js.
 */
export function initA11y() {
    const panel    = document.getElementById('a11y-panel');
    const openBtn  = document.getElementById('a11y-toggle-btn');
    const closeBtn = document.getElementById('a11y-panel-close');

    const open  = () => {
        panel?.removeAttribute('aria-hidden');
        panel?.classList.add('is-open');
        closeBtn?.focus();
    };
    const close = () => {
        panel?.setAttribute('aria-hidden', 'true');
        panel?.classList.remove('is-open');
    };

    openBtn?.addEventListener('click', open);
    closeBtn?.addEventListener('click', close);

    // Close on Escape or click outside
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
    document.addEventListener('click', (e) => {
        if (panel?.classList.contains('is-open')
            && !panel.contains(e.target)
            && e.target !== openBtn) {
            close();
        }
    });

    // ── Font scale ──────────────────────────────────────────────────
    const fontSizes = { small: '0.875', medium: '1', large: '1.125' };
    const savedScale = localStorage.getItem('fontScale') || 'medium';
    applyFontScale(savedScale);

    document.querySelectorAll('.font-scale-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.scale === savedScale);
        btn.addEventListener('click', () => {
            const scale = btn.dataset.scale;
            applyFontScale(scale);
            localStorage.setItem('fontScale', scale);
            document.querySelectorAll('.font-scale-btn')
                    .forEach(b => b.classList.toggle('active', b === btn));
        });
    });

    function applyFontScale(scale) {
        document.documentElement.style.setProperty(
            '--font-scale', fontSizes[scale] ?? '1'
        );
    }

    // ── High contrast ───────────────────────────────────────────────
    const contrastBtn   = document.getElementById('contrast-toggle-btn');
    const contrastLabel = document.getElementById('contrast-label-text');
    const savedContrast = localStorage.getItem('contrast') || 'normal';

    applyContrast(savedContrast === 'high');

    contrastBtn?.addEventListener('click', () => {
        const isHigh = document.documentElement.getAttribute('data-contrast') === 'high';
        applyContrast(!isHigh);
    });

    function applyContrast(high) {
        if (high) {
            document.documentElement.setAttribute('data-contrast', 'high');
            localStorage.setItem('contrast', 'high');
        } else {
            document.documentElement.removeAttribute('data-contrast');
            localStorage.setItem('contrast', 'normal');
        }
        if (contrastLabel) contrastLabel.textContent = high ? 'High' : 'Normal';
        contrastBtn?.setAttribute('aria-pressed', String(high));
    }
}
