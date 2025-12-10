/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Entity class representing a product category in the system
 * @us US-1306 Create category of products - Granularity: Entity Definition
 * @us US-1307 Edit category of products - Granularity: Entity Definition
 * @us US-0904 Delete category of products - Granularity: Entity Definition
 * @us US-2100 List products within a category - Granularity: Entity Definition
 */
package com.bluevelvet.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import java.util.ArrayList;
import java.util.List;

/**
 * @brief Defines the category structure with hierarchical support for
 *        subcategories
 */
@Entity
@Table(name = "categories")
public class Category {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Size(max = 100)
    @Column(name = "name", unique = true, nullable = false)
    private String name;

    @Column(name = "image_file_name")
    private String imageFileName;

    @Column(name = "enabled", nullable = false)
    private Boolean enabled = true;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_id")
    @com.fasterxml.jackson.annotation.JsonBackReference
    private Category parent;

    @OneToMany(mappedBy = "parent", cascade = CascadeType.ALL)
    @com.fasterxml.jackson.annotation.JsonManagedReference
    private List<Category> children = new ArrayList<>();

    /**
     * @brief Default constructor for JPA
     */
    public Category() {
    }

    /**
     * @brief Parameterized constructor for creating category instances
     * @param categoryName          The name of the category
     * @param categoryImageFileName The filename of the category image
     * @param categoryEnabled       The enabled status of the category
     * @param categoryParent        The parent category for hierarchical structure
     */
    public Category(String categoryName, String categoryImageFileName, Boolean categoryEnabled,
            Category categoryParent) {
        this.name = categoryName;
        this.imageFileName = categoryImageFileName;
        this.enabled = categoryEnabled;
        this.parent = categoryParent;
    }

    /**
     * @brief Parameterized constructor for basic category creation
     * @param categoryName The name of the category
     */
    public Category(String categoryName) {
        this.name = categoryName;
        this.enabled = true;
    }

    /**
     * @brief Parameterized constructor for creating a subcategory
     * @param categoryName The name of the category
     * @param parent       The parent category
     */
    public Category(String categoryName, Category parent) {
        this.name = categoryName;
        this.parent = parent;
        this.enabled = true;
    }

    // Getters and Setters with JavaDoc

    /**
     * @brief Retrieves the category identifier
     * @return Long representing the unique category ID
     */
    public Long getId() {
        return id;
    }

    /**
     * @brief Sets the category identifier
     * @param categoryId The unique identifier for the category
     */
    public void setId(Long categoryId) {
        this.id = categoryId;
    }

    /**
     * @brief Retrieves the category name
     * @return String containing the category name
     */
    public String getName() {
        return name;
    }

    /**
     * @brief Sets the category name
     * @param categoryName The name to set for the category
     */
    public void setName(String categoryName) {
        this.name = categoryName;
    }

    /**
     * @brief Retrieves the category image filename
     * @return String containing the image filename
     */
    public String getImageFileName() {
        return imageFileName;
    }

    /**
     * @brief Sets the category image filename
     * @param categoryImageFileName The image filename to associate with the
     *                              category
     */
    public void setImageFileName(String categoryImageFileName) {
        this.imageFileName = categoryImageFileName;
    }

    /**
     * @brief Retrieves the enabled status of the category
     * @return Boolean indicating if the category is enabled
     */
    public Boolean getEnabled() {
        return enabled;
    }

    /**
     * @brief Sets the enabled status of the category
     * @param categoryEnabled The enabled status to set for the category
     */
    public void setEnabled(Boolean categoryEnabled) {
        this.enabled = categoryEnabled;
    }

    /**
     * @brief Retrieves the parent category
     * @return Category object representing the parent, or null if root category
     */
    public Category getParent() {
        return parent;
    }

    /**
     * @brief Sets the parent category
     * @param categoryParent The parent category to set for hierarchical structure
     */
    public void setParent(Category categoryParent) {
        this.parent = categoryParent;
    }

    /**
     * @brief Retrieves the children categories
     * @return List of child categories
     */
    public List<Category> getChildren() {
        return children;
    }

    /**
     * @brief Sets the children categories
     * @param children The list of child categories
     */
    public void setChildren(List<Category> children) {
        this.children = children;
    }

    /**
     * @brief Generates string representation of the category
     * @return String containing category details
     */
    @Override
    public String toString() {
        return "Category{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", imageFileName='" + imageFileName + '\'' +
                ", enabled=" + enabled +
                ", parent=" + (parent != null ? parent.getName() : "null") +
                '}';
    }
}
