package com.bluevelvet.category;

import com.bluevelvet.auth.RoleRepository;
import com.bluevelvet.auth.UserRepository;
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
public class CategoryControllerIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private CategoryRepository categoryRepository;

    @BeforeEach
    void setUp() {
        categoryRepository.deleteAll();
        // Roles are initialized by DataInitializer, but we can ensure they exist or
        // just use @WithMockUser
        // DataInitializer runs on startup, so roles should be there.
    }

    @Test
    @WithMockUser(username = "admin", roles = "ADMINISTRATOR")
    void createCategory_Success() throws Exception {
        mockMvc.perform(post("/api/categories")
                .param("name", "New Category")
                .param("enabled", "true"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name", is("New Category")));
    }

    @Test
    @WithMockUser(username = "user", roles = "USER") // No such role in our enum, but Spring Security handles strings
    void createCategory_Forbidden_ForNonAdmin() throws Exception {
        // Our SecurityConfig uses hasRole('ADMINISTRATOR')
        // @WithMockUser(roles="USER") creates a user with authority ROLE_USER.
        // The controller requires ROLE_ADMINISTRATOR.

        mockMvc.perform(post("/api/categories")
                .param("name", "Forbidden Category"))
                .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(username = "admin", roles = "ADMINISTRATOR")
    void getRootCategories_Pagination() throws Exception {
        // Create 10 categories
        for (int i = 0; i < 10; i++) {
            categoryRepository.save(new Category("Cat " + i));
        }

        mockMvc.perform(get("/api/categories/root")
                .param("page", "0")
                .param("size", "5")
                .param("sortBy", "name")
                .param("sortDir", "asc"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content", hasSize(5)))
                .andExpect(jsonPath("$.totalElements", is(10)))
                .andExpect(jsonPath("$.totalPages", is(2)))
                .andExpect(jsonPath("$.content[0].name", is("Cat 0")));
    }

    @Test
    @WithMockUser(username = "admin", roles = "ADMINISTRATOR")
    void getCategory_WithChildren_Hierarchical() throws Exception {
        Category parent = new Category("Parent");
        Category child = new Category("Child", parent);
        parent.getChildren().add(child);

        categoryRepository.save(parent);

        mockMvc.perform(get("/api/categories/root"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content[0].name", is("Parent")))
                .andExpect(jsonPath("$.content[0].children", hasSize(1)))
                .andExpect(jsonPath("$.content[0].children[0].name", is("Child")));
    }

    @Test
    @WithMockUser(username = "admin", roles = "ADMINISTRATOR")
    void getCategoryPath_Success() throws Exception {
        Category parent = new Category("Parent");
        Category child = new Category("Child", parent);
        Category grandchild = new Category("Grandchild", child);

        parent.getChildren().add(child);
        child.getChildren().add(grandchild);

        categoryRepository.save(parent);

        // We need to fetch the saved grandchild to get its ID
        // Since we saved parent with cascade, grandchild should be saved.
        // But we don't have the ID in the 'grandchild' object unless we refresh or
        // fetch.
        // Let's fetch by name.
        // Actually, save() returns the saved entity, but cascade might not update child
        // IDs in the original object graph immediately without refresh.
        // Let's rely on repository to find it.

        // Wait, if I save parent, Hibernate might update IDs in the objects if they are
        // the same instances.
        // Let's try fetching.

        // To be safe and simple:
        Category savedParent = categoryRepository.save(parent);
        Category savedChild = savedParent.getChildren().get(0);
        Category savedGrandchild = savedChild.getChildren().get(0);

        mockMvc.perform(get("/api/categories/{id}/path", savedGrandchild.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(3)))
                .andExpect(jsonPath("$[0].name", is("Parent")))
                .andExpect(jsonPath("$[1].name", is("Child")))
                .andExpect(jsonPath("$[2].name", is("Grandchild")));
    }
}
