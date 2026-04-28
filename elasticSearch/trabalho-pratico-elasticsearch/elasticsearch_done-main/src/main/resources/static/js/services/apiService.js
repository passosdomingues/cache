/**
 * @brief Isolated API service for REST endpoint communication.
 *
 * Centralizes all fetch calls to the backend, providing a clean
 * abstraction layer between UI components and the server API.
 *
 * @module apiService
 */

const API_BASE = '/v1';

/**
 * @brief Fetches autocomplete suggestions from the suggest endpoint.
 *
 * Sends a GET request to /v1/suggest and extracts the suggestions array
 * from the response. Returns an empty array on error or empty input.
 *
 * @param {string} query - The search term to get suggestions for.
 * @returns {Promise<string[]>} A list of suggestion strings.
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
