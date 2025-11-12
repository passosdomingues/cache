/**
 * @brief Accessibility management script
 * @details Handles accessibility features like high contrast, large text, and reduced motion
 * @author Rafael Passos Domingues
 * @version 1.0.0
 */

(function() {
    'use strict';

    const ACCESSIBILITY_KEY = 'bluevelvet-accessibility';
    const ACCESSIBILITY_TOGGLE_ID = 'accessibilityToggle';
    const ACCESSIBILITY_PANEL_ID = 'accessibilityPanel';
    const CLOSE_ACCESSIBILITY_ID = 'closeAccessibility';
    
    const HIGH_CONTRAST_ID = 'highContrast';
    const LARGE_TEXT_ID = 'largeText';
    const REDUCED_MOTION_ID = 'reducedMotion';

    /**
     * @brief Initialize accessibility settings from localStorage
     */
    function initializeAccessibility() {
        const settings = getAccessibilitySettings();
        
        if (settings.highContrast) {
            enableHighContrast();
            document.getElementById(HIGH_CONTRAST_ID).checked = true;
        }
        
        if (settings.largeText) {
            enableLargeText();
            document.getElementById(LARGE_TEXT_ID).checked = true;
        }
        
        if (settings.reducedMotion) {
            enableReducedMotion();
            document.getElementById(REDUCED_MOTION_ID).checked = true;
        }
    }

    /**
     * @brief Get accessibility settings from localStorage
     * @return Object with accessibility settings
     */
    function getAccessibilitySettings() {
        const stored = localStorage.getItem(ACCESSIBILITY_KEY);
        return stored ? JSON.parse(stored) : {
            highContrast: false,
            largeText: false,
            reducedMotion: false
        };
    }

    /**
     * @brief Save accessibility settings to localStorage
     * @param settings The settings object
     */
    function saveAccessibilitySettings(settings) {
        localStorage.setItem(ACCESSIBILITY_KEY, JSON.stringify(settings));
    }

    /**
     * @brief Enable high contrast mode
     */
    function enableHighContrast() {
        document.getElementById('app').classList.add('high-contrast');
    }

    /**
     * @brief Disable high contrast mode
     */
    function disableHighContrast() {
        document.getElementById('app').classList.remove('high-contrast');
    }

    /**
     * @brief Enable large text
     */
    function enableLargeText() {
        document.getElementById('app').classList.add('large-text');
    }

    /**
     * @brief Disable large text
     */
    function disableLargeText() {
        document.getElementById('app').classList.remove('large-text');
    }

    /**
     * @brief Enable reduced motion
     */
    function enableReducedMotion() {
        document.getElementById('app').classList.add('reduce-motion');
    }

    /**
     * @brief Disable reduced motion
     */
    function disableReducedMotion() {
        document.getElementById('app').classList.remove('reduce-motion');
    }

    /**
     * @brief Toggle accessibility panel
     */
    function toggleAccessibilityPanel() {
        const panel = document.getElementById(ACCESSIBILITY_PANEL_ID);
        if (panel) {
            panel.classList.toggle('show');
        }
    }

    /**
     * @brief Close accessibility panel
     */
    function closeAccessibilityPanel() {
        const panel = document.getElementById(ACCESSIBILITY_PANEL_ID);
        if (panel) {
            panel.classList.remove('show');
        }
    }

    /**
     * @brief Setup event listeners for accessibility controls
     */
    function setupEventListeners() {
        // Toggle button
        const accessibilityToggle = document.getElementById(ACCESSIBILITY_TOGGLE_ID);
        if (accessibilityToggle) {
            accessibilityToggle.addEventListener('click', toggleAccessibilityPanel);
        }

        // Close button
        const closeButton = document.getElementById(CLOSE_ACCESSIBILITY_ID);
        if (closeButton) {
            closeButton.addEventListener('click', closeAccessibilityPanel);
        }

        // High contrast checkbox
        const highContrastCheckbox = document.getElementById(HIGH_CONTRAST_ID);
        if (highContrastCheckbox) {
            highContrastCheckbox.addEventListener('change', function() {
                if (this.checked) {
                    enableHighContrast();
                } else {
                    disableHighContrast();
                }
                updateAccessibilitySettings();
            });
        }

        // Large text checkbox
        const largeTextCheckbox = document.getElementById(LARGE_TEXT_ID);
        if (largeTextCheckbox) {
            largeTextCheckbox.addEventListener('change', function() {
                if (this.checked) {
                    enableLargeText();
                } else {
                    disableLargeText();
                }
                updateAccessibilitySettings();
            });
        }

        // Reduced motion checkbox
        const reducedMotionCheckbox = document.getElementById(REDUCED_MOTION_ID);
        if (reducedMotionCheckbox) {
            reducedMotionCheckbox.addEventListener('change', function() {
                if (this.checked) {
                    enableReducedMotion();
                } else {
                    disableReducedMotion();
                }
                updateAccessibilitySettings();
            });
        }

        // Close panel when clicking outside
        document.addEventListener('click', function(event) {
            const panel = document.getElementById(ACCESSIBILITY_PANEL_ID);
            const toggle = document.getElementById(ACCESSIBILITY_TOGGLE_ID);
            
            if (panel && toggle && !panel.contains(event.target) && !toggle.contains(event.target)) {
                closeAccessibilityPanel();
            }
        });

        // Close panel on ESC key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeAccessibilityPanel();
            }
        });
    }

    /**
     * @brief Update accessibility settings in localStorage
     */
    function updateAccessibilitySettings() {
        const settings = {
            highContrast: document.getElementById(HIGH_CONTRAST_ID).checked,
            largeText: document.getElementById(LARGE_TEXT_ID).checked,
            reducedMotion: document.getElementById(REDUCED_MOTION_ID).checked
        };
        saveAccessibilitySettings(settings);
    }

    /**
     * @brief Initialize on DOM ready
     */
    document.addEventListener('DOMContentLoaded', function() {
        initializeAccessibility();
        setupEventListeners();
    });

    // Expose functions globally if needed
    window.bluevelvetAccessibility = {
        toggleAccessibilityPanel,
        closeAccessibilityPanel,
        enableHighContrast,
        disableHighContrast,
        enableLargeText,
        disableLargeText,
        enableReducedMotion,
        disableReducedMotion
    };

})();
