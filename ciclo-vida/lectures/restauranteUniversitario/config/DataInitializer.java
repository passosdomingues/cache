package com.university.restaurant.config;

import com.university.restaurant.model.*;
import com.university.restaurant.repository.MenuRepository;
import com.university.restaurant.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.util.Arrays;

/**
 * Initializes default data including admin user, test user, and sample menu
 */
@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private MenuRepository menuRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) throws Exception {
        // Create admin user
        if (!userRepository.findByEmail("admin@university.com").isPresent()) {
            User admin = new User();
            admin.setName("Administrator");
            admin.setEmail("admin@university.com");
            admin.setPassword(passwordEncoder.encode("admin123"));
            admin.setVegetarian(false);
            admin.setVegan(false);
            admin.setAdministrator(true);
            userRepository.save(admin);
        }

        // Create test user
        if (!userRepository.findByEmail("user@university.com").isPresent()) {
            User user = new User();
            user.setName("Test User");
            user.setEmail("user@university.com");
            user.setPassword(passwordEncoder.encode("user123"));
            user.setVegetarian(true);
            user.setVegan(false);
            user.setAdministrator(false);
            userRepository.save(user);
        }

        // Create sample menu data for August 18-25, 2025
        if (menuRepository.count() == 0) {
            initializeMenuData();
        }
    }

    private void initializeMenuData() {
        // Breakfast menu
        createMenu(WeekDay.MONDAY, MealType.BREAKFAST, "Erva Doce", "Biscoito de maisena", "Maçã", 
                  LocalDate.of(2025, 8, 18), LocalDate.of(2025, 8, 25));
        createMenu(WeekDay.TUESDAY, MealType.BREAKFAST, "Canela", "Biscoito água e sal", "Melancia", 
                  LocalDate.of(2025, 8, 19), LocalDate.of(2025, 8, 25));
        createMenu(WeekDay.WEDNESDAY, MealType.BREAKFAST, "Hortelã", "Biscoito de chocolate", "Laranja", 
                  LocalDate.of(2025, 8, 20), LocalDate.of(2025, 8, 25));
        createMenu(WeekDay.THURSDAY, MealType.BREAKFAST, "Camomila", "Sequilhos de coco", "Banana", 
                  LocalDate.of(2025, 8, 21), LocalDate.of(2025, 8, 25));
        createMenu(WeekDay.FRIDAY, MealType.BREAKFAST, "Capim cidreira", "Torrada", "Mamão", 
                  LocalDate.of(2025, 8, 22), LocalDate.of(2025, 8, 25));
        createMenu(WeekDay.MONDAY, MealType.BREAKFAST, "Erva doce", "Biscoito de coco", "Maçã", 
                  LocalDate.of(2025, 8, 25), LocalDate.of(2025, 8, 25));

        // Lunch menu
        createLunchMenu(WeekDay.MONDAY, "Strogonoff de frango/Parmegiana suína", "Strogonoff de soja", 
                       Arrays.asList("Alface", "Acelga", "Tomate"), "Batata palha", "Laranja", 
                       LocalDate.of(2025, 8, 18), LocalDate.of(2025, 8, 25));
        createLunchMenu(WeekDay.TUESDAY, "Picadinho bovino/Isca de frango", "Torta de milho com queijo", 
                       Arrays.asList("Alface", "Agrião", "Pepino", "Batata doce cozida"), "Abobora madura com ervas", "Mamão", 
                       LocalDate.of(2025, 8, 19), LocalDate.of(2025, 8, 25));
        // Add more lunch menus for other days...

        // Dinner menu
        createDinnerMenu(WeekDay.MONDAY, "Fricassê de frango/Rocambole bovino", "Ovos mexidos", 
                        Arrays.asList("Alface", "Couve", "Cenoura ralada", "Beterraba cozida"), "Repolho refogado", "Mamão", 
                        LocalDate.of(2025, 8, 18), LocalDate.of(2025, 8, 25));
        // Add more dinner menus for other days...
    }

    private void createMenu(WeekDay day, MealType mealType, String drink, String snack, String fruit, 
                           LocalDate validFrom, LocalDate validTo) {
        Menu menu = new Menu();
        menu.setWeekDay(day);
        menu.setMealType(mealType);
        menu.setDescription(String.format("Drink: %s, Snack: %s, Fruit: %s", drink, snack, fruit));
        menu.setValidFrom(validFrom);
        menu.setValidTo(validTo);
        menu.setActive(true);
        menuRepository.save(menu);
    }

    private void createLunchMenu(WeekDay day, String mainDish, String vegetarianOption, 
                                java.util.List<String> salads, String garnish, String dessert, 
                                LocalDate validFrom, LocalDate validTo) {
        Menu menu = new Menu();
        menu.setWeekDay(day);
        menu.setMealType(MealType.LUNCH);
        menu.setDescription(String.format("Main: %s, Vegetarian: %s, Salads: %s, Garnish: %s, Dessert: %s", 
                         mainDish, vegetarianOption, String.join(", ", salads), garnish, dessert));
        menu.setVegetarianOption(vegetarianOption);
        menu.setValidFrom(validFrom);
        menu.setValidTo(validTo);
        menu.setActive(true);
        menuRepository.save(menu);
    }

    private void createDinnerMenu(WeekDay day, String mainDish, String vegetarianOption, 
                                 java.util.List<String> salads, String garnish, String dessert, 
                                 LocalDate validFrom, LocalDate validTo) {
        Menu menu = new Menu();
        menu.setWeekDay(day);
        menu.setMealType(MealType.DINNER);
        menu.setDescription(String.format("Main: %s, Vegetarian: %s, Salads: %s, Garnish: %s, Dessert: %s", 
                         mainDish, vegetarianOption, String.join(", ", salads), garnish, dessert));
        menu.setVegetarianOption(vegetarianOption);
        menu.setValidFrom(validFrom);
        menu.setValidTo(validTo);
        menu.setActive(true);
        menuRepository.save(menu);
    }
}