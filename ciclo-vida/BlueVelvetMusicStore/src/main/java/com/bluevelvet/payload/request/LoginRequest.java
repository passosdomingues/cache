/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025-12-08
 * @brief Request object for user login.
 * @us US-1232 Login - Granularity: DTO
 */
package com.bluevelvet.payload.request;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

/**
 * @brief Data transfer object for login requests.
 */
@Data
public class LoginRequest {
	/**
	 * @brief The user's email.
	 */
	@NotBlank
	private String email;

	/**
	 * @brief The user's password.
	 */
	@NotBlank
	private String password;
}
