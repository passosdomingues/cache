/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Represents a role in the system.
 * @us US-1603 Register new users - Granularity: Role Entity
 */
package com.bluevelvet.auth;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * @brief Entity class representing a user role.
 */
@Entity
@Table(name = "roles")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Role {
    /**
     * @brief The unique identifier for the role.
     */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    /**
     * @brief The name of the role.
     */
    @Enumerated(EnumType.STRING)
    @Column(length = 30)
    private RoleName name;

    /**
     * @brief Constructs a new Role with the specified name.
     * @param name The name of the role.
     */
    public Role(RoleName name) {
        this.name = name;
    }
}
