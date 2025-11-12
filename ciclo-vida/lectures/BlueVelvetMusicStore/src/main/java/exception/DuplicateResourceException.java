package exception;

/**
 * @brief Exception thrown when attempting to create a duplicate resource
 * @details Typically results in HTTP 409 Conflict response
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
public class DuplicateResourceException extends BusinessException {

    private static final long serialVersionUID = 1L;

    /**
     * @brief Constructor with resource type and field value
     * @param resourceType The type of resource (e.g., "Category")
     * @param fieldName The field name that caused the duplicate (e.g., "name")
     * @param fieldValue The value that is duplicated
     */
    public DuplicateResourceException(String resourceType, String fieldName, String fieldValue) {
        super(String.format("%s with %s '%s' already exists", resourceType, fieldName, fieldValue));
    }

    /**
     * @brief Constructor with custom message
     * @param message Custom error message
     */
    public DuplicateResourceException(String message) {
        super(message);
    }

}
