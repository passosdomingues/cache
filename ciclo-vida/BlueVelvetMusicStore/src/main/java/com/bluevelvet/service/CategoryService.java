/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Service layer for category business logic and operations
 * @us US-1306 Create category of products - Granularity: Business Logic
 * @us US-1307 Edit category of products - Granularity: Business Logic
 * @us US-0904 Delete category of products - Granularity: Business Logic
 * @us US-2100 List products within a category - Granularity: Business Logic
 */
package com.bluevelvet.service;

import com.bluevelvet.entity.Category;
import com.bluevelvet.repository.CategoryRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

/**
 * @brief Handles category-related business operations and data processing
 */
@Service
public class CategoryService {

    private final CategoryRepository categoryRepository;
    private final FileStorageService fileStorageService;

    /**
     * @brief Constructor for dependency injection of category repository and file
     *        storage service
     * @param categoryRepository The category repository to be injected
     * @param fileStorageService The file storage service to be injected
     */
    @Autowired
    public CategoryService(CategoryRepository categoryRepository, FileStorageService fileStorageService) {
        this.categoryRepository = categoryRepository;
        this.fileStorageService = fileStorageService;
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
     * @brief Retrieves all root categories with pagination
     * @param pageable Pagination info
     * @return Page of root categories
     */
    public Page<Category> getRootCategories(Pageable pageable) {
        return categoryRepository.findByParentIsNull(pageable);
    }

    /**
     * @brief Finds a category by its unique identifier
     * @param categoryId The ID of the category to find
     * @return Optional containing the category if found
     */
    public Optional<Category> getCategoryById(Long categoryId) {
        if (categoryId == null)
            return Optional.empty();
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
        if (category == null)
            throw new IllegalArgumentException("Category must not be null");
        return categoryRepository.save(category);
    }

    /**
     * @brief Creates a new category with the specified details.
     * @param name     The name of the category.
     * @param parentId The ID of the parent category (can be null).
     * @param enabled  Whether the category is enabled.
     * @param image    The image file for the category (can be null).
     * @return The created Category.
     * @throws IOException              If an error occurs while saving the image.
     * @throws IllegalArgumentException If the category name already exists or
     *                                  parent is not found.
     */
    public Category createCategory(String name, Long parentId, boolean enabled, MultipartFile image)
            throws IOException {
        if (categoryRepository.existsByName(name)) {
            throw new IllegalArgumentException("Category with name " + name + " already exists");
        }

        Category category = new Category(name);
        category.setEnabled(enabled);

        if (parentId != null) {
            Category parent = categoryRepository.findById(parentId)
                    .orElseThrow(() -> new IllegalArgumentException("Parent category not found with ID: " + parentId));
            category.setParent(parent);
        }

        if (image != null && !image.isEmpty()) {
            String fileName = fileStorageService.saveFile(image);
            category.setImageFileName(fileName);
        }

        return categoryRepository.save(category);
    }

    /**
     * @brief Updates an existing category (US-1307).
     * @param id       The ID of the category to update.
     * @param name     The new name of the category.
     * @param parentId The new parent ID (can be null).
     * @param enabled  The new enabled status.
     * @param image    The new image file (can be null).
     * @return The updated Category.
     * @throws IOException If image saving fails.
     */
    public Category updateCategory(Long id, String name, Long parentId, boolean enabled, MultipartFile image)
            throws IOException {
        if (id == null) {
            throw new IllegalArgumentException("Category ID must not be null");
        }
        Category category = categoryRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Category not found with ID: " + id));

        category.setName(name);
        category.setEnabled(enabled);

        if (parentId != null) {
            Category parent = categoryRepository.findById(parentId)
                    .orElseThrow(() -> new IllegalArgumentException("Parent category not found"));

            // Check for circular reference
            if (parent.getId().equals(id) || isDescendant(category, parent)) {
                throw new IllegalArgumentException("Category cannot be its own parent or a descendant of itself");
            }
            category.setParent(parent);
        } else {
            category.setParent(null);
        }

        if (image != null && !image.isEmpty()) {
            // Delete old image if it exists
            if (category.getImageFileName() != null) {
                fileStorageService.deleteFile(category.getImageFileName());
            }
            String fileName = fileStorageService.saveFile(image);
            category.setImageFileName(fileName);
        }

        return categoryRepository.save(category);
    }

    /**
     * @brief Deletes a category by its unique identifier (US-0904).
     *        Only allows deletion if the category has no children.
     *        Also deletes the associated image directory/file.
     * @param categoryId The ID of the category to delete
     * @throws IllegalArgumentException if the category has children.
     */
    public void deleteCategory(Long categoryId) {
        if (categoryId == null)
            return;

        Category category = categoryRepository.findById(categoryId)
                .orElseThrow(() -> new IllegalArgumentException("Category not found"));

        if (!category.getChildren().isEmpty()) {
            throw new IllegalArgumentException(
                    "Cannot delete category with sub-categories. Please delete children first.");
        }

        if (category.getImageFileName() != null) {
            fileStorageService.deleteFile(category.getImageFileName());
            // Note: If we had a directory per category, we would delete it here.
            // Currently assuming 'deleteFile' handles the cleanup of the file.
            // Requirement "delete the category image directory" implies structure
            // optimization usually.
        }

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
        if (parentCategoryId == null)
            return List.of();
        Optional<Category> parentCategory = categoryRepository.findById(parentCategoryId);
        return parentCategory.map(categoryRepository::findByParent)
                .orElse(List.of());
    }

    /**
     * @brief Toggles the enabled status of a category
     * @param categoryId The ID of the category to toggle
     * @return Boolean indicating the new enabled status, or null if category not
     *         found
     */
    public Boolean toggleCategoryStatus(Long categoryId) {
        if (categoryId == null)
            return null;
        Optional<Category> categoryOptional = categoryRepository.findById(categoryId);
        if (categoryOptional.isPresent()) {
            Category category = categoryOptional.get();
            category.setEnabled(!category.getEnabled());
            categoryRepository.save(category);
            return category.getEnabled();
        }
        return null;
    }

    /**
     * @brief Checks if a category is a descendant of another category (recursive)
     * @param ancestor   The potential ancestor category
     * @param descendant The potential descendant category
     * @return true if 'descendant' is indeed a descendant of 'ancestor'
     */
    private boolean isDescendant(Category ancestor, Category descendant) {
        if (descendant == null || descendant.getParent() == null) {
            return false;
        }
        if (descendant.getParent().getId().equals(ancestor.getId())) {
            return true;
        }
        return isDescendant(ancestor, descendant.getParent());
    }
}
