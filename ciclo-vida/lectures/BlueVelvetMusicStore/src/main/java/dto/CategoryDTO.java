package dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.*;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.Set;

/**
 * @brief Data Transfer Object for Category
 * @details Used for API responses and request payloads
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@EqualsAndHashCode(exclude = {"subcategories"})
@ToString(exclude = {"subcategories"})
public class CategoryDTO implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * @brief Category ID
     */
    private Long id;

    /**
     * @brief Category name
     */
    @NotBlank(message = "Category name cannot be blank")
    @Size(min = 1, max = 255, message = "Category name must be between 1 and 255 characters")
    private String name;

    /**
     * @brief Category description
     */
    private String description;

    /**
     * @brief Image file name
     */
    private String imageFileName;

    /**
     * @brief Image URL
     */
    private String imageUrl;

    /**
     * @brief Parent category ID
     */
    private Long parentId;

    /**
     * @brief Parent category name
     */
    private String parentName;

    /**
     * @brief Is active flag
     */
    @Builder.Default
    private Boolean isActive = Boolean.TRUE;

    /**
     * @brief Display order
     */
    @Builder.Default
    private Integer displayOrder = 0;

    /**
     * @brief Full category path
     */
    private String fullPath;

    /**
     * @brief Subcategories
     */
    private Set<CategoryDTO> subcategories;

    /**
     * @brief Creation timestamp
     */
    private LocalDateTime createdAt;

    /**
     * @brief Last update timestamp
     */
    private LocalDateTime updatedAt;

}
