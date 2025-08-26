package com.university.restaurant.service;

import com.university.restaurant.model.Reservation;
import com.university.restaurant.model.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessageHelper;
import org.springframework.stereotype.Service;
import org.thymeleaf.TemplateEngine;
import org.thymeleaf.context.Context;

import jakarta.mail.MessagingException;
import jakarta.mail.internet.MimeMessage;

/**
 * Service for sending emails
 */
@Service
public class EmailService {
    
    @Autowired
    private JavaMailSender mailSender;
    
    @Autowired
    private TemplateEngine templateEngine;
    
    /**
     * Send reservation confirmation email
     */
    public void sendReservationConfirmation(User user, Reservation reservation) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            
            Context context = new Context();
            context.setVariable("user", user);
            context.setVariable("reservation", reservation);
            
            String htmlContent = templateEngine.process("email/reservation-confirmation", context);
            
            helper.setTo(user.getEmail());
            helper.setSubject("Reservation Confirmation - University Restaurant");
            helper.setText(htmlContent, true);
            
            mailSender.send(message);
        } catch (MessagingException e) {
            // Fallback to simple email
            sendSimpleReservationConfirmation(user, reservation);
        }
    }
    
    /**
     * Simple email fallback
     */
    private void sendSimpleReservationConfirmation(User user, Reservation reservation) {
        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(user.getEmail());
        message.setSubject("Reservation Confirmation - University Restaurant");
        
        String text = String.format(
            "Hello %s,\n\nYour reservation has been confirmed!\n\n" +
            "Reservation Details:\n" +
            "Date: %s\n" +
            "Meal: %s\n" +
            "Menu: %s\n\n" +
            "Thank you for using our reservation system.\n\n" +
            "University Restaurant Team",
            user.getName(),
            reservation.getReservationDate().toString(),
            reservation.getMenu().getMealType().getDisplayName(),
            reservation.isVegan() ? reservation.getMenu().getVeganOption() : 
                (reservation.isVegetarian() ? reservation.getMenu().getVegetarianOption() : 
                reservation.getMenu().getDescription())
        );
        
        message.setText(text);
        mailSender.send(message);
    }
    
    /**
     * Send reservation cancellation email
     */
    public void sendReservationCancellation(User user, Reservation reservation) {
        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(user.getEmail());
        message.setSubject("Reservation Cancellation - University Restaurant");
        
        String text = String.format(
            "Hello %s,\n\nYour reservation for %s (%s) has been cancelled.\n\n" +
            "University Restaurant Team",
            user.getName(),
            reservation.getReservationDate().toString(),
            reservation.getMenu().getMealType().getDisplayName()
        );
        
        message.setText(text);
        mailSender.send(message);
    }
    
    /**
     * Send daily menu notification
     */
    public void sendDailyMenuNotification(User user, java.util.List<Menu> todaysMenu) {
        try {
            MimeMessage message = mailSender.createMimeMessage();
            MimeMessageHelper helper = new MimeMessageHelper(message, true, "UTF-8");
            
            Context context = new Context();
            context.setVariable("user", user);
            context.setVariable("menus", todaysMenu);
            context.setVariable("today", LocalDate.now());
            
            String htmlContent = templateEngine.process("email/daily-menu", context);
            
            helper.setTo(user.getEmail());
            helper.setSubject("Today's Menu - University Restaurant");
            helper.setText(htmlContent, true);
            
            mailSender.send(message);
        } catch (MessagingException e) {
            // Log error but don't throw exception
            System.err.println("Failed to send daily menu notification: " + e.getMessage());
        }
    }
}