/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Data initializer for pre-populating database with essential data
 * @us US-1306 Create category of products - Granularity: Database Seeding
 */
package com.bluevelvet.config;

import com.bluevelvet.auth.Role;
import com.bluevelvet.auth.RoleName;
import com.bluevelvet.auth.RoleRepository;
import com.bluevelvet.entity.Category;
import com.bluevelvet.repository.CategoryRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

/**
 * @brief Loads initial roles and categories into the database on application
 *        startup
 */
@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    RoleRepository roleRepository;

    @Autowired
    CategoryRepository categoryRepository;

    /**
     * @brief Executes data initialization on application startup
     * @param args Command line arguments passed to the application
     * @throws Exception if data initialization fails
     */
    @Override
    public void run(String... args) throws Exception {
        initializeRoles();
        initializeCategories();
    }

    /**
     * @brief Initializes system roles if they don't exist
     */
    private void initializeRoles() {
        if (roleRepository.count() == 0) {
            roleRepository.save(new Role(RoleName.ROLE_ADMINISTRATOR));
            roleRepository.save(new Role(RoleName.ROLE_SALES_MANAGER));
            roleRepository.save(new Role(RoleName.ROLE_EDITOR));
            roleRepository.save(new Role(RoleName.ROLE_ASSISTANT));
            roleRepository.save(new Role(RoleName.ROLE_SHIPPING_MANAGER));

            System.out.println("Initial roles created successfully");
        }
    }

    /**
     * @brief Initializes product categories if they don't exist
     */
    private void initializeCategories() {
        if (categoryRepository.count() == 0) {
            // Create root categories
            Category musicCategory = new Category("Music");
            musicCategory.setEnabled(true);
            categoryRepository.save(musicCategory);

            Category booksCategory = new Category("Books");
            booksCategory.setEnabled(true);
            categoryRepository.save(booksCategory);

            Category tshirtsCategory = new Category("T-Shirts");
            tshirtsCategory.setEnabled(true);
            categoryRepository.save(tshirtsCategory);

            // Create subcategories for Music
            Category vinylCategory = new Category("Vinyl");
            vinylCategory.setParent(musicCategory);
            vinylCategory.setEnabled(true);
            categoryRepository.save(vinylCategory);

            Category cdCategory = new Category("CD");
            cdCategory.setParent(musicCategory);
            cdCategory.setEnabled(true);
            categoryRepository.save(cdCategory);

            Category mp3Category = new Category("MP3");
            mp3Category.setParent(musicCategory);
            mp3Category.setEnabled(true);
            categoryRepository.save(mp3Category);

            // Create subcategories for Books
            Category biographiesCategory = new Category("Biographies");
            biographiesCategory.setParent(booksCategory);
            biographiesCategory.setEnabled(true);
            categoryRepository.save(biographiesCategory);

            Category sheetMusicCategory = new Category("Sheet Music");
            sheetMusicCategory.setParent(booksCategory);
            sheetMusicCategory.setEnabled(true);
            categoryRepository.save(sheetMusicCategory);

            Category acousticGuitarCategory = new Category("Acoustic Guitar");
            acousticGuitarCategory.setParent(musicCategory);
            acousticGuitarCategory.setEnabled(true);
            categoryRepository.save(acousticGuitarCategory);

            System.out.println("Initial categories created successfully");
        }
    }
}
