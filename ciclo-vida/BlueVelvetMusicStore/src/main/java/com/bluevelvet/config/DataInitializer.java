package com.bluevelvet.config;

import com.bluevelvet.auth.Role;
import com.bluevelvet.auth.RoleName;
import com.bluevelvet.auth.RoleRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    RoleRepository roleRepository;

    @Autowired
    com.bluevelvet.category.CategoryRepository categoryRepository;

    @Override
    public void run(String... args) throws Exception {
        if (roleRepository.count() == 0) {
            roleRepository.save(new Role(RoleName.ROLE_ADMINISTRATOR));
            roleRepository.save(new Role(RoleName.ROLE_SALES_MANAGER));
            roleRepository.save(new Role(RoleName.ROLE_EDITOR));
            roleRepository.save(new Role(RoleName.ROLE_ASSISTANT));
            roleRepository.save(new Role(RoleName.ROLE_SHIPPING_MANAGER));
        }

        if (categoryRepository.count() == 0) {
            // Root Categories
            com.bluevelvet.category.Category music = new com.bluevelvet.category.Category("Music");
            music.setEnabled(true);
            categoryRepository.save(music);

            com.bluevelvet.category.Category books = new com.bluevelvet.category.Category("Books");
            books.setEnabled(true);
            categoryRepository.save(books);

            com.bluevelvet.category.Category tshirts = new com.bluevelvet.category.Category("T-Shirts");
            tshirts.setEnabled(true);
            categoryRepository.save(tshirts);

            // Subcategories for Music
            categoryRepository.save(new com.bluevelvet.category.Category("Vinyl", music));
            categoryRepository.save(new com.bluevelvet.category.Category("CD", music));
            categoryRepository.save(new com.bluevelvet.category.Category("MP3", music));

            // Subcategories for Books
            categoryRepository.save(new com.bluevelvet.category.Category("Biographies", books));
            categoryRepository.save(new com.bluevelvet.category.Category("Sheet Music", books));
        }
    }
}
