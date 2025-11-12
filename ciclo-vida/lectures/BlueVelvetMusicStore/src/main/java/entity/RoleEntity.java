package entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;

/**
 * @brief JPA Entity representing a user role in the Bluevelvet Music Store
 * @details Implements role-based access control (RBAC) for authorization
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@Entity
@Table(name = "roles", indexes = {
    @Index(name = "idx_role_name", columnList = "name", unique = true)
})
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@EqualsAndHashCode(exclude = "users")
@ToString(exclude = "users")
public class RoleEntity implements Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * @brief Unique identifier for the role
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    /**
     * @brief Role name (e.g., ADMIN, USER, MANAGER)
     */
    @Column(name = "name", nullable = false, unique = true, length = 50)
    @NotBlank(message = "Role name cannot be blank")
    private String name;

    /**
     * @brief Role description
     */
    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    /**
     * @brief Users assigned to this role
     */
    @ManyToMany(mappedBy = "roles", fetch = FetchType.LAZY)
    private Set<UserEntity> users = new HashSet<>();

    /**
     * @brief Timestamp when the role was created
     */
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    /**
     * @brief Timestamp when the role was last updated
     */
    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    /**
     * @brief Predefined role constants
     */
    public static class RoleNames {
        public static final String ADMIN = "ADMIN";
        public static final String MANAGER = "MANAGER";
        public static final String USER = "USER";
        public static final String GUEST = "GUEST";
    }

}
