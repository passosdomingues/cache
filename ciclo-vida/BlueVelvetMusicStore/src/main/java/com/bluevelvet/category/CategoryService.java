package com.bluevelvet.category;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

/**
 * Service layer for category business logic and operations
 *
 * @brief Handles category-related business operations and data processing
 * @author Developer
 */
@Service
public class CategoryService {

    private final CategoryRepository categoryRepository;

    /**
     * @brief Constructor for dependency injection of category repository
     * @param categoryRepository The category repository to be injected
     */
    @Autowired
    public CategoryService(CategoryRepository categoryRepository) {
        this.categoryRepository = categoryRepository;
    }

    /**
     * @brief Retrieves all categories from the database
     * @return List of all categories
     */
    public List<Category> getAllCategories() {
        return categoryRepository.findAll();
    }

    /**
     * @brief Retrieves all enabled categories
     * @return List of enabled categories
     */
    public List<Category> getEnabledCategories() {
        return categoryRepository.findByEnabledTrue();
    }

    /**
     * @brief Retrieves all root categories (categories with no parent)
     * @return List of root categories
     */
    public List<Category> getRootCategories() {
        return categoryRepository.findByParentIsNull();
    }

    /**
     * @brief Finds a category by its unique identifier
     * @param categoryId The ID of the category to find
     * @return Optional containing the category if found
     */
    public Optional<Category> getCategoryById(Long categoryId) {
        return categoryRepository.findById(categoryId);
    }

    /**
     * @brief Finds a category by its exact name
     * @param categoryName The name of the category to find
     * @return Optional containing the category if found
     */
    public Optional<Category> getCategoryByName(String categoryName) {
        return categoryRepository.findByName(categoryName);
    }

    /**
     * @brief Saves a new category or updates an existing one
     * @param category The category entity to save or update
     * @return The saved category entity
     */
    public Category saveCategory(Category category) {
        return categoryRepository.save(category);
    }

    /**
     * @brief Deletes a category by its unique identifier
     * @param categoryId The ID of the category to delete
     */
    public void deleteCategory(Long categoryId) {
        categoryRepository.deleteById(categoryId);
    }

    /**
     * @brief Checks if a category with the given name exists
     * @param categoryName The name to check for existence
     * @return Boolean indicating if category exists
     */
    public boolean categoryExists(String categoryName) {
        return categoryRepository.existsByName(categoryName);
    }

    /**
     * @brief Retrieves all subcategories of a specific parent category
     * @param parentCategory The parent category to find children for
     * @return List of child categories
     */
    public List<Category> getSubcategories(Category parentCategory) {
        return categoryRepository.findByParent(parentCategory);
    }

    /**
     * @brief Retrieves all subcategories of a parent category by ID
     * @param parentCategoryId The ID of the parent category
     * @return List of child categories
     */
    public List<Category> getSubcategoriesByParentId(Long parentCategoryId) {
        Optional<Category> parentCategory = categoryRepository.findById(parentCategoryId);
        return parentCategory.map(categoryRepository::findByParent)
                .orElse(List.of());
    }

    /**
     * @brief Toggles the enabled status of a category
     * @param categoryId The ID of the category to toggle
     * @return Boolean indicating the new enabled status, or null if category not found
     */
    public Boolean toggleCategoryStatus(Long categoryId) {
        Optional<Category> categoryOptional = categoryRepository.findById(categoryId);
        if (categoryOptional.isPresent()) {
            Category category = categoryOptional.get();
            category.setEnabled(!category.getEnabled());
            categoryRepository.save(category);
            return category.getEnabled();
        }
        return null;
    }
}