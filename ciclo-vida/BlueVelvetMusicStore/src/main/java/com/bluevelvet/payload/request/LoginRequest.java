/**
 * @brief Request object for user login.
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 November 30
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
