package dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.*;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.Set;

/**
 * @brief Data Transfer Object for User
 * @details Used for API responses and request payloads
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserDTO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * @brief User ID
     */
    private Long id;

    /**
     * @brief User email
     */
    @NotBlank(message = "Email cannot be blank")
    @Email(message = "Email should be valid")
    private String email;

    /**
     * @brief User full name
     */
    @NotBlank(message = "Full name cannot be blank")
    private String fullName;

    /**
     * @brief User profile picture URL
     */
    private String pictureUrl;

    /**
     * @brief OAuth provider
     */
    private String oauthProvider;

    /**
     * @brief User roles
     */
    private Set<String> roles;

    /**
     * @brief Is active flag
     */
    @Builder.Default
    private Boolean isActive = Boolean.TRUE;

    /**
     * @brief Is email verified flag
     */
    @Builder.Default
    private Boolean isEmailVerified = Boolean.FALSE;

    /**
     * @brief Creation timestamp
     */
    private LocalDateTime createdAt;

    /**
     * @brief Last update timestamp
     */
    private LocalDateTime updatedAt;

    /**
     * @brief Last login timestamp
     */
    private LocalDateTime lastLoginAt;

}
