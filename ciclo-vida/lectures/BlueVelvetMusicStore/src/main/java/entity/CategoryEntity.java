package entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.SoftDelete;
import org.hibernate.annotations.UpdateTimestamp;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

/**
 * @brief JPA Entity representing a product category in the Bluevelvet Music Store
 * @details Implements hierarchical category structure with parent-child relationships
 * Supports soft delete to maintain data integrity and audit trails
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@Entity
@Table(name = "categories", indexes = {
    @Index(name = "idx_category_name", columnList = "name"),
    @Index(name = "idx_category_parent_id", columnList = "parent_id"),
    @Index(name = "idx_category_is_active", columnList = "is_active"),
    @Index(name = "idx_category_deleted_at", columnList = "deleted_at")
})
@SoftDelete(columnName = "deleted_at")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@EqualsAndHashCode(exclude = {"parentCategory", "subcategories"})
@ToString(exclude = {"parentCategory", "subcategories"})
public class CategoryEntity implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * @brief Unique identifier for the category
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    /**
     * @brief Category name - must be unique and not blank
     */
    @Column(name = "name", nullable = false, unique = true, length = 255)
    @NotBlank(message = "Category name cannot be blank")
    @Size(min = 1, max = 255, message = "Category name must be between 1 and 255 characters")
    private String name;

    /**
     * @brief Detailed description of the category
     */
    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    /**
     * @brief File name for the category image
     */
    @Column(name = "image_file_name", length = 255)
    private String imageFileName;

    /**
     * @brief URL or path to the category image
     */
    @Column(name = "image_url", length = 500)
    private String imageUrl;

    /**
     * @brief Parent category for hierarchical structure (null for root categories)
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_id", foreignKey = @ForeignKey(name = "fk_category_parent"))
    private CategoryEntity parentCategory;

    /**
     * @brief Child categories (subcategories)
     */
    @OneToMany(mappedBy = "parentCategory", cascade = CascadeType.ALL, orphanRemoval = false)
    private Set<CategoryEntity> subcategories = new HashSet<>();

    /**
     * @brief Flag indicating if the category is active
     */
    @Column(name = "is_active", nullable = false)
    @Builder.Default
    private Boolean isActive = Boolean.TRUE;

    /**
     * @brief Display order for the category in listings
     */
    @Column(name = "display_order")
    @Builder.Default
    private Integer displayOrder = 0;

    /**
     * @brief Timestamp when the category was created
     */
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    /**
     * @brief Timestamp when the category was last updated
     */
    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    /**
     * @brief Timestamp when the category was soft deleted (null if not deleted)
     */
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;

    /**
     * @brief Add a subcategory to this category
     * @param subcategory The subcategory to add
     */
    public void addSubcategory(CategoryEntity subcategory) {
        if (subcategory != null) {
            this.subcategories.add(subcategory);
            subcategory.setParentCategory(this);
        }
    }

    /**
     * @brief Remove a subcategory from this category
     * @param subcategory The subcategory to remove
     */
    public void removeSubcategory(CategoryEntity subcategory) {
        if (subcategory != null) {
            this.subcategories.remove(subcategory);
            subcategory.setParentCategory(null);
        }
    }

    /**
     * @brief Check if this category is a root category (no parent)
     * @return true if this is a root category, false otherwise
     */
    public boolean isRootCategory() {
        return this.parentCategory == null;
    }

    /**
     * @brief Get the full category path (e.g., "Electronics > Guitars > Acoustic")
     * @return The full path as a string
     */
    public String getFullPath() {
        StringBuilder path = new StringBuilder(this.name);
        CategoryEntity current = this.parentCategory;
        
        while (current != null) {
            path.insert(0, current.getName() + " > ");
            current = current.getParentCategory();
        }
        
        return path.toString();
    }

}
