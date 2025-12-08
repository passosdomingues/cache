/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025-12-08
 * @brief REST controller for category management operations
 * @us US-1306 Create category of products - Granularity: API Endpoint
 * @us US-0907 List categories of products - Granularity: API Endpoint
 * @us US-1307 Edit category of products - Granularity: API Endpoint
 * @us US-0904 Delete category of products - Granularity: API Endpoint
 */
package com.bluevelvet.category;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import com.bluevelvet.payload.response.MessageResponse;

import java.util.List;
import java.util.Optional;

/**
 * @brief Provides endpoints for category CRUD operations and hierarchical
 *        management
 */
@CrossOrigin(origins = "*", maxAge = 3600)
@RestController
@RequestMapping("/api/categories")
public class CategoryController {

    private final CategoryService categoryService;

    /**
     * @brief Constructor for dependency injection of category service
     * @param injectedCategoryService The category service to be injected
     */
    @Autowired
    public CategoryController(CategoryService injectedCategoryService) {
        this.categoryService = injectedCategoryService;
    }

    /**
     * @brief Retrieves all categories (public endpoint)
     * @return ResponseEntity containing list of all categories or error message
     */
    @GetMapping("/public")
    public ResponseEntity<?> getAllCategories() {
        try {
            List<Category> categories = categoryService.getAllCategories();
            return ResponseEntity.ok(categories);
        } catch (Exception exception) {
            return ResponseEntity.badRequest()
                    .body(new MessageResponse("Error retrieving categories: " + exception.getMessage()));
        }
    }

    /**
     * @brief Retrieves only enabled categories (public endpoint)
     * @return ResponseEntity containing list of enabled categories or error message
     */
    @GetMapping("/public/enabled")
    public ResponseEntity<?> getEnabledCategories() {
        try {
            List<Category> categories = categoryService.getEnabledCategories();
            return ResponseEntity.ok(categories);
        } catch (Exception exception) {
            return ResponseEntity.badRequest()
                    .body(new MessageResponse("Error retrieving enabled categories: " + exception.getMessage()));
        }
    }

    /**
     * @brief Retrieves root categories (categories with no parent)
     * @return ResponseEntity containing list of root categories or error message
     */
    @GetMapping("/public/roots")
    public ResponseEntity<?> getRootCategories() {
        try {
            List<Category> categories = categoryService.getRootCategories();
            return ResponseEntity.ok(categories);
        } catch (Exception exception) {
            return ResponseEntity.badRequest()
                    .body(new MessageResponse("Error retrieving root categories: " + exception.getMessage()));
        }
    }

    /**
     * @brief Retrieves a specific category by ID
     * @param categoryId The ID of the category to retrieve
     * @return ResponseEntity containing the category or error message
     */
    @GetMapping("/public/{categoryId}")
    public ResponseEntity<?> getCategoryById(@PathVariable Long categoryId) {
        try {
            Optional<Category> category = categoryService.getCategoryById(categoryId);
            if (category.isPresent()) {
                return ResponseEntity.ok(category.get());
            } else {
                return ResponseEntity.badRequest()
                        .body(new MessageResponse("Error: Category not found with ID: " + categoryId));
            }
        } catch (Exception exception) {
            return ResponseEntity.badRequest()
                    .body(new MessageResponse("Error retrieving category: " + exception.getMessage()));
        }
    }

    /**
     * @brief Retrieves subcategories of a specific parent category
     * @param parentCategoryId The ID of the parent category
     * @return ResponseEntity containing list of subcategories or error message
     */
    @GetMapping("/public/{parentCategoryId}/subcategories")
    public ResponseEntity<?> getSubcategories(@PathVariable Long parentCategoryId) {
        try {
            List<Category> subcategories = categoryService.getSubcategoriesByParentId(parentCategoryId);
            return ResponseEntity.ok(subcategories);
        } catch (Exception exception) {
            return ResponseEntity.badRequest()
                    .body(new MessageResponse("Error retrieving subcategories: " + exception.getMessage()));
        }
    }

    /**
     * @brief Creates a new category (admin only)
     * @param category The category object to create
     * @return ResponseEntity with success message or error
     */
    @PostMapping
    @PreAuthorize("hasRole('ADMINISTRATOR')")
    public ResponseEntity<?> createCategory(@RequestBody Category category) {
        try {
            if (categoryService.categoryExists(category.getName())) {
                return ResponseEntity.badRequest()
                        .body(new MessageResponse("Error: Category name already exists"));
            }

            Category savedCategory = categoryService.saveCategory(category);
            return ResponseEntity.ok(savedCategory);
        } catch (Exception exception) {
            return ResponseEntity.badRequest()
                    .body(new MessageResponse("Error creating category: " + exception.getMessage()));
        }
    }

    /**
     * @brief Updates an existing category (admin only)
     * @param categoryId The ID of the category to update
     * @param category   The updated category data
     * @return ResponseEntity with updated category or error message
     */
    @PutMapping("/{categoryId}")
    @PreAuthorize("hasRole('ADMINISTRATOR')")
    public ResponseEntity<?> updateCategory(@PathVariable Long categoryId, @RequestBody Category category) {
        try {
            if (!categoryService.getCategoryById(categoryId).isPresent()) {
                return ResponseEntity.badRequest()
                        .body(new MessageResponse("Error: Category not found with ID: " + categoryId));
            }

            category.setId(categoryId);
            Category updatedCategory = categoryService.saveCategory(category);
            return ResponseEntity.ok(updatedCategory);
        } catch (Exception exception) {
            return ResponseEntity.badRequest()
                    .body(new MessageResponse("Error updating category: " + exception.getMessage()));
        }
    }

    /**
     * @brief Deletes a category (admin only)
     * @param categoryId The ID of the category to delete
     * @return ResponseEntity with success message or error
     */
    @DeleteMapping("/{categoryId}")
    @PreAuthorize("hasRole('ADMINISTRATOR')")
    public ResponseEntity<?> deleteCategory(@PathVariable Long categoryId) {
        try {
            categoryService.deleteCategory(categoryId);
            return ResponseEntity.ok(new MessageResponse("Category deleted successfully"));
        } catch (Exception exception) {
            return ResponseEntity.badRequest()
                    .body(new MessageResponse("Error deleting category: " + exception.getMessage()));
        }
    }

    /**
     * @brief Toggles the enabled status of a category (admin only)
     * @param categoryId The ID of the category to toggle
     * @return ResponseEntity with new status or error message
     */
    @PatchMapping("/{categoryId}/toggle")
    @PreAuthorize("hasRole('ADMINISTRATOR')")
    public ResponseEntity<?> toggleCategoryStatus(@PathVariable Long categoryId) {
        try {
            Boolean newStatus = categoryService.toggleCategoryStatus(categoryId);
            if (newStatus != null) {
                return ResponseEntity.ok(new MessageResponse("Category status updated to: " + newStatus));
            } else {
                return ResponseEntity.badRequest()
                        .body(new MessageResponse("Error: Category not found with ID: " + categoryId));
            }
        } catch (Exception exception) {
            return ResponseEntity.badRequest()
                    .body(new MessageResponse("Error toggling category status: " + exception.getMessage()));
        }
    }
}
