/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Repository interface for category data access operations
 * @us US-1306 Create category of products - Granularity: Data Access
 * @us US-0904 Delete category of products - Granularity: Data Access
 * @us US-1307 Edit category of products - Granularity: Data Access
 * @us US-2100 List products within a category - Granularity: Data Access
 */
package com.bluevelvet.repository;

import com.bluevelvet.entity.Category;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * @brief Provides data access methods for category entity with custom queries
 */
@Repository
public interface CategoryRepository extends JpaRepository<Category, Long> {

    /**
     * @brief Finds a category by its exact name
     * @param categoryName The name of the category to search for
     * @return Optional containing the category if found
     */
    Optional<Category> findByName(String categoryName);

    /**
     * @brief Checks if a category exists with the specified name
     * @param categoryName The name to check for existence
     * @return Boolean indicating if category with given name exists
     */
    boolean existsByName(String categoryName);

    /**
     * @brief Finds all categories that are enabled
     * @return List of enabled categories
     */
    List<Category> findByEnabledTrue();

    /**
     * @brief Finds all categories that have no parent (root categories)
     * @return List of root categories
     */
    List<Category> findByParentIsNull();

    /**
     * @brief Finds all categories that have no parent (root categories) with
     *        pagination
     * @param pageable Pagination info
     * @return Page of root categories
     */
    Page<Category> findByParentIsNull(Pageable pageable);

    /**
     * @brief Finds all subcategories of a specific parent category
     * @param parentCategory The parent category to find children for
     * @return List of child categories
     */
    List<Category> findByParent(Category parentCategory);

    /**
     * @brief Custom query to find categories by enabled status and name pattern
     * @param categoryEnabled     The enabled status to filter by
     * @param categoryNamePattern The name pattern to search for (using LIKE)
     * @return List of categories matching the criteria
     */
    @Query("SELECT c FROM Category c WHERE c.enabled = :categoryEnabled AND c.name LIKE %:categoryNamePattern%")
    List<Category> findByEnabledAndNameContaining(@Param("categoryEnabled") Boolean categoryEnabled,
            @Param("categoryNamePattern") String categoryNamePattern);
}
