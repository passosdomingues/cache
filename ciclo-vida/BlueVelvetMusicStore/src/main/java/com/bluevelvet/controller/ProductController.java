/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief REST controller for product management operations.
 * @us US-2100 List products within a category - Granularity: API Endpoint
 */
package com.bluevelvet.controller;

import com.bluevelvet.entity.Product;
import com.bluevelvet.service.ProductService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * @brief Controller for handling product-related requests.
 */
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class ProductController {

    private final ProductService productService;

    /**
     * @brief Get all products with pagination.
     * @param pageable Pagination information.
     * @return A ResponseEntity containing a page of products.
     */
    @GetMapping("/products")
    public ResponseEntity<Page<Product>> getAllProducts(
            @PageableDefault(sort = "name", direction = Sort.Direction.ASC, size = 20) Pageable pageable) {
        Page<Product> products = productService.findAll(pageable);
        return ResponseEntity.ok(products);
    }

    /**
     * @brief Get featured products (first 8 enabled products).
     * @return A ResponseEntity containing a list of featured products.
     */
    @GetMapping("/products/featured")
    public ResponseEntity<List<Product>> getFeaturedProducts() {
        List<Product> products = productService.findFeaturedProducts();
        return ResponseEntity.ok(products);
    }

    /**
     * @brief Get product by ID.
     * @param id The product ID.
     * @return A ResponseEntity containing the product.
     */
    @GetMapping("/products/{id}")
    public ResponseEntity<Product> getProductById(@PathVariable Long id) {
        Product product = productService.findById(id);
        return ResponseEntity.ok(product);
    }

    /**
     * @brief Lists products by category with pagination.
     * @param categoryId The ID of the category.
     * @param pageable   Pagination information.
     * @return A ResponseEntity containing a page of products.
     */
    @GetMapping("/categories/{categoryId}/products")
    public ResponseEntity<Page<Product>> listProductsByCategory(
            @PathVariable Long categoryId,
            @PageableDefault(sort = "name", direction = Sort.Direction.ASC, size = 20) Pageable pageable) {

        Page<Product> products = productService.listProductsByCategory(categoryId, pageable);
        return ResponseEntity.ok(products);
    }

    /**
     * @brief Search products by name.
     * @param query    The search query.
     * @param pageable Pagination information.
     * @return A ResponseEntity containing a page of products.
     */
    @GetMapping("/products/search")
    public ResponseEntity<Page<Product>> searchProducts(
            @RequestParam String query,
            @PageableDefault(sort = "name", direction = Sort.Direction.ASC, size = 20) Pageable pageable) {
        Page<Product> products = productService.searchByName(query, pageable);
        return ResponseEntity.ok(products);
    }

    /**
     * @brief Create a new product.
     * @param product The product to create.
     * @return A ResponseEntity containing the created product.
     */
    @PostMapping("/products")
    public ResponseEntity<Product> createProduct(@RequestBody Product product) {
        Product created = productService.save(product);
        return ResponseEntity.ok(created);
    }

    /**
     * @brief Update an existing product.
     * @param id      The product ID.
     * @param product The updated product data.
     * @return A ResponseEntity containing the updated product.
     */
    @PutMapping("/products/{id}")
    public ResponseEntity<Product> updateProduct(@PathVariable Long id, @RequestBody Product product) {
        product.setId(id);
        Product updated = productService.save(product);
        return ResponseEntity.ok(updated);
    }

    /**
     * @brief Delete a product.
     * @param id The product ID.
     * @return A ResponseEntity with no content.
     */
    @DeleteMapping("/products/{id}")
    public ResponseEntity<Void> deleteProduct(@PathVariable Long id) {
        productService.deleteById(id);
        return ResponseEntity.noContent().build();
    }
}
