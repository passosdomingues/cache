/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Integration Test for Product Controller.
 * @us US-2100 List products within a category - Granularity: Integration Test
 */
package com.bluevelvet.controller;

import com.bluevelvet.entity.Category;
import com.bluevelvet.entity.Product;
import com.bluevelvet.repository.CategoryRepository;
import com.bluevelvet.repository.ProductRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;

import static org.hamcrest.Matchers.hasSize;
import static org.hamcrest.Matchers.is;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
@SuppressWarnings("null")
public class ProductControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private CategoryRepository categoryRepository;

    @BeforeEach
    void setUp() {
        productRepository.deleteAll();
        categoryRepository.deleteAll();
        productRepository.flush();
        categoryRepository.flush();
    }

    @Test
    @WithMockUser
    void listProductsByCategory_Success() throws Exception {
        Category category = new Category("Music");
        category = categoryRepository.save(category);

        Product product1 = new Product("Guitar", new BigDecimal("100.00"), category);
        product1.setEnabled(true);
        productRepository.save(product1);

        Product product2 = new Product("Piano", new BigDecimal("500.00"), category);
        product2.setEnabled(true);
        productRepository.save(product2);

        mockMvc.perform(get("/api/categories/{id}/products", category.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content", hasSize(2)))
                .andExpect(jsonPath("$.content[0].name", is("Guitar"))) // Default sort is name ASC
                .andExpect(jsonPath("$.content[1].name", is("Piano")));
    }

    @Test
    @WithMockUser
    void listProductsByCategory_NotFound() throws Exception {
        mockMvc.perform(get("/api/categories/{id}/products", 999L))
                .andExpect(status().isNotFound());
    }

    @Test
    @WithMockUser
    void listProductsByCategory_OnlyEnabled() throws Exception {
        Category category = new Category("Music");
        category = categoryRepository.save(category);

        Product product1 = new Product("Guitar", new BigDecimal("100.00"), category);
        product1.setEnabled(true);
        productRepository.save(product1);

        Product product2 = new Product("Broken Drum", new BigDecimal("50.00"), category);
        product2.setEnabled(false);
        productRepository.save(product2);

        mockMvc.perform(get("/api/categories/{id}/products", category.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content", hasSize(1)))
                .andExpect(jsonPath("$.content[0].name", is("Guitar")));
    }

    @Test
    @WithMockUser
    void listProductsByCategory_Pagination() throws Exception {
        Category category = new Category("Music");
        category = categoryRepository.save(category);

        for (int i = 0; i < 10; i++) {
            Product p = new Product("Product " + i, new BigDecimal("10.00"), category);
            p.setEnabled(true);
            productRepository.save(p);
        }

        mockMvc.perform(get("/api/categories/{id}/products", category.getId())
                .param("page", "0")
                .param("size", "5"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content", hasSize(5)))
                .andExpect(jsonPath("$.totalElements", is(10)))
                .andExpect(jsonPath("$.totalPages", is(2)));
    }
}
