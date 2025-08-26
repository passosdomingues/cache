package com.university.restaurant.repository;

import com.university.restaurant.model.Menu;
import com.university.restaurant.model.WeekDay;
import com.university.restaurant.model.MealType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

/**
 * Repository for menu operations
 */
@Repository
public interface MenuRepository extends JpaRepository<Menu, Long> {
    
    @Query("SELECT m FROM Menu m WHERE m.weekDay = :weekDay AND m.mealType = :mealType " +
           "AND m.validFrom <= :date AND m.validTo >= :date AND m.active = true")
    List<Menu> findByWeekDayAndMealTypeAndDate(@Param("weekDay") WeekDay weekDay, 
                                              @Param("mealType") MealType mealType, 
                                              @Param("date") LocalDate date);
    
    @Query("SELECT m FROM Menu m WHERE m.active = true AND m.validTo >= CURRENT_DATE " +
           "ORDER BY m.weekDay, m.mealType")
    List<Menu> findActiveMenusOrdered();
    
    @Query("SELECT m FROM Menu m WHERE m.weekDay = :weekDay AND m.mealType = :mealType " +
           "AND m.validFrom <= :date AND m.validTo >= :date AND m.active = true")
    Menu findActiveMenu(@Param("weekDay") WeekDay weekDay, 
                       @Param("mealType") MealType mealType, 
                       @Param("date") LocalDate date);
    
    @Query("SELECT m FROM Menu m WHERE m.validFrom <= :endDate AND m.validTo >= :startDate " +
           "AND m.active = true ORDER BY m.validFrom, m.weekDay, m.mealType")
    List<Menu> findMenusBetweenDates(@Param("startDate") LocalDate startDate, 
                                    @Param("endDate") LocalDate endDate);
    
    @Query("SELECT m FROM Menu m WHERE m.validFrom <= :date AND m.validTo >= :date " +
           "AND m.active = true ORDER BY m.mealType")
    List<Menu> findMenusForDate(@Param("date") LocalDate date);
}