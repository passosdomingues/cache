/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Service class for product-related operations.
 * @us US-2100 List products within a category - Granularity: Business Logic
 */
package com.bluevelvet.service;

import com.bluevelvet.entity.Category;
import com.bluevelvet.entity.Product;
import com.bluevelvet.repository.CategoryRepository;
import com.bluevelvet.repository.ProductRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * @brief Service for managing products.
 */
@Service
@RequiredArgsConstructor
public class ProductService {

    private final ProductRepository productRepository;
    private final CategoryRepository categoryRepository;

    /**
     * @brief Lists products by category with pagination.
     * @param categoryId The ID of the category.
     * @param pageable   Pagination information.
     * @return A Page of products.
     * @throws EntityNotFoundException if the category is not found.
     */
    @Transactional(readOnly = true)
    public Page<Product> listProductsByCategory(Long categoryId, Pageable pageable) {
        if (categoryId == null) {
            throw new IllegalArgumentException("Category ID must not be null");
        }
        Category category = categoryRepository.findById(categoryId)
                .orElseThrow(() -> new EntityNotFoundException("Category not found with id: " + categoryId));

        return productRepository.findByCategoryAndEnabledTrue(category, pageable);
    }
}
