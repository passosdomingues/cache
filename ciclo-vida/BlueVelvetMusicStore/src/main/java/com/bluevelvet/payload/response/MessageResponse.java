/**
 * @brief Response object for messages.
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 November 30
 */
package com.bluevelvet.payload.response;

import lombok.AllArgsConstructor;
import lombok.Data;

/**
 * @brief Data transfer object for message responses.
 */
@Data
@AllArgsConstructor
public class MessageResponse {
	/**
	 * @brief The message content.
	 */
	private String message;
}
