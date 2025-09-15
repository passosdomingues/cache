package com.university.restaurant.service;

import com.university.restaurant.model.User;
import com.university.restaurant.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Optional;

/**
 * Service for user-related operations
 */
@Service
public class UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private PasswordEncoder passwordEncoder;
    
    /**
     * Register a new user
     */
    public User registerUser(User user) {
        if (userRepository.existsByEmail(user.getEmail())) {
            throw new IllegalArgumentException("Email is already in use");
        }
        
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        return userRepository.save(user);
    }
    
    /**
     * Find user by email
     */
    public Optional<User> findByEmail(String email) {
        return userRepository.findByEmail(email);
    }
    
    /**
     * Validate user credentials
     */
    public boolean validateCredentials(String email, String password) {
        Optional<User> userOpt = userRepository.findByEmail(email);
        return userOpt.isPresent() && passwordEncoder.matches(password, userOpt.get().getPassword());
    }
    
    /**
     * Check if admin user exists
     */
    public boolean adminUserExists() {
        return userRepository.countByAdministratorTrue() > 0;
    }
    
    /**
     * Create the first admin user
     */
    public User createFirstAdmin(User user) {
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        user.setAdministrator(true);
        return userRepository.save(user);
    }
    
    /**
     * Update user profile
     */
    public User updateUserProfile(Long userId, User userDetails) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("User not found"));
        
        user.setName(userDetails.getName());
        user.setVegetarian(userDetails.isVegetarian());
        user.setVegan(userDetails.isVegan());
        user.setDietaryRestrictions(userDetails.getDietaryRestrictions());
        
        return userRepository.save(user);
    }
}