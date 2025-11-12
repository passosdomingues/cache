package security;

import com.bluevelvet.service.UserService;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.security.web.authentication.SimpleUrlAuthenticationSuccessHandler;
import org.springframework.stereotype.Component;

import java.io.IOException;

/**
 * @brief OAuth2 authentication success handler
 * @details Handles successful OAuth2 authentication and user creation/update
 * Redirects to dashboard after successful login
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class OAuth2AuthenticationSuccessHandler extends SimpleUrlAuthenticationSuccessHandler {

    private final UserService userService;

    /**
     * @brief Handle successful OAuth2 authentication
     * @param request The HTTP request
     * @param response The HTTP response
     * @param authentication The authentication object
     * @throws IOException if an I/O error occurs
     * @throws ServletException if a servlet error occurs
     */
    @Override
    public void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response,
                                        Authentication authentication) throws IOException, ServletException {
        
        log.info("OAuth2 authentication successful");
        
        OAuth2User oAuth2User = (OAuth2User) authentication.getPrincipal();
        
        // Extract user information from OAuth2 provider
        String email = oAuth2User.getAttribute("email");
        String name = oAuth2User.getAttribute("name");
        String picture = oAuth2User.getAttribute("picture");
        String providerId = oAuth2User.getName();
        
        log.debug("Processing OAuth2 user: email={}, provider={}", email, "google");
        
        try {
            // Get or create user
            userService.getOrCreateOAuthUser(email, name, picture, "google", providerId);
            
            // Update last login
            userService.getUserByEmail(email);
            
            log.info("User authenticated successfully: {}", email);
        } catch (Exception e) {
            log.error("Error processing OAuth2 user", e);
            throw new ServletException("Error processing OAuth2 authentication", e);
        }
        
        // Redirect to dashboard
        setDefaultTargetUrl("/dashboard");
        super.onAuthenticationSuccess(request, response, authentication);
    }

}
