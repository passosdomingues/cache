package controller;

import com.bluevelvet.domain.dto.CategoryDTO;
import com.bluevelvet.service.CategoryService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

/**
 * @brief MVC Controller for Category web pages
 * @details Handles Thymeleaf template rendering for category management
 * Provides user interface for browsing and managing categories
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@Controller
@RequestMapping("/categories")
@RequiredArgsConstructor
@Slf4j
public class CategoryController {

    private final CategoryService categoryService;
    private static final int DEFAULT_PAGE_SIZE = 12;

    /**
     * @brief Display categories listing page
     * @param page The page number
     * @param sortBy The sort field
     * @param sortDirection The sort direction
     * @param searchTerm The search term
     * @param model The model
     * @return The template name
     */
    @GetMapping
    public String listCategories(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "name") String sortBy,
            @RequestParam(defaultValue = "ASC") String sortDirection,
            @RequestParam(required = false) String searchTerm,
            Model model) {
        
        log.debug("Listing categories - page: {}, sortBy: {}, searchTerm: {}", page, sortBy, searchTerm);
        
        Sort.Direction direction = Sort.Direction.fromString(sortDirection);
        Pageable pageable = PageRequest.of(page, DEFAULT_PAGE_SIZE, Sort.by(direction, sortBy));
        
        Page<CategoryDTO> categories;
        if (searchTerm != null && !searchTerm.isEmpty()) {
            categories = categoryService.searchCategoriesByName(searchTerm, pageable);
            model.addAttribute("searchTerm", searchTerm);
        } else {
            categories = categoryService.getAllRootCategoriesPaginated(pageable);
        }
        
        model.addAttribute("categories", categories);
        model.addAttribute("currentPage", page);
        model.addAttribute("sortBy", sortBy);
        model.addAttribute("sortDirection", sortDirection);
        model.addAttribute("totalPages", categories.getTotalPages());
        model.addAttribute("totalElements", categories.getTotalElements());
        
        return "categories/list";
    }

    /**
     * @brief Display category detail page
     * @param id The category ID
     * @param model The model
     * @return The template name
     */
    @GetMapping("/{id}")
    public String viewCategory(
            @PathVariable Long id,
            Model model) {
        
        log.debug("Viewing category with ID: {}", id);
        
        CategoryDTO category = categoryService.getCategoryById(id);
        model.addAttribute("category", category);
        
        // Get subcategories if this is a root category
        if (category.getParentId() == null) {
            Page<CategoryDTO> subcategories = categoryService.getSubcategoriesByParentIdPaginated(
                id, 
                PageRequest.of(0, 12, Sort.by("displayOrder"))
            );
            model.addAttribute("subcategories", subcategories.getContent());
        }
        
        return "categories/detail";
    }

    /**
     * @brief Display category creation form (admin only)
     * @param model The model
     * @return The template name
     */
    @GetMapping("/new")
    @PreAuthorize("hasRole('ADMIN')")
    public String showCreateForm(Model model) {
        log.debug("Displaying category creation form");
        
        model.addAttribute("category", new CategoryDTO());
        model.addAttribute("rootCategories", categoryService.getAllRootCategories());
        
        return "categories/form";
    }

    /**
     * @brief Display category edit form (admin only)
     * @param id The category ID
     * @param model The model
     * @return The template name
     */
    @GetMapping("/{id}/edit")
    @PreAuthorize("hasRole('ADMIN')")
    public String showEditForm(
            @PathVariable Long id,
            Model model) {
        
        log.debug("Displaying category edit form for ID: {}", id);
        
        CategoryDTO category = categoryService.getCategoryById(id);
        model.addAttribute("category", category);
        model.addAttribute("rootCategories", categoryService.getAllRootCategories());
        
        return "categories/form";
    }

    /**
     * @brief Save a category (create or update)
     * @param categoryDTO The category data
     * @return Redirect to category list
     */
    @PostMapping("/save")
    @PreAuthorize("hasRole('ADMIN')")
    public String saveCategory(@ModelAttribute CategoryDTO categoryDTO) {
        log.info("Saving category: {}", categoryDTO.getName());
        
        if (categoryDTO.getId() != null) {
            categoryService.updateCategory(categoryDTO.getId(), categoryDTO);
        } else {
            categoryService.createCategory(categoryDTO);
        }
        
        return "redirect:/categories";
    }

    /**
     * @brief Delete a category (admin only)
     * @param id The category ID
     * @return Redirect to category list
     */
    @PostMapping("/{id}/delete")
    @PreAuthorize("hasRole('ADMIN')")
    public String deleteCategory(@PathVariable Long id) {
        log.info("Deleting category with ID: {}", id);
        categoryService.deleteCategory(id);
        return "redirect:/categories";
    }

}
