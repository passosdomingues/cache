package com.university.restaurant.service;

import com.university.restaurant.model.Menu;
import com.university.restaurant.model.WeekDay;
import com.university.restaurant.model.MealType;
import com.university.restaurant.repository.MenuRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

/**
 * Service for menu-related operations
 */
@Service
public class MenuService {
    
    @Autowired
    private MenuRepository menuRepository;
    
    /**
     * Create a new menu
     */
    public Menu createMenu(Menu menu) {
        return menuRepository.save(menu);
    }
    
    /**
     * Get active menus
     */
    public List<Menu> getActiveMenus() {
        return menuRepository.findActiveMenusOrdered();
    }
    
    /**
     * Get menu by weekday and meal type
     */
    public Optional<Menu> getMenu(WeekDay weekDay, MealType mealType) {
        return menuRepository.findActiveMenu(weekDay, mealType, LocalDate.now());
    }
    
    /**
     * Update an existing menu
     */
    public Menu updateMenu(Long id, Menu menuDetails) {
        Menu menu = menuRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Menu not found"));
        
        menu.setWeekDay(menuDetails.getWeekDay());
        menu.setMealType(menuDetails.getMealType());
        menu.setDescription(menuDetails.getDescription());
        menu.setVegetarianOption(menuDetails.getVegetarianOption());
        menu.setVeganOption(menuDetails.getVeganOption());
        menu.setValidFrom(menuDetails.getValidFrom());
        menu.setValidTo(menuDetails.getValidTo());
        menu.setActive(menuDetails.isActive());
        
        return menuRepository.save(menu);
    }
    
    /**
     * Delete a menu (soft delete)
     */
    public void deleteMenu(Long id) {
        Menu menu = menuRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Menu not found"));
        
        menu.setActive(false);
        menuRepository.save(menu);
    }
    
    /**
     * Get menu by ID
     */
    public Menu getById(Long id) {
        return menuRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Menu not found"));
    }
    
    /**
     * Get weekly menu
     */
    public List<Menu> getWeeklyMenu(LocalDate startDate) {
        LocalDate endDate = startDate.plusDays(6);
        return menuRepository.findMenusBetweenDates(startDate, endDate);
    }
    
    /**
     * Get today's menu
     */
    public List<Menu> getTodaysMenu() {
        return menuRepository.findMenusForDate(LocalDate.now());
    }
}