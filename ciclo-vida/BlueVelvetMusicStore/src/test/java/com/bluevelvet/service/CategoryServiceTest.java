/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Unit Test for Category Service.
 * @us US-1306 Create category of products - Granularity: Unit Test
 */
package com.bluevelvet.service;

import com.bluevelvet.entity.Category;
import com.bluevelvet.repository.CategoryRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.io.IOException;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
@SuppressWarnings("null")
public class CategoryServiceTest {

    @Mock
    private CategoryRepository categoryRepository;

    @Mock
    private FileStorageService fileStorageService;

    @InjectMocks
    private CategoryService categoryService;

    private Category rootCategory;

    @BeforeEach
    void setUp() {
        rootCategory = new Category("Music");
        rootCategory.setId(1L);
        rootCategory.setEnabled(true);
    }

    @Test
    void createRootCategory_Success() throws IOException {
        when(categoryRepository.existsByName("Music")).thenReturn(false);
        when(categoryRepository.save(any(Category.class))).thenReturn(rootCategory);

        Category created = categoryService.createCategory("Music", null, true, null);

        assertNotNull(created);
        assertEquals("Music", created.getName());
        assertNull(created.getParent());
        verify(categoryRepository).save(any(Category.class));
    }

    @Test
    void createSubCategory_Success() throws IOException {
        Category subCategory = new Category("Vinyl", rootCategory);
        subCategory.setId(2L);

        when(categoryRepository.existsByName("Vinyl")).thenReturn(false);
        when(categoryRepository.findById(1L)).thenReturn(Optional.of(rootCategory));
        when(categoryRepository.save(any(Category.class))).thenReturn(subCategory);

        Category created = categoryService.createCategory("Vinyl", 1L, true, null);

        assertNotNull(created);
        assertEquals("Vinyl", created.getName());
        assertEquals(rootCategory, created.getParent());
        verify(categoryRepository).save(any(Category.class));
    }

    @Test
    void createCategory_DuplicateName_ThrowsException() {
        when(categoryRepository.existsByName("Music")).thenReturn(true);

        assertThrows(IllegalArgumentException.class, () -> {
            categoryService.createCategory("Music", null, true, null);
        });

        verify(categoryRepository, never()).save(any(Category.class));
    }

    @Test
    void createSubCategory_ParentNotFound_ThrowsException() {
        when(categoryRepository.existsByName("Vinyl")).thenReturn(false);
        when(categoryRepository.findById(99L)).thenReturn(Optional.empty());

        assertThrows(IllegalArgumentException.class, () -> {
            categoryService.createCategory("Vinyl", 99L, true, null);
        });

        verify(categoryRepository, never()).save(any(Category.class));
    }
}
