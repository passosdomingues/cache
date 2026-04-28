/**
 * Hook utilitário para debounce de funções.
 * Retarda a execução da função até que `delay` ms tenham se passado
 * desde a última vez que ela foi chamada.
 * 
 * @param {Function} func A função a ser envelopada
 * @param {number} delay O tempo de debounce em milissegundos
 * @returns {Function} Função debounced
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
