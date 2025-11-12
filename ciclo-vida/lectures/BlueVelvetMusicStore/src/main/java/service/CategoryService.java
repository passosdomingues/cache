package service;

import com.bluevelvet.domain.dto.CategoryDTO;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;

/**
 * @brief Service interface for category operations
 * @details Defines the contract for category business logic
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
public interface CategoryService {

    /**
     * @brief Create a new category
     * @param categoryDTO The category data
     * @return The created category DTO
     * @throws com.bluevelvet.exception.DuplicateResourceException if category name already exists
     */
    CategoryDTO createCategory(CategoryDTO categoryDTO);

    /**
     * @brief Update an existing category
     * @param id The category ID
     * @param categoryDTO The updated category data
     * @return The updated category DTO
     * @throws com.bluevelvet.exception.ResourceNotFoundException if category not found
     * @throws com.bluevelvet.exception.DuplicateResourceException if new name already exists
     */
    CategoryDTO updateCategory(Long id, CategoryDTO categoryDTO);

    /**
     * @brief Get a category by ID
     * @param id The category ID
     * @return The category DTO
     * @throws com.bluevelvet.exception.ResourceNotFoundException if category not found
     */
    CategoryDTO getCategoryById(Long id);

    /**
     * @brief Get all root categories
     * @return List of root category DTOs
     */
    List<CategoryDTO> getAllRootCategories();

    /**
     * @brief Get all root categories with pagination
     * @param pageable Pagination information
     * @return Page of root category DTOs
     */
    Page<CategoryDTO> getAllRootCategoriesPaginated(Pageable pageable);

    /**
     * @brief Get subcategories of a parent category
     * @param parentId The parent category ID
     * @return List of subcategory DTOs
     * @throws com.bluevelvet.exception.ResourceNotFoundException if parent category not found
     */
    List<CategoryDTO> getSubcategoriesByParentId(Long parentId);

    /**
     * @brief Get subcategories of a parent category with pagination
     * @param parentId The parent category ID
     * @param pageable Pagination information
     * @return Page of subcategory DTOs
     * @throws com.bluevelvet.exception.ResourceNotFoundException if parent category not found
     */
    Page<CategoryDTO> getSubcategoriesByParentIdPaginated(Long parentId, Pageable pageable);

    /**
     * @brief Search categories by name
     * @param searchTerm The search term
     * @param pageable Pagination information
     * @return Page of matching category DTOs
     */
    Page<CategoryDTO> searchCategoriesByName(String searchTerm, Pageable pageable);

    /**
     * @brief Delete a category (soft delete)
     * @param id The category ID
     * @throws com.bluevelvet.exception.ResourceNotFoundException if category not found
     */
    void deleteCategory(Long id);

    /**
     * @brief Activate a category
     * @param id The category ID
     * @return The activated category DTO
     * @throws com.bluevelvet.exception.ResourceNotFoundException if category not found
     */
    CategoryDTO activateCategory(Long id);

    /**
     * @brief Deactivate a category
     * @param id The category ID
     * @return The deactivated category DTO
     * @throws com.bluevelvet.exception.ResourceNotFoundException if category not found
     */
    CategoryDTO deactivateCategory(Long id);

    /**
     * @brief Get the total count of active categories
     * @return The count of active categories
     */
    long getActiveCategoriesCount();

}
