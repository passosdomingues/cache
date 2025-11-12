package security;

import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationFailureHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

/**
 * @brief OAuth2 authentication failure handler
 * @details Handles failed OAuth2 authentication attempts
 * Redirects to login page with error message
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@Component
@Slf4j
public class OAuth2AuthenticationFailureHandler extends SimpleUrlAuthenticationFailureHandler {

    /**
     * @brief Handle failed OAuth2 authentication
     * @param request The HTTP request
     * @param response The HTTP response
     * @param exception The authentication exception
     * @throws IOException if an I/O error occurs
     * @throws ServletException if a servlet error occurs
     */
    @Override
    public void onAuthenticationFailure(HttpServletRequest request, HttpServletResponse response,
                                        AuthenticationException exception) throws IOException, ServletException {
        
        log.warn("OAuth2 authentication failed: {}", exception.getMessage());
        
        String errorMessage = URLEncoder.encode(
            "Authentication failed. Please try again.",
            StandardCharsets.UTF_8
        );
        
        setDefaultFailureUrl("/login?error=" + errorMessage);
        super.onAuthenticationFailure(request, response, exception);
    }

}
