package com.bluevelvet.category;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CategoryRepository extends JpaRepository<Category, Long> {
    boolean existsByName(String name);
    
    // Find root categories (where parent is null)
    List<Category> findByParentIsNull();
    
    // Find root categories with pagination
    Page<Category> findByParentIsNull(Pageable pageable);
    
    // Find all categories sorted by name
    List<Category> findAllByOrderByNameAsc();
}
