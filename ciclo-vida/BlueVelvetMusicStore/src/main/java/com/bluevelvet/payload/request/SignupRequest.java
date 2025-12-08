/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025-12-08
 * @brief Request object for user registration.
 * @us US-1603 Register new users - Granularity: DTO
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
