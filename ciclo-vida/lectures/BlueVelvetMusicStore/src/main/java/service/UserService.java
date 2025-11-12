package service;

import com.bluevelvet.domain.dto.UserDTO;
import org.springframework.security.core.userdetails.UserDetailsService;

/**
 * @brief Service interface for user operations
 * @details Defines the contract for user business logic and authentication
 * Extends Spring Security's UserDetailsService for integration
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
public interface UserService extends UserDetailsService {

    /**
     * @brief Get or create a user from OAuth provider
     * @param email The user email
     * @param fullName The user full name
     * @param pictureUrl The user picture URL
     * @param oauthProvider The OAuth provider (e.g., "google")
     * @param oauthProviderId The provider's unique ID
     * @return The user DTO
     */
    UserDTO getOrCreateOAuthUser(String email, String fullName, String pictureUrl, String oauthProvider, String oauthProviderId);

    /**
     * @brief Get a user by email
     * @param email The user email
     * @return The user DTO
     * @throws com.bluevelvet.exception.ResourceNotFoundException if user not found
     */
    UserDTO getUserByEmail(String email);

    /**
     * @brief Get a user by ID
     * @param id The user ID
     * @return The user DTO
     * @throws com.bluevelvet.exception.ResourceNotFoundException if user not found
     */
    UserDTO getUserById(Long id);

    /**
     * @brief Update user information
     * @param id The user ID
     * @param userDTO The updated user data
     * @return The updated user DTO
     * @throws com.bluevelvet.exception.ResourceNotFoundException if user not found
     */
    UserDTO updateUser(Long id, UserDTO userDTO);

    /**
     * @brief Verify user email
     * @param id The user ID
     * @return The updated user DTO
     * @throws com.bluevelvet.exception.ResourceNotFoundException if user not found
     */
    UserDTO verifyUserEmail(Long id);

    /**
     * @brief Deactivate a user account
     * @param id The user ID
     * @throws com.bluevelvet.exception.ResourceNotFoundException if user not found
     */
    void deactivateUser(Long id);

    /**
     * @brief Activate a user account
     * @param id The user ID
     * @return The updated user DTO
     * @throws com.bluevelvet.exception.ResourceNotFoundException if user not found
     */
    UserDTO activateUser(Long id);

    /**
     * @brief Update last login timestamp
     * @param id The user ID
     * @throws com.bluevelvet.exception.ResourceNotFoundException if user not found
     */
    void updateLastLogin(Long id);

}
