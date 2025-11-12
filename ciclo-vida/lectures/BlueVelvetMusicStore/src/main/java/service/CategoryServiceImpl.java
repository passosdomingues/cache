package service;

import com.bluevelvet.domain.dto.CategoryDTO;
import com.bluevelvet.domain.entity.CategoryEntity;
import com.bluevelvet.exception.DuplicateResourceException;
import com.bluevelvet.exception.ResourceNotFoundException;
import com.bluevelvet.repository.CategoryRepository;
import com.bluevelvet.service.CategoryService;
import com.bluevelvet.util.EntityMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

/**
 * @brief Implementation of CategoryService
 * @details Provides business logic for category management
 * Handles validation, exception management, and data transformation
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@Service
@RequiredArgsConstructor
@Slf4j
@Transactional
public class CategoryServiceImpl implements CategoryService {

    private final CategoryRepository categoryRepository;

    /**
     * @brief Create a new category
     * @param categoryDTO The category data
     * @return The created category DTO
     * @throws DuplicateResourceException if category name already exists
     */
    @Override
    public CategoryDTO createCategory(CategoryDTO categoryDTO) {
        log.info("Creating new category with name: {}", categoryDTO.getName());

        // Validate category name uniqueness
        if (categoryRepository.findByName(categoryDTO.getName()).isPresent()) {
            log.warn("Category with name '{}' already exists", categoryDTO.getName());
            throw new DuplicateResourceException("Category", "name", categoryDTO.getName());
        }

        // Build and save the entity
        CategoryEntity entity = CategoryEntity.builder()
            .name(categoryDTO.getName())
            .description(categoryDTO.getDescription())
            .imageFileName(categoryDTO.getImageFileName())
            .imageUrl(categoryDTO.getImageUrl())
            .isActive(categoryDTO.getIsActive() != null ? categoryDTO.getIsActive() : true)
            .displayOrder(categoryDTO.getDisplayOrder() != null ? categoryDTO.getDisplayOrder() : 0)
            .build();

        // Set parent category if provided
        if (categoryDTO.getParentId() != null) {
            CategoryEntity parentCategory = categoryRepository.findById(categoryDTO.getParentId())
                .orElseThrow(() -> new ResourceNotFoundException("Category", categoryDTO.getParentId()));
            entity.setParentCategory(parentCategory);
        }

        CategoryEntity savedEntity = categoryRepository.save(entity);
        log.info("Category created successfully with ID: {}", savedEntity.getId());

        return EntityMapper.toCategoryDTO(savedEntity);
    }

    /**
     * @brief Update an existing category
     * @param id The category ID
     * @param categoryDTO The updated category data
     * @return The updated category DTO
     * @throws ResourceNotFoundException if category not found
     * @throws DuplicateResourceException if new name already exists
     */
    @Override
    public CategoryDTO updateCategory(Long id, CategoryDTO categoryDTO) {
        log.info("Updating category with ID: {}", id);

        CategoryEntity entity = categoryRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Category", id));

        // Validate name uniqueness if name is being changed
        if (!entity.getName().equals(categoryDTO.getName()) && 
            categoryRepository.findByName(categoryDTO.getName()).isPresent()) {
            log.warn("Category with name '{}' already exists", categoryDTO.getName());
            throw new DuplicateResourceException("Category", "name", categoryDTO.getName());
        }

        // Update fields
        entity.setName(categoryDTO.getName());
        entity.setDescription(categoryDTO.getDescription());
        entity.setImageFileName(categoryDTO.getImageFileName());
        entity.setImageUrl(categoryDTO.getImageUrl());
        entity.setIsActive(categoryDTO.getIsActive() != null ? categoryDTO.getIsActive() : entity.getIsActive());
        entity.setDisplayOrder(categoryDTO.getDisplayOrder() != null ? categoryDTO.getDisplayOrder() : entity.getDisplayOrder());

        // Update parent category if provided
        if (categoryDTO.getParentId() != null) {
            CategoryEntity parentCategory = categoryRepository.findById(categoryDTO.getParentId())
                .orElseThrow(() -> new ResourceNotFoundException("Category", categoryDTO.getParentId()));
            
            // Prevent circular references
            if (parentCategory.getId().equals(id)) {
                log.warn("Attempted to set category as its own parent");
                throw new IllegalArgumentException("A category cannot be its own parent");
            }
            
            entity.setParentCategory(parentCategory);
        } else if (categoryDTO.getParentId() == null && entity.getParentCategory() != null) {
            entity.setParentCategory(null);
        }

        CategoryEntity updatedEntity = categoryRepository.save(entity);
        log.info("Category updated successfully with ID: {}", id);

        return EntityMapper.toCategoryDTO(updatedEntity);
    }

    /**
     * @brief Get a category by ID
     * @param id The category ID
     * @return The category DTO
     * @throws ResourceNotFoundException if category not found
     */
    @Override
    @Transactional(readOnly = true)
    public CategoryDTO getCategoryById(Long id) {
        log.debug("Fetching category with ID: {}", id);

        CategoryEntity entity = categoryRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Category", id));

        return EntityMapper.toCategoryDTO(entity);
    }

    /**
     * @brief Get all root categories
     * @return List of root category DTOs
     */
    @Override
    @Transactional(readOnly = true)
    public List<CategoryDTO> getAllRootCategories() {
        log.debug("Fetching all root categories");

        return categoryRepository.findAllRootCategories().stream()
            .map(EntityMapper::toCategoryDTO)
            .collect(Collectors.toList());
    }

    /**
     * @brief Get all root categories with pagination
     * @param pageable Pagination information
     * @return Page of root category DTOs
     */
    @Override
    @Transactional(readOnly = true)
    public Page<CategoryDTO> getAllRootCategoriesPaginated(Pageable pageable) {
        log.debug("Fetching root categories with pagination: {}", pageable);

        return categoryRepository.findAllRootCategoriesPaginated(pageable)
            .map(EntityMapper::toCategoryDTO);
    }

    /**
     * @brief Get subcategories of a parent category
     * @param parentId The parent category ID
     * @return List of subcategory DTOs
     * @throws ResourceNotFoundException if parent category not found
     */
    @Override
    @Transactional(readOnly = true)
    public List<CategoryDTO> getSubcategoriesByParentId(Long parentId) {
        log.debug("Fetching subcategories for parent ID: {}", parentId);

        // Verify parent exists
        categoryRepository.findById(parentId)
            .orElseThrow(() -> new ResourceNotFoundException("Category", parentId));

        return categoryRepository.findSubcategoriesByParentId(parentId).stream()
            .map(EntityMapper::toCategoryDTO)
            .collect(Collectors.toList());
    }

    /**
     * @brief Get subcategories of a parent category with pagination
     * @param parentId The parent category ID
     * @param pageable Pagination information
     * @return Page of subcategory DTOs
     * @throws ResourceNotFoundException if parent category not found
     */
    @Override
    @Transactional(readOnly = true)
    public Page<CategoryDTO> getSubcategoriesByParentIdPaginated(Long parentId, Pageable pageable) {
        log.debug("Fetching subcategories for parent ID: {} with pagination: {}", parentId, pageable);

        // Verify parent exists
        categoryRepository.findById(parentId)
            .orElseThrow(() -> new ResourceNotFoundException("Category", parentId));

        return categoryRepository.findSubcategoriesByParentIdPaginated(parentId, pageable)
            .map(EntityMapper::toCategoryDTO);
    }

    /**
     * @brief Search categories by name
     * @param searchTerm The search term
     * @param pageable Pagination information
     * @return Page of matching category DTOs
     */
    @Override
    @Transactional(readOnly = true)
    public Page<CategoryDTO> searchCategoriesByName(String searchTerm, Pageable pageable) {
        log.debug("Searching categories with term: {}", searchTerm);

        return categoryRepository.searchByName(searchTerm, pageable)
            .map(EntityMapper::toCategoryDTO);
    }

    /**
     * @brief Delete a category (soft delete)
     * @param id The category ID
     * @throws ResourceNotFoundException if category not found
     */
    @Override
    public void deleteCategory(Long id) {
        log.info("Deleting category with ID: {}", id);

        CategoryEntity entity = categoryRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Category", id));

        categoryRepository.delete(entity);
        log.info("Category deleted successfully with ID: {}", id);
    }

    /**
     * @brief Activate a category
     * @param id The category ID
     * @return The activated category DTO
     * @throws ResourceNotFoundException if category not found
     */
    @Override
    public CategoryDTO activateCategory(Long id) {
        log.info("Activating category with ID: {}", id);

        CategoryEntity entity = categoryRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Category", id));

        entity.setIsActive(true);
        CategoryEntity updatedEntity = categoryRepository.save(entity);
        log.info("Category activated successfully with ID: {}", id);

        return EntityMapper.toCategoryDTO(updatedEntity);
    }

    /**
     * @brief Deactivate a category
     * @param id The category ID
     * @return The deactivated category DTO
     * @throws ResourceNotFoundException if category not found
     */
    @Override
    public CategoryDTO deactivateCategory(Long id) {
        log.info("Deactivating category with ID: {}", id);

        CategoryEntity entity = categoryRepository.findById(id)
            .orElseThrow(() -> new ResourceNotFoundException("Category", id));

        entity.setIsActive(false);
        CategoryEntity updatedEntity = categoryRepository.save(entity);
        log.info("Category deactivated successfully with ID: {}", id);

        return EntityMapper.toCategoryDTO(updatedEntity);
    }

    /**
     * @brief Get the total count of active categories
     * @return The count of active categories
     */
    @Override
    @Transactional(readOnly = true)
    public long getActiveCategoriesCount() {
        log.debug("Counting active categories");
        return categoryRepository.countActive();
    }

}
