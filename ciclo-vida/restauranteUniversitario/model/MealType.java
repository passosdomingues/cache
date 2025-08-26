package com.university.restaurant.model;

/**
 * Meal type enumeration
 */
public enum MealType {
    BREAKFAST("Breakfast"),
    LUNCH("Lunch"),
    DINNER("Dinner");
    
    private final String displayName;
    
    MealType(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() {
        return displayName;
    }
}