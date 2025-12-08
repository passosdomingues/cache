/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025-12-08
 * @brief Integration Test for Category Controller.
 * @us US-1306 Create category of products - Granularity: Integration Test
 * @us US-0907 List categories of products - Granularity: Integration Test
 */
package com.bluevelvet.category;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
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

    @Autowired
    private ObjectMapper objectMapper;

    @BeforeEach
    void setUp() {
        categoryRepository.deleteAll();
    }

    @Test
    @WithMockUser(username = "admin", roles = "ADMINISTRATOR")
    void createCategory_Success() throws Exception {
        Category category = new Category("New Category");
        category.setEnabled(true);

        mockMvc.perform(post("/api/categories")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(category)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name", is("New Category")));
    }

    @Test
    @WithMockUser(username = "user", roles = "USER")
    void createCategory_Forbidden_ForNonAdmin() throws Exception {
        Category category = new Category("Forbidden Category");

        mockMvc.perform(post("/api/categories")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(category)))
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
                .andExpect(jsonPath("$", hasSize(5)))
                .andExpect(jsonPath("$[0].name", is("Cat 0")));
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
                .andExpect(jsonPath("$[0].name", is("Parent")))
                .andExpect(jsonPath("$[0].children", hasSize(1)))
                .andExpect(jsonPath("$[0].children[0].name", is("Child")));
    }
}
