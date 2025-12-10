/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Entity class representing a product in the system.
 * @us US-2100 List products within a category - Granularity: Entity Definition
 */
package com.bluevelvet.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.PositiveOrZero;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

/**
 * @brief Entity class representing a product.
 */
@Entity
@Table(name = "products")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Product {

    /**
     * @brief The unique identifier for the product.
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * @brief The name of the product.
     */
    @NotBlank
    @Column(nullable = false)
    private String name;

    /**
     * @brief The description of the product.
     */
    @Column(columnDefinition = "TEXT")
    private String description;

    /**
     * @brief The price of the product.
     */
    @NotNull
    @PositiveOrZero
    @Column(nullable = false)
    private BigDecimal price;

    /**
     * @brief Indicates if the product is enabled.
     */
    private boolean enabled;

    /**
     * @brief Indicates if the product is in stock.
     */
    private boolean inStock;

    /**
     * @brief The images associated with the product.
     */
    @ElementCollection
    @CollectionTable(name = "product_images", joinColumns = @JoinColumn(name = "product_id"))
    @Column(name = "image_file_name")
    private Set<String> images = new HashSet<>();

    /**
     * @brief The category the product belongs to.
     */
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id", nullable = false)
    private Category category;

    /**
     * @brief The timestamp when the product was created.
     */
    @CreationTimestamp
    private LocalDateTime createdTime;

    /**
     * @brief The timestamp when the product was last updated.
     */
    @UpdateTimestamp
    private LocalDateTime updatedTime;

    /**
     * @brief Constructs a new Product with the specified name, price, and category.
     * @param name     The name of the product.
     * @param price    The price of the product.
     * @param category The category of the product.
     */
    public Product(String name, BigDecimal price, Category category) {
        this.name = name;
        this.price = price;
        this.category = category;
    }
}
