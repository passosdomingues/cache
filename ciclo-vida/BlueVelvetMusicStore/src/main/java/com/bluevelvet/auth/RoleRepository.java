/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Repository interface for Role entity.
 * @us US-1603 Register new users - Granularity: Data Access
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
