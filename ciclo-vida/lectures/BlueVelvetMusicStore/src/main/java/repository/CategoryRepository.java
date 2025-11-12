package repository;

import com.bluevelvet.domain.entity.CategoryEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * @brief Repository interface for CategoryEntity
 * @details Provides database access operations for categories
 * Extends JpaRepository for CRUD operations and custom queries
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@Repository
public interface CategoryRepository extends JpaRepository<CategoryEntity, Long> {

    /**
     * @brief Find a category by name
     * @param name The category name
     * @return Optional containing the category if found
     */
    Optional<CategoryEntity> findByName(String name);

    /**
     * @brief Find all root categories (without parent)
     * @return List of root categories
     */
    @Query("SELECT c FROM CategoryEntity c WHERE c.parentCategory IS NULL AND c.isActive = true ORDER BY c.displayOrder ASC, c.name ASC")
    List<CategoryEntity> findAllRootCategories();

    /**
     * @brief Find all root categories with pagination
     * @param pageable Pagination information
     * @return Page of root categories
     */
    @Query("SELECT c FROM CategoryEntity c WHERE c.parentCategory IS NULL AND c.isActive = true ORDER BY c.displayOrder ASC, c.name ASC")
    Page<CategoryEntity> findAllRootCategoriesPaginated(Pageable pageable);

    /**
     * @brief Find subcategories of a parent category
     * @param parentId The parent category ID
     * @return List of subcategories
     */
    @Query("SELECT c FROM CategoryEntity c WHERE c.parentCategory.id = :parentId AND c.isActive = true ORDER BY c.displayOrder ASC, c.name ASC")
    List<CategoryEntity> findSubcategoriesByParentId(@Param("parentId") Long parentId);

    /**
     * @brief Find subcategories of a parent category with pagination
     * @param parentId The parent category ID
     * @param pageable Pagination information
     * @return Page of subcategories
     */
    @Query("SELECT c FROM CategoryEntity c WHERE c.parentCategory.id = :parentId AND c.isActive = true ORDER BY c.displayOrder ASC, c.name ASC")
    Page<CategoryEntity> findSubcategoriesByParentIdPaginated(@Param("parentId") Long parentId, Pageable pageable);

    /**
     * @brief Search categories by name (case-insensitive)
     * @param searchTerm The search term
     * @param pageable Pagination information
     * @return Page of matching categories
     */
    @Query("SELECT c FROM CategoryEntity c WHERE LOWER(c.name) LIKE LOWER(CONCAT('%', :searchTerm, '%')) AND c.isActive = true ORDER BY c.name ASC")
    Page<CategoryEntity> searchByName(@Param("searchTerm") String searchTerm, Pageable pageable);

    /**
     * @brief Find all active categories
     * @return List of active categories
     */
    @Query("SELECT c FROM CategoryEntity c WHERE c.isActive = true ORDER BY c.displayOrder ASC, c.name ASC")
    List<CategoryEntity> findAllActive();

    /**
     * @brief Find all active categories with pagination
     * @param pageable Pagination information
     * @return Page of active categories
     */
    @Query("SELECT c FROM CategoryEntity c WHERE c.isActive = true ORDER BY c.displayOrder ASC, c.name ASC")
    Page<CategoryEntity> findAllActivePaginated(Pageable pageable);

    /**
     * @brief Check if a category name already exists (excluding a specific ID)
     * @param name The category name
     * @param excludeId The ID to exclude from the check
     * @return true if the name exists, false otherwise
     */
    @Query("SELECT COUNT(c) > 0 FROM CategoryEntity c WHERE c.name = :name AND c.id != :excludeId")
    boolean existsByNameExcluding(@Param("name") String name, @Param("excludeId") Long excludeId);

    /**
     * @brief Count all active categories
     * @return The count of active categories
     */
    @Query("SELECT COUNT(c) FROM CategoryEntity c WHERE c.isActive = true")
    long countActive();

}
