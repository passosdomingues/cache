/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Enumeration of available role names.
 * @us US-1603 Register new users - Granularity: Role Definition
 */
package com.bluevelvet.auth;

/**
 * @brief Enumeration representing the various roles available in the system.
 */
public enum RoleName {
    /**
     * @brief Role for system administrators.
     */
    ROLE_ADMINISTRATOR,
    /**
     * @brief Role for sales managers.
     */
    ROLE_SALES_MANAGER,
    /**
     * @brief Role for content editors.
     */
    ROLE_EDITOR,
    /**
     * @brief Role for assistants.
     */
    ROLE_ASSISTANT,
    /**
     * @brief Role for shipping managers.
     */
    ROLE_SHIPPING_MANAGER
}
