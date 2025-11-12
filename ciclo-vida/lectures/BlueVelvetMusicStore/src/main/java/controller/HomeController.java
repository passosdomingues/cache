package controller;

import com.bluevelvet.service.CategoryService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;

/**
 * @brief MVC Controller for home and dashboard pages
 * @details Handles rendering of home page and user dashboard
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@Controller
@RequestMapping("/")
@RequiredArgsConstructor
@Slf4j
public class HomeController {

    private final CategoryService categoryService;

    /**
     * @brief Display home page
     * @param authentication The authentication object
     * @param model The model
     * @return The template name
     */
    @GetMapping
    public String home(Authentication authentication, Model model) {
        log.debug("Displaying home page");
        
        model.addAttribute("isAuthenticated", authentication != null && authentication.isAuthenticated());
        
        if (authentication != null && authentication.isAuthenticated()) {
            model.addAttribute("username", authentication.getName());
        }
        
        // Add featured categories
        model.addAttribute("featuredCategories", categoryService.getAllRootCategories());
        
        return "index";
    }

    /**
     * @brief Display dashboard (authenticated users only)
     * @param authentication The authentication object
     * @param model The model
     * @return The template name
     */
    @GetMapping("/dashboard")
    public String dashboard(Authentication authentication, Model model) {
        log.debug("Displaying dashboard for user: {}", authentication.getName());
        
        model.addAttribute("username", authentication.getName());
        model.addAttribute("activeCategoriesCount", categoryService.getActiveCategoriesCount());
        model.addAttribute("rootCategories", categoryService.getAllRootCategories());
        
        return "dashboard";
    }

    /**
     * @brief Display login page
     * @return The template name
     */
    @GetMapping("/login")
    public String login() {
        log.debug("Displaying login page");
        return "login";
    }

}
