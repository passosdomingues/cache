/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Repository interface for Product entity.
 * @us US-2100 List products within a category - Granularity: Data Access
 */
package com.bluevelvet.repository;

import com.bluevelvet.entity.Category;
import com.bluevelvet.entity.Product;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * @brief Repository for accessing Product data.
 */
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    /**
     * @brief Finds enabled products by category with pagination.
     * @param category The category to filter by.
     * @param pageable Pagination information.
     * @return A Page of enabled products in the specified category.
     */
    Page<Product> findByCategoryAndEnabledTrue(Category category, Pageable pageable);

    /**
     * @brief Finds enabled and in-stock products with pagination.
     * @param pageable Pagination information.
     * @return A Page of enabled and in-stock products.
     */
    Page<Product> findByEnabledTrueAndInStockTrue(Pageable pageable);

    /**
     * @brief Searches products by name (case-insensitive) with pagination.
     * @param name     The name to search for.
     * @param pageable Pagination information.
     * @return A Page of products matching the name.
     */
    Page<Product> findByNameContainingIgnoreCase(String name, Pageable pageable);
}
