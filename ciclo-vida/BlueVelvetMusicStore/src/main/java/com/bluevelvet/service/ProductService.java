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
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

/**
 * @brief Service for managing products.
 */
@Service
@RequiredArgsConstructor
public class ProductService {

    private final ProductRepository productRepository;
    private final CategoryRepository categoryRepository;

    /**
     * @brief Get all products with pagination.
     * @param pageable Pagination information.
     * @return A Page of products.
     */
    @Transactional(readOnly = true)
    public Page<Product> findAll(Pageable pageable) {
        return productRepository.findAll(pageable);
    }

    /**
     * @brief Get featured products (first 8 enabled and in-stock products).
     * @return A list of featured products.
     */
    @Transactional(readOnly = true)
    public List<Product> findFeaturedProducts() {
        Pageable pageable = PageRequest.of(0, 8);
        return productRepository.findByEnabledTrueAndInStockTrue(pageable).getContent();
    }

    /**
     * @brief Find product by ID.
     * @param id The product ID.
     * @return The product.
     * @throws EntityNotFoundException if product not found.
     */
    @Transactional(readOnly = true)
    public Product findById(Long id) {
        return productRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Product not found with id: " + id));
    }

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

    /**
     * @brief Search products by name.
     * @param query    The search query.
     * @param pageable Pagination information.
     * @return A Page of products.
     */
    @Transactional(readOnly = true)
    public Page<Product> searchByName(String query, Pageable pageable) {
        return productRepository.findByNameContainingIgnoreCase(query, pageable);
    }

    /**
     * @brief Save a product (create or update).
     * @param product The product to save.
     * @return The saved product.
     */
    @Transactional
    public Product save(Product product) {
        if (product.getId() == null) {
            product.setCreatedTime(LocalDateTime.now());
        }
        product.setUpdatedTime(LocalDateTime.now());
        return productRepository.save(product);
    }

    /**
     * @brief Delete a product by ID.
     * @param id The product ID.
     */
    @Transactional
    public void deleteById(Long id) {
        if (!productRepository.existsById(id)) {
            throw new EntityNotFoundException("Product not found with id: " + id);
        }
        productRepository.deleteById(id);
    }
}
