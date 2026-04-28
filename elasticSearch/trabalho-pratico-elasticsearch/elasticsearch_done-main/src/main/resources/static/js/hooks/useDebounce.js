/**
 * @brief Utility hook that creates a debounced version of a function.
 *
 * Delays execution of the wrapped function until the specified delay
 * has elapsed since the last invocation. Useful for rate-limiting
 * expensive operations triggered by rapid user input.
 *
 * @param {Function} func - The function to debounce.
 * @param {number} delay - The debounce interval in milliseconds.
 * @returns {Function} A debounced wrapper function.
 */
export function useDebounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
}
