/**
 * @brief REST controller for product management operations.
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 November 30
 */
package com.bluevelvet.product;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * @brief Controller for handling product-related requests.
 */
@RestController
@RequestMapping("/api/categories")
@RequiredArgsConstructor
public class ProductController {

    private final ProductService productService;

    /**
     * @brief Lists products by category with pagination.
     * @param categoryId The ID of the category.
     * @param pageable   Pagination information.
     * @return A ResponseEntity containing a page of products.
     */
    @GetMapping("/{categoryId}/products")
    public ResponseEntity<Page<Product>> listProductsByCategory(
            @PathVariable Long categoryId,
            @PageableDefault(sort = "createdTime", direction = Sort.Direction.DESC) Pageable pageable) {

        Page<Product> products = productService.listProductsByCategory(categoryId, pageable);
        return ResponseEntity.ok(products);
    }
}
