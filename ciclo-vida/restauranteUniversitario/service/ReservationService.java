package com.university.restaurant.service;

import com.university.restaurant.model.Menu;
import com.university.restaurant.model.Reservation;
import com.university.restaurant.model.User;
import com.university.restaurant.repository.MenuRepository;
import com.university.restaurant.repository.ReservationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

/**
 * Service for reservation-related operations
 */
@Service
public class ReservationService {
    
    @Autowired
    private ReservationRepository reservationRepository;
    
    @Autowired
    private MenuRepository menuRepository;
    
    @Autowired
    private EmailService emailService;
    
    /**
     * Create a new reservation
     */
    public Reservation createReservation(User user, Long menuId, LocalDate reservationDate) {
        Menu menu = menuRepository.findById(menuId)
                .orElseThrow(() -> new IllegalArgumentException("Menu not found"));
        
        // Check if user already has a reservation for the same meal type on the same day
        List<Reservation> existingReservations = reservationRepository
                .findByUserAndReservationDateAndMealType(user, reservationDate, menu.getMealType());
        
        if (!existingReservations.isEmpty()) {
            throw new IllegalArgumentException("You already have a reservation for this meal on the selected date");
        }
        
        // Check capacity limits (example: max 200 reservations per meal)
        long reservationCount = reservationRepository
                .countByReservationDateAndMealType(reservationDate, menu.getMealType());
        
        if (reservationCount >= 200) {
            throw new IllegalArgumentException("Sorry, this meal is fully booked");
        }
        
        Reservation reservation = new Reservation();
        reservation.setUser(user);
        reservation.setMenu(menu);
        reservation.setReservationDate(reservationDate);
        reservation.setVegetarian(user.isVegetarian());
        reservation.setVegan(user.isVegan());
        
        Reservation savedReservation = reservationRepository.save(reservation);
        
        // Send confirmation email
        emailService.sendReservationConfirmation(user, savedReservation);
        
        return savedReservation;
    }
    
    /**
     * Cancel a reservation
     */
    public Reservation cancelReservation(Long reservationId, User user) {
        Reservation reservation = reservationRepository.findById(reservationId)
                .orElseThrow(() -> new IllegalArgumentException("Reservation not found"));
        
        if (!reservation.getUser().getId().equals(user.getId()) && !user.isAdministrator()) {
            throw new IllegalArgumentException("You can only cancel your own reservations");
        }
        
        reservation.setStatus(Reservation.Status.CANCELLED);
        Reservation cancelledReservation = reservationRepository.save(reservation);
        
        // Send cancellation email
        emailService.sendReservationCancellation(reservation.getUser(), cancelledReservation);
        
        return cancelledReservation;
    }
    
    /**
     * Get user's reservations
     */
    public List<Reservation> getUserReservations(User user) {
        return reservationRepository.findByUser(user);
    }
    
    /**
     * Get reservations for a specific date
     */
    public List<Reservation> getReservationsForDate(LocalDate date) {
        return reservationRepository.findByReservationDate(date);
    }
    
    /**
     * Check in a user for their reservation
     */
    public Reservation checkIn(Long reservationId) {
        Reservation reservation = reservationRepository.findById(reservationId)
                .orElseThrow(() -> new IllegalArgumentException("Reservation not found"));
        
        reservation.setStatus(Reservation.Status.CHECKED_IN);
        return reservationRepository.save(reservation);
    }
    
    /**
     * Get reservation statistics for a date range
     */
    public ReservationStats getReservationStats(LocalDate startDate, LocalDate endDate) {
        List<Reservation> reservations = reservationRepository
                .findByReservationDateBetween(startDate, endDate);
        
        ReservationStats stats = new ReservationStats();
        stats.setTotalReservations(reservations.size());
        stats.setVegetarianCount((int) reservations.stream()
                .filter(Reservation::isVegetarian).count());
        stats.setVeganCount((int) reservations.stream()
                .filter(Reservation::isVegan).count());
        
        return stats;
    }
    
    /**
     * Inner class for reservation statistics
     */
    public static class ReservationStats {
        private int totalReservations;
        private int vegetarianCount;
        private int veganCount;
        
        // Getters and setters
        public int getTotalReservations() { return totalReservations; }
        public void setTotalReservations(int totalReservations) { this.totalReservations = totalReservations; }
        
        public int getVegetarianCount() { return vegetarianCount; }
        public void setVegetarianCount(int vegetarianCount) { this.vegetarianCount = vegetarianCount; }
        
        public int getVeganCount() { return veganCount; }
        public void setVeganCount(int veganCount) { this.veganCount = veganCount; }
    }
}