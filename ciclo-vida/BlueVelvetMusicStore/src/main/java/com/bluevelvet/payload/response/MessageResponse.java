/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025-12-08
 * @brief Response object for messages.
 * @us US-0000 Shared - Granularity: DTO
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
