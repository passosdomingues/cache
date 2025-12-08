/**
 * @brief Repository interface for Product entity.
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 November 30
 */
package com.bluevelvet.product;

import com.bluevelvet.category.Category;
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
}
