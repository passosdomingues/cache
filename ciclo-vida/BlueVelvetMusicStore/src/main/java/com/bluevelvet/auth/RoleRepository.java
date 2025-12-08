/**
 * @brief Repository interface for Role entity.
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 November 30 [20:09]
 */
package com.bluevelvet.auth;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * @brief Repository for accessing Role data.
 */
@Repository
public interface RoleRepository extends JpaRepository<Role, Long> {
    /**
     * @brief Finds a role by its name.
     * @param name The name of the role.
     * @return An Optional containing the Role if found, or empty otherwise.
     */
    Optional<Role> findByName(RoleName name);
}
