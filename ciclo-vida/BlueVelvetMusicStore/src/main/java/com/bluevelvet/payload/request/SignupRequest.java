/**
 * @brief Request object for user registration.
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 November 30
 */
package com.bluevelvet.payload.request;

import java.util.Set;

import jakarta.validation.constraints.*;
import lombok.Data;

/**
 * @brief Data transfer object for signup requests.
 */
@Data
public class SignupRequest {
    /**
     * @brief The user's email.
     */
    @NotBlank
    @Size(max = 50)
    @Email
    private String email;

    /**
     * @brief The roles requested by the user.
     */
    private Set<String> role;

    /**
     * @brief The user's password.
     */
    @NotBlank
    @Size(min = 6, max = 40)
    private String password;
}
