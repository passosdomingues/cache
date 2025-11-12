package exception;

/**
 * @brief Base exception for business logic errors
 * @details Used for domain-specific exceptions that should be handled gracefully
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
public class BusinessException extends RuntimeException {

    private static final long serialVersionUID = 1L;

    /**
     * @brief Constructor with message
     * @param message Error message
     */
    public BusinessException(String message) {
        super(message);
    }

    /**
     * @brief Constructor with message and cause
     * @param message Error message
     * @param cause The cause exception
     */
    public BusinessException(String message, Throwable cause) {
        super(message, cause);
    }

}
