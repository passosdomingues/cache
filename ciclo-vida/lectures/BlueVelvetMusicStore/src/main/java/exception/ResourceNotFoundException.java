package exception;

/**
 * @brief Exception thrown when a requested resource is not found
 * @details Typically results in HTTP 404 response
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
public class ResourceNotFoundException extends BusinessException {

    private static final long serialVersionUID = 1L;

    /**
     * @brief Constructor with resource type and ID
     * @param resourceType The type of resource (e.g., "Category")
     * @param id The ID of the resource that was not found
     */
    public ResourceNotFoundException(String resourceType, Long id) {
        super(String.format("%s with ID %d not found", resourceType, id));
    }

    /**
     * @brief Constructor with custom message
     * @param message Custom error message
     */
    public ResourceNotFoundException(String message) {
        super(message);
    }

}
