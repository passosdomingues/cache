/**
 * Sidebar (tuning panel) open/close, range sliders, checkbox wiring.
 */
export function initSidebar() {
    const sidebar    = document.getElementById('sidebar');
    const backdrop   = document.getElementById('sidebar-backdrop');
    const openBtn    = document.getElementById('hamburger-btn');
    const closeBtn   = document.getElementById('sidebar-close-btn');
    const resetBtn   = document.getElementById('reset-tuning-btn');

    if (!sidebar) return;

    const open = () => {
        sidebar.classList.add('is-open');
        sidebar.setAttribute('aria-hidden', 'false');
        backdrop?.classList.add('is-visible');
        openBtn?.setAttribute('aria-expanded', 'true');
        closeBtn?.focus();
    };

    const close = () => {
        sidebar.classList.remove('is-open');
        sidebar.setAttribute('aria-hidden', 'true');
        backdrop?.classList.remove('is-visible');
        openBtn?.setAttribute('aria-expanded', 'false');
        openBtn?.focus();
    };

    openBtn?.addEventListener('click', open);
    closeBtn?.addEventListener('click', close);
    backdrop?.addEventListener('click', close);

    // Escape closes from anywhere
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebar.classList.contains('is-open')) close();
    });

    // ── Range sliders — live value display ──────────────────────────────
    document.querySelectorAll('.tune-range').forEach(range => {
        const valSpan = document.getElementById(range.id + '-val');
        if (valSpan) {
            range.addEventListener('input', () => {
                valSpan.textContent = range.value;
            });
        }
    });

    // ── Checkbox → hidden input wiring ──────────────────────────────────
    // Ensures unchecked checkboxes send "false" rather than being absent.
    ['highlight', 'spellCheck'].forEach(name => {
        const cb     = document.getElementById(name);
        const hidden = document.getElementById(name + '-hidden');
        if (cb && hidden) {
            const sync = () => { hidden.disabled = cb.checked; };
            cb.addEventListener('change', sync);
            sync(); // initialise on load
        }
    });

    // ── Reset to defaults ────────────────────────────────────────────────
    resetBtn?.addEventListener('click', () => {
        const defaults = {
            fuzziness:   'AUTO',
            phraseBoost: '2',
            titleBoost:  '1.5',
            slop:        '0',
        };

        Object.entries(defaults).forEach(([name, value]) => {
            const el = sidebar.querySelector(`[name="${name}"]`);
            if (el) {
                el.value = value;
                // Update range value display
                const valSpan = document.getElementById(el.id + '-val');
                if (valSpan) valSpan.textContent = value;
            }
        });

        // Re-enable both toggles
        ['highlight', 'spellCheck'].forEach(name => {
            const cb = document.getElementById(name);
            if (cb) {
                cb.checked = true;
                cb.dispatchEvent(new Event('change'));
            }
        });
    });
}
