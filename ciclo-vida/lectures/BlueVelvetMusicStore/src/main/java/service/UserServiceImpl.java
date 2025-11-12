package service;

import com.bluevelvet.domain.dto.UserDTO;
import com.bluevelvet.domain.entity.RoleEntity;
import com.bluevelvet.domain.entity.UserEntity;
import com.bluevelvet.exception.ResourceNotFoundException;
import com.bluevelvet.repository.RoleRepository;
import com.bluevelvet.repository.UserRepository;
import com.bluevelvet.service.UserService;
import com.bluevelvet.util.EntityMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

/**
 * @brief Implementation of UserService
 * @details Provides business logic for user management and authentication
 * Integrates with Spring Security for authentication and authorization
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class UserServiceImpl implements UserService {

    private final UserRepository userRepository;
    private final RoleRepository roleRepository;

    /**
     * @brief Get or create a user from OAuth provider
     * @param email The user email
     * @param fullName The user full name
     * @param pictureUrl The user picture URL
     * @param oauthProvider The OAuth provider (e.g., "google")
     * @param oauthProviderId The provider's unique ID
     * @return The user DTO
     */
    @Override
    public UserDTO getOrCreateOAuthUser(String email, String fullName, String pictureUrl, 
                                        String oauthProvider, String oauthProviderId) {
        log.info("Getting or creating OAuth user: {} from provider: {}", email, oauthProvider);

        // Try to find existing user by OAuth provider ID
        UserEntity user = userRepository.findByOAuthProviderAndProviderId(oauthProvider, oauthProviderId)
            .orElseGet(() -> {
                // If not found, try to find by email
                return userRepository.findByEmail(email)
                    .orElseGet(() -> {
                        // Create new user if not found
                        log.info("Creating new OAuth user: {}", email);
                        UserEntity newUser = UserEntity.builder()
                            .email(email)
                            .fullName(fullName)
                            .pictureUrl(pictureUrl)
                            .oauthProvider(oauthProvider)
                            .oauthProviderId(oauthProviderId)
                            .isActive(true)
                            .isEmailVerified(true)
                            .build();

                        // Assign default USER role
                        RoleEntity userRole = roleRepository.findByName("USER")
                            .orElseGet(() -> {
                                log.warn("USER role not found, creating it");
                                return roleRepository.save(
                                    RoleEntity.builder()
                                        .name("USER")
                                        .description("Default user role")
                                        .build()
                                );
                            });

                        newUser.addRole(userRole);
                        return userRepository.save(newUser);
                    });
            });

        // Update OAuth provider information if user was found by email
        if (user.getOauthProvider() == null) {
            user.setOauthProvider(oauthProvider);
            user.setOauthProviderId(oauthProviderId);
            user.setPictureUrl(pictureUrl);
            user.setIsEmailVerified(true);
            user = userRepository.save(user);
            log.info("Updated user with OAuth information: {}", email);
        }

        return EntityMapper.toUserDTO(user);
    }

    /**
     * @brief Get a user by email
     * @param email The user email
     * @return The user DTO
     * @throws ResourceNotFoundException if user not found
     */
    @Override
    @Transactional(readOnly = true)
    public UserDTO getUserByEmail(String email) {
        log.debug("Fetching user by email: {}", email);

        UserEntity user = userRepository.findByEmail(email)
            .orElseThrow(() -> new ResourceNotFoundException("User with email: " + email + " not found"));

        return EntityMapper.toUserDTO(user);
    }

    /**
     * @brief Get a user by ID
     * @param id The user ID
     * @return The user DTO
     * @throws ResourceNotFoundException if user not found
     */
    @Override
    @Transactional(readOnly = true)
    public UserDTO getUserById(Long id) {
        log.debug("Fetching user by ID: {}", id);

        UserEntity user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User", id));

        return EntityMapper.toUserDTO(user);
    }

    /**
     * @brief Update user information
     * @param id The user ID
     * @param userDTO The updated user data
     * @return The updated user DTO
     * @throws ResourceNotFoundException if user not found
     */
    @Override
    public UserDTO updateUser(Long id, UserDTO userDTO) {
        log.info("Updating user with ID: {}", id);

        UserEntity user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User", id));

        user.setFullName(userDTO.getFullName());
        user.setPictureUrl(userDTO.getPictureUrl());

        UserEntity updatedUser = userRepository.save(user);
        log.info("User updated successfully with ID: {}", id);

        return EntityMapper.toUserDTO(updatedUser);
    }

    /**
     * @brief Verify user email
     * @param id The user ID
     * @return The updated user DTO
     * @throws ResourceNotFoundException if user not found
     */
    @Override
    public UserDTO verifyUserEmail(Long id) {
        log.info("Verifying email for user with ID: {}", id);

        UserEntity user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User", id));

        user.setIsEmailVerified(true);
        UserEntity updatedUser = userRepository.save(user);
        log.info("Email verified successfully for user with ID: {}", id);

        return EntityMapper.toUserDTO(updatedUser);
    }

    /**
     * @brief Deactivate a user account
     * @param id The user ID
     * @throws ResourceNotFoundException if user not found
     */
    @Override
    public void deactivateUser(Long id) {
        log.info("Deactivating user with ID: {}", id);

        UserEntity user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User", id));

        user.setIsActive(false);
        userRepository.save(user);
        log.info("User deactivated successfully with ID: {}", id);
    }

    /**
     * @brief Activate a user account
     * @param id The user ID
     * @return The updated user DTO
     * @throws ResourceNotFoundException if user not found
     */
    @Override
    public UserDTO activateUser(Long id) {
        log.info("Activating user with ID: {}", id);

        UserEntity user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User", id));

        user.setIsActive(true);
        UserEntity updatedUser = userRepository.save(user);
        log.info("User activated successfully with ID: {}", id);

        return EntityMapper.toUserDTO(updatedUser);
    }

    /**
     * @brief Update last login timestamp
     * @param id The user ID
     * @throws ResourceNotFoundException if user not found
     */
    @Override
    public void updateLastLogin(Long id) {
        log.debug("Updating last login for user with ID: {}", id);

        UserEntity user = userRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("User", id));

        user.setLastLoginAt(LocalDateTime.now());
        userRepository.save(user);
    }

    /**
     * @brief Load user by username (email) for Spring Security
     * @param username The username (email)
     * @return UserDetails for authentication
     * @throws UsernameNotFoundException if user not found
     */
    @Override
    @Transactional(readOnly = true)
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        log.debug("Loading user by username: {}", username);

        return userRepository.findByEmail(username)
            .orElseThrow(() -> {
                log.warn("User not found with email: {}", username);
                return new UsernameNotFoundException("User not found with email: " + username);
            });
    }

}
