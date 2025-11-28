package com.bluevelvet.product;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/categories")
@RequiredArgsConstructor
public class ProductController {

    private final ProductService productService;

    @GetMapping("/{categoryId}/products")
    public ResponseEntity<Page<Product>> listProductsByCategory(
            @PathVariable Long categoryId,
            @PageableDefault(sort = "createdTime", direction = Sort.Direction.DESC) Pageable pageable) {

        Page<Product> products = productService.listProductsByCategory(categoryId, pageable);
        return ResponseEntity.ok(products);
    }
}
