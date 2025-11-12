package repository;

import com.bluevelvet.domain.entity.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * @brief Repository interface for UserEntity
 * @details Provides database access operations for users
 * Extends JpaRepository for CRUD operations and custom queries
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@Repository
public interface UserRepository extends JpaRepository<UserEntity, Long> {

    /**
     * @brief Find a user by email
     * @param email The user email
     * @return Optional containing the user if found
     */
    Optional<UserEntity> findByEmail(String email);

    /**
     * @brief Find a user by OAuth provider and provider ID
     * @param provider The OAuth provider (e.g., "google")
     * @param providerId The provider's unique ID for the user
     * @return Optional containing the user if found
     */
    @Query("SELECT u FROM UserEntity u WHERE u.oauthProvider = :provider AND u.oauthProviderId = :providerId")
    Optional<UserEntity> findByOAuthProviderAndProviderId(@Param("provider") String provider, @Param("providerId") String providerId);

    /**
     * @brief Check if an email already exists
     * @param email The email to check
     * @return true if the email exists, false otherwise
     */
    boolean existsByEmail(String email);

    /**
     * @brief Count all active users
     * @return The count of active users
     */
    @Query("SELECT COUNT(u) FROM UserEntity u WHERE u.isActive = true")
    long countActiveUsers();

}
