package com.bluevelvet.category;

import com.bluevelvet.service.FileStorageService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

@Service
public class CategoryService {
    @Autowired
    private CategoryRepository categoryRepository;

    @Autowired
    private FileStorageService fileStorageService;

    public Category createCategory(String name, Long parentId, boolean enabled, MultipartFile image)
            throws IOException {
        if (categoryRepository.existsByName(name)) {
            throw new IllegalArgumentException("Category name already exists");
        }

        Category category = new Category();
        category.setName(name);
        category.setEnabled(enabled);

        if (parentId != null) {
            Category parent = categoryRepository.findById(parentId)
                    .orElseThrow(() -> new IllegalArgumentException("Parent category not found"));
            category.setParent(parent);
        }

        if (image != null && !image.isEmpty()) {
            String fileName = fileStorageService.saveFile(image);
            category.setImageFileName(fileName);
        }

        return categoryRepository.save(category);
    }

    public List<Category> getAllCategories() {
        return categoryRepository.findAll();
    }

    public Page<Category> getRootCategories(Pageable pageable) {
        return categoryRepository.findByParentIsNull(pageable);
    }

    public Category getCategoryById(Long id) {
        return categoryRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("Category not found"));
    }

    @Transactional
    public Category updateCategory(Long id, String name, Long parentId, Boolean enabled, MultipartFile image)
            throws IOException {
        Category category = getCategoryById(id);

        if (name != null && !name.isEmpty() && !name.equals(category.getName())) {
            if (categoryRepository.existsByName(name)) {
                throw new IllegalArgumentException("Category name already exists");
            }
            category.setName(name);
        }

        if (enabled != null) {
            category.setEnabled(enabled);
        }

        if (parentId != null) {
            Category parent = categoryRepository.findById(parentId)
                    .orElseThrow(() -> new IllegalArgumentException("Parent category not found"));
            // Prevent circular dependency
            if (parent.getId().equals(id)) {
                throw new IllegalArgumentException("Category cannot be its own parent");
            }
            category.setParent(parent);
        } else {
            // If parentId is explicitly null, we might want to set parent to null (make it
            // root)
            // But usually we need a flag or check if the argument was provided.
            // For now, let's assume if parentId is passed as null, we don't change it
            // unless we have a specific logic.
            // However, for "update", we usually pass the new state. If parentId is null,
            // does it mean "no parent" or "don't change"?
            // Let's assume "no parent" if we are strictly following a DTO update.
            // But here I'll stick to: if parentId is passed (not null), update it. If we
            // want to remove parent, we might need a specific flag or ID -1.
            // Let's assume for now we don't remove parent in this simple method unless
            // specified.
        }

        if (image != null && !image.isEmpty()) {
            // Delete old image
            if (category.getImageFileName() != null) {
                fileStorageService.deleteFile(category.getImageFileName());
            }
            String fileName = fileStorageService.saveFile(image);
            category.setImageFileName(fileName);
        }

        return categoryRepository.save(category);
    }

    public void deleteCategory(Long id) {
        Category category = getCategoryById(id);
        if (!category.getChildren().isEmpty()) {
            throw new IllegalStateException("Cannot delete category with children");
        }

        if (category.getImageFileName() != null) {
            fileStorageService.deleteFile(category.getImageFileName());
        }

        categoryRepository.delete(category);
    }

    public List<Category> getCategoryPath(Long id) {
        Category category = getCategoryById(id);
        List<Category> path = new java.util.ArrayList<>();
        Category current = category;
        while (current != null) {
            path.add(0, current);
            current = current.getParent();
        }
        return path;
    }
}
