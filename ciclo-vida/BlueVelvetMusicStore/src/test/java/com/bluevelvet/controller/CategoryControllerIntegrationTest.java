/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Integration Test for Category Controller.
 * @us US-1306 Create category of products - Granularity: Integration Test
 * @us US-0907 List categories of products - Granularity: Integration Test
 */
package com.bluevelvet.controller;

import com.bluevelvet.entity.Category;
import com.bluevelvet.repository.CategoryRepository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;

import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
@SuppressWarnings("null")
public class CategoryControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private CategoryRepository categoryRepository;

    @BeforeEach
    void setUp() {
        categoryRepository.deleteAll();
    }

    @Test
    @WithMockUser(username = "admin", roles = "ADMINISTRATOR")
    void createCategory_Success() throws Exception {
        mockMvc.perform(multipart("/api/categories")
                .param("name", "New Category")
                .param("enabled", "true"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name", is("New Category")));
    }

    @Test
    @WithMockUser(username = "user", roles = "USER")
    void createCategory_Forbidden_ForNonAdmin() throws Exception {
        mockMvc.perform(multipart("/api/categories")
                .param("name", "Forbidden Category"))
                .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(username = "admin", roles = "ADMINISTRATOR")
    void getRootCategories_Success() throws Exception {
        // Create 5 categories
        for (int i = 0; i < 5; i++) {
            categoryRepository.save(new Category("Cat " + i));
        }

        mockMvc.perform(get("/api/categories/public/roots"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content", hasSize(5)))
                .andExpect(jsonPath("$.content[0].name", is("Cat 0")));
    }

    @Test
    @WithMockUser(username = "admin", roles = "ADMINISTRATOR")
    void getCategory_WithChildren_Hierarchical() throws Exception {
        Category parent = new Category("Parent");
        Category child = new Category("Child", parent);
        parent.getChildren().add(child);

        categoryRepository.save(parent);
        categoryRepository.flush();

        mockMvc.perform(get("/api/categories/public/roots"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content[0].name", is("Parent")))
                .andExpect(jsonPath("$.content[0].children", hasSize(1)))
                .andExpect(jsonPath("$.content[0].children[0].name", is("Child")));
    }
}
