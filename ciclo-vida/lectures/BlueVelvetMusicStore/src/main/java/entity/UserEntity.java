package entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.SoftDelete;
import org.hibernate.annotations.UpdateTimestamp;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.Collection;
import java.util.HashSet;
import java.util.Set;
import java.util.stream.Collectors;

/**
 * @brief JPA Entity representing a user in the Bluevelvet Music Store
 * @details Implements Spring Security's UserDetails for authentication and authorization
 * Supports OAuth2 authentication with Google and role-based access control
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@Entity
@Table(name = "users", indexes = {
    @Index(name = "idx_user_email", columnList = "email", unique = true),
    @Index(name = "idx_user_oauth_id", columnList = "oauth_provider_id"),
    @Index(name = "idx_user_is_active", columnList = "is_active"),
    @Index(name = "idx_user_deleted_at", columnList = "deleted_at")
})
@SoftDelete(columnName = "deleted_at")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
@EqualsAndHashCode(exclude = "roles")
@ToString(exclude = "roles")
public class UserEntity implements UserDetails, Serializable {

    private static final long serialVersionUID = 1L;

    /**
     * @brief Unique identifier for the user
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    /**
     * @brief User's email address - used as username for authentication
     */
    @Column(name = "email", nullable = false, unique = true, length = 255)
    @NotBlank(message = "Email cannot be blank")
    @Email(message = "Email should be valid")
    private String email;

    /**
     * @brief User's full name
     */
    @Column(name = "full_name", nullable = false, length = 255)
    @NotBlank(message = "Full name cannot be blank")
    private String fullName;

    /**
     * @brief User's profile picture URL (from OAuth provider)
     */
    @Column(name = "picture_url", length = 500)
    private String pictureUrl;

    /**
     * @brief OAuth provider identifier (e.g., "google")
     */
    @Column(name = "oauth_provider", length = 50)
    private String oauthProvider;

    /**
     * @brief OAuth provider's unique identifier for this user
     */
    @Column(name = "oauth_provider_id", length = 255)
    private String oauthProviderId;

    /**
     * @brief Hashed password (null if using OAuth)
     */
    @Column(name = "password_hash", length = 255)
    private String passwordHash;

    /**
     * @brief User's roles for authorization
     */
    @ManyToMany(fetch = FetchType.EAGER, cascade = CascadeType.PERSIST)
    @JoinTable(
        name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id", foreignKey = @ForeignKey(name = "fk_user_roles_user")),
        inverseJoinColumns = @JoinColumn(name = "role_id", foreignKey = @ForeignKey(name = "fk_user_roles_role"))
    )
    private Set<RoleEntity> roles = new HashSet<>();

    /**
     * @brief Flag indicating if the user account is active
     */
    @Column(name = "is_active", nullable = false)
    @Builder.Default
    private Boolean isActive = Boolean.TRUE;

    /**
     * @brief Flag indicating if the user's email is verified
     */
    @Column(name = "is_email_verified", nullable = false)
    @Builder.Default
    private Boolean isEmailVerified = Boolean.FALSE;

    /**
     * @brief Timestamp when the user account was created
     */
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    /**
     * @brief Timestamp when the user account was last updated
     */
    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    /**
     * @brief Timestamp of the last login
     */
    @Column(name = "last_login_at")
    private LocalDateTime lastLoginAt;

    /**
     * @brief Timestamp when the user account was soft deleted (null if not deleted)
     */
    @Column(name = "deleted_at")
    private LocalDateTime deletedAt;

    /**
     * @brief Get authorities granted to the user
     * @return Collection of granted authorities
     */
    @Override
    public Collection<? extends GrantedAuthority> getAuthorities() {
        return this.roles.stream()
            .map(role -> new SimpleGrantedAuthority("ROLE_" + role.getName()))
            .collect(Collectors.toSet());
    }

    /**
     * @brief Get the password (not used for OAuth users)
     * @return The password hash or null
     */
    @Override
    public String getPassword() {
        return this.passwordHash;
    }

    /**
     * @brief Get the username (email)
     * @return The user's email
     */
    @Override
    public String getUsername() {
        return this.email;
    }

    /**
     * @brief Check if the account is not expired
     * @return true if the account is valid
     */
    @Override
    public boolean isAccountNonExpired() {
        return true;
    }

    /**
     * @brief Check if the account is not locked
     * @return true if the account is not locked
     */
    @Override
    public boolean isAccountNonLocked() {
        return this.isActive;
    }

    /**
     * @brief Check if the credentials are not expired
     * @return true if the credentials are valid
     */
    @Override
    public boolean isCredentialsNonExpired() {
        return true;
    }

    /**
     * @brief Check if the user is enabled
     * @return true if the user is enabled
     */
    @Override
    public boolean isEnabled() {
        return this.isActive;
    }

    /**
     * @brief Add a role to the user
     * @param role The role to add
     */
    public void addRole(RoleEntity role) {
        if (role != null) {
            this.roles.add(role);
        }
    }

    /**
     * @brief Remove a role from the user
     * @param role The role to remove
     */
    public void removeRole(RoleEntity role) {
        if (role != null) {
            this.roles.remove(role);
        }
    }

    /**
     * @brief Check if the user has a specific role
     * @param roleName The name of the role to check
     * @return true if the user has the role, false otherwise
     */
    public boolean hasRole(String roleName) {
        return this.roles.stream()
            .anyMatch(role -> role.getName().equalsIgnoreCase(roleName));
    }

    /**
     * @brief Check if the user is an administrator
     * @return true if the user has the ADMIN role
     */
    public boolean isAdmin() {
        return hasRole("ADMIN");
    }

}
