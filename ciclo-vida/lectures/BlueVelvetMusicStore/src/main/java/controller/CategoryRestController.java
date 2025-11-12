package controller;

import com.bluevelvet.domain.dto.CategoryDTO;
import com.bluevelvet.service.CategoryService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * @brief REST API Controller for Category management
 * @details Provides RESTful endpoints for CRUD operations on categories
 * Implements proper HTTP methods and status codes
 * Secured with Spring Security and OAuth2
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@RestController
@RequestMapping("/api/v1/categories")
@RequiredArgsConstructor
@Slf4j
@Tag(name = "Categories", description = "Category management endpoints")
@SecurityRequirement(name = "oauth2")
public class CategoryRestController {

    private final CategoryService categoryService;

    /**
     * @brief Create a new category
     * @param categoryDTO The category data
     * @return ResponseEntity with the created category
     */
    @PostMapping
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Create a new category", description = "Creates a new product category")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "201", description = "Category created successfully"),
        @ApiResponse(responseCode = "400", description = "Invalid input"),
        @ApiResponse(responseCode = "409", description = "Category name already exists")
    })
    public ResponseEntity<CategoryDTO> createCategory(@Valid @RequestBody CategoryDTO categoryDTO) {
        log.info("Creating new category: {}", categoryDTO.getName());
        CategoryDTO createdCategory = categoryService.createCategory(categoryDTO);
        return ResponseEntity.status(HttpStatus.CREATED).body(createdCategory);
    }

    /**
     * @brief Update an existing category
     * @param id The category ID
     * @param categoryDTO The updated category data
     * @return ResponseEntity with the updated category
     */
    @PutMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Update a category", description = "Updates an existing product category")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Category updated successfully"),
        @ApiResponse(responseCode = "404", description = "Category not found"),
        @ApiResponse(responseCode = "409", description = "Category name already exists")
    })
    public ResponseEntity<CategoryDTO> updateCategory(
            @Parameter(description = "Category ID") @PathVariable Long id,
            @Valid @RequestBody CategoryDTO categoryDTO) {
        log.info("Updating category with ID: {}", id);
        CategoryDTO updatedCategory = categoryService.updateCategory(id, categoryDTO);
        return ResponseEntity.ok(updatedCategory);
    }

    /**
     * @brief Get a category by ID
     * @param id The category ID
     * @return ResponseEntity with the category
     */
    @GetMapping("/{id}")
    @Operation(summary = "Get a category by ID", description = "Retrieves a specific category by its ID")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Category found"),
        @ApiResponse(responseCode = "404", description = "Category not found")
    })
    public ResponseEntity<CategoryDTO> getCategoryById(
            @Parameter(description = "Category ID") @PathVariable Long id) {
        log.debug("Fetching category with ID: {}", id);
        CategoryDTO category = categoryService.getCategoryById(id);
        return ResponseEntity.ok(category);
    }

    /**
     * @brief Get all root categories
     * @return ResponseEntity with list of root categories
     */
    @GetMapping("/root/all")
    @Operation(summary = "Get all root categories", description = "Retrieves all root categories (without parent)")
    @ApiResponse(responseCode = "200", description = "Root categories retrieved successfully")
    public ResponseEntity<List<CategoryDTO>> getAllRootCategories() {
        log.debug("Fetching all root categories");
        List<CategoryDTO> categories = categoryService.getAllRootCategories();
        return ResponseEntity.ok(categories);
    }

    /**
     * @brief Get all root categories with pagination
     * @param pageable Pagination information
     * @return ResponseEntity with paginated root categories
     */
    @GetMapping("/root")
    @Operation(summary = "Get root categories with pagination", description = "Retrieves root categories with pagination support")
    @ApiResponse(responseCode = "200", description = "Root categories retrieved successfully")
    public ResponseEntity<Page<CategoryDTO>> getAllRootCategoriesPaginated(
            @PageableDefault(size = 20, page = 0, sort = "displayOrder", direction = Sort.Direction.ASC) Pageable pageable) {
        log.debug("Fetching root categories with pagination: {}", pageable);
        Page<CategoryDTO> categories = categoryService.getAllRootCategoriesPaginated(pageable);
        return ResponseEntity.ok(categories);
    }

    /**
     * @brief Get subcategories of a parent category
     * @param parentId The parent category ID
     * @return ResponseEntity with list of subcategories
     */
    @GetMapping("/{parentId}/subcategories/all")
    @Operation(summary = "Get subcategories", description = "Retrieves all subcategories of a parent category")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Subcategories retrieved successfully"),
        @ApiResponse(responseCode = "404", description = "Parent category not found")
    })
    public ResponseEntity<List<CategoryDTO>> getSubcategoriesByParentId(
            @Parameter(description = "Parent Category ID") @PathVariable Long parentId) {
        log.debug("Fetching subcategories for parent ID: {}", parentId);
        List<CategoryDTO> subcategories = categoryService.getSubcategoriesByParentId(parentId);
        return ResponseEntity.ok(subcategories);
    }

    /**
     * @brief Get subcategories with pagination
     * @param parentId The parent category ID
     * @param pageable Pagination information
     * @return ResponseEntity with paginated subcategories
     */
    @GetMapping("/{parentId}/subcategories")
    @Operation(summary = "Get subcategories with pagination", description = "Retrieves subcategories with pagination support")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Subcategories retrieved successfully"),
        @ApiResponse(responseCode = "404", description = "Parent category not found")
    })
    public ResponseEntity<Page<CategoryDTO>> getSubcategoriesByParentIdPaginated(
            @Parameter(description = "Parent Category ID") @PathVariable Long parentId,
            @PageableDefault(size = 20, page = 0, sort = "displayOrder", direction = Sort.Direction.ASC) Pageable pageable) {
        log.debug("Fetching subcategories for parent ID: {} with pagination: {}", parentId, pageable);
        Page<CategoryDTO> subcategories = categoryService.getSubcategoriesByParentIdPaginated(parentId, pageable);
        return ResponseEntity.ok(subcategories);
    }

    /**
     * @brief Search categories by name
     * @param searchTerm The search term
     * @param pageable Pagination information
     * @return ResponseEntity with search results
     */
    @GetMapping("/search")
    @Operation(summary = "Search categories", description = "Searches categories by name")
    @ApiResponse(responseCode = "200", description = "Search completed successfully")
    public ResponseEntity<Page<CategoryDTO>> searchCategoriesByName(
            @Parameter(description = "Search term") @RequestParam String searchTerm,
            @PageableDefault(size = 20, page = 0, sort = "name", direction = Sort.Direction.ASC) Pageable pageable) {
        log.debug("Searching categories with term: {}", searchTerm);
        Page<CategoryDTO> results = categoryService.searchCategoriesByName(searchTerm, pageable);
        return ResponseEntity.ok(results);
    }

    /**
     * @brief Delete a category
     * @param id The category ID
     * @return ResponseEntity with no content
     */
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Delete a category", description = "Deletes a category (soft delete)")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "204", description = "Category deleted successfully"),
        @ApiResponse(responseCode = "404", description = "Category not found")
    })
    public ResponseEntity<Void> deleteCategory(
            @Parameter(description = "Category ID") @PathVariable Long id) {
        log.info("Deleting category with ID: {}", id);
        categoryService.deleteCategory(id);
        return ResponseEntity.noContent().build();
    }

    /**
     * @brief Activate a category
     * @param id The category ID
     * @return ResponseEntity with the activated category
     */
    @PatchMapping("/{id}/activate")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Activate a category", description = "Activates a deactivated category")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Category activated successfully"),
        @ApiResponse(responseCode = "404", description = "Category not found")
    })
    public ResponseEntity<CategoryDTO> activateCategory(
            @Parameter(description = "Category ID") @PathVariable Long id) {
        log.info("Activating category with ID: {}", id);
        CategoryDTO activatedCategory = categoryService.activateCategory(id);
        return ResponseEntity.ok(activatedCategory);
    }

    /**
     * @brief Deactivate a category
     * @param id The category ID
     * @return ResponseEntity with the deactivated category
     */
    @PatchMapping("/{id}/deactivate")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Deactivate a category", description = "Deactivates an active category")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Category deactivated successfully"),
        @ApiResponse(responseCode = "404", description = "Category not found")
    })
    public ResponseEntity<CategoryDTO> deactivateCategory(
            @Parameter(description = "Category ID") @PathVariable Long id) {
        log.info("Deactivating category with ID: {}", id);
        CategoryDTO deactivatedCategory = categoryService.deactivateCategory(id);
        return ResponseEntity.ok(deactivatedCategory);
    }

    /**
     * @brief Get the count of active categories
     * @return ResponseEntity with the count
     */
    @GetMapping("/stats/active-count")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Get active categories count", description = "Retrieves the total count of active categories")
    @ApiResponse(responseCode = "200", description = "Count retrieved successfully")
    public ResponseEntity<Long> getActiveCategoriesCount() {
        log.debug("Fetching active categories count");
        long count = categoryService.getActiveCategoriesCount();
        return ResponseEntity.ok(count);
    }

}
