/**
 * Serviço de API isolado para chamadas REST.
 */

const API_BASE = '/v1';

/**
 * Busca sugestões de autocomplete
 * @param {string} query Termo de busca
 * @returns {Promise<Array>} Lista de sugestões
 */
export async function fetchSuggestions(query) {
    if (!query || query.trim() === '') return [];
    
    try {
        const response = await fetch(`${API_BASE}/suggest?query=${encodeURIComponent(query)}&size=5`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data.suggestions || [];
    } catch (error) {
        console.error('Error fetching suggestions:', error);
        return [];
    }
}
