/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Repository interface for User entity.
 * @us US-1232 Login - Granularity: Data Access
 * @us US-1603 Register new users - Granularity: Data Access
 */
package com.bluevelvet.auth;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * @brief Repository for accessing User data.
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    /**
     * @brief Finds a user by their email.
     * @param email The email to search for.
     * @return An Optional containing the User if found, or empty otherwise.
     */
    Optional<User> findByEmail(String email);

    /**
     * @brief Checks if a user exists with the given email.
     * @param email The email to check.
     * @return true if a user exists with the email, false otherwise.
     */
    Boolean existsByEmail(String email);
}
