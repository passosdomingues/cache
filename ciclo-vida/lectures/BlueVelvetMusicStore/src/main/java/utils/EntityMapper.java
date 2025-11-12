package utils;

import com.bluevelvet.domain.dto.CategoryDTO;
import com.bluevelvet.domain.dto.UserDTO;
import com.bluevelvet.domain.entity.CategoryEntity;
import com.bluevelvet.domain.entity.UserEntity;
import org.springframework.stereotype.Component;

import java.util.stream.Collectors;

/**
 * @brief Utility class for mapping between entities and DTOs
 * @details Provides static methods for converting domain entities to data transfer objects
 * Follows the Mapper design pattern for clean separation of concerns
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@Component
public class EntityMapper {

    /**
     * @brief Convert CategoryEntity to CategoryDTO
     * @param entity The category entity
     * @return The category DTO
     */
    public static CategoryDTO toCategoryDTO(CategoryEntity entity) {
        if (entity == null) {
            return null;
        }

        return CategoryDTO.builder()
            .id(entity.getId())
            .name(entity.getName())
            .description(entity.getDescription())
            .imageFileName(entity.getImageFileName())
            .imageUrl(entity.getImageUrl())
            .parentId(entity.getParentCategory() != null ? entity.getParentCategory().getId() : null)
            .parentName(entity.getParentCategory() != null ? entity.getParentCategory().getName() : null)
            .isActive(entity.getIsActive())
            .displayOrder(entity.getDisplayOrder())
            .fullPath(entity.getFullPath())
            .subcategories(
                entity.getSubcategories() != null
                    ? entity.getSubcategories().stream()
                        .map(EntityMapper::toCategoryDTO)
                        .collect(Collectors.toSet())
                    : null
            )
            .createdAt(entity.getCreatedAt())
            .updatedAt(entity.getUpdatedAt())
            .build();
    }

    /**
     * @brief Convert UserEntity to UserDTO
     * @param entity The user entity
     * @return The user DTO
     */
    public static UserDTO toUserDTO(UserEntity entity) {
        if (entity == null) {
            return null;
        }

        return UserDTO.builder()
            .id(entity.getId())
            .email(entity.getEmail())
            .fullName(entity.getFullName())
            .pictureUrl(entity.getPictureUrl())
            .oauthProvider(entity.getOauthProvider())
            .roles(
                entity.getRoles() != null
                    ? entity.getRoles().stream()
                        .map(role -> role.getName())
                        .collect(Collectors.toSet())
                    : null
            )
            .isActive(entity.getIsActive())
            .isEmailVerified(entity.getIsEmailVerified())
            .createdAt(entity.getCreatedAt())
            .updatedAt(entity.getUpdatedAt())
            .lastLoginAt(entity.getLastLoginAt())
            .build();
    }

}
