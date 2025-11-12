package repository;

import com.bluevelvet.domain.entity.RoleEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * @brief Repository interface for RoleEntity
 * @details Provides database access operations for roles
 * Extends JpaRepository for CRUD operations
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@Repository
public interface RoleRepository extends JpaRepository<RoleEntity, Long> {

    /**
     * @brief Find a role by name
     * @param name The role name
     * @return Optional containing the role if found
     */
    Optional<RoleEntity> findByName(String name);

}
