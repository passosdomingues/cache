package com.university.restaurant.controller;

import com.university.restaurant.model.Menu;
import com.university.restaurant.model.WeekDay;
import com.university.restaurant.model.MealType;
import com.university.restaurant.model.User;
import com.university.restaurant.service.MenuService;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;

/**
 * Controller for menu-related operations
 */
@Controller
public class MenuController {
    
    @Autowired
    private MenuService menuService;
    
    /**
     * Display the weekly menu
     */
    @GetMapping("/menu")
    public String showMenu(Model model, HttpSession session,
                         @RequestParam(value = "week", required = false) 
                         @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate weekStart) {
        
        User user = (User) session.getAttribute("user");
        if (user != null) {
            model.addAttribute("user", user);
        }
        
        if (weekStart == null) {
            weekStart = LocalDate.now();
            // Adjust to Monday of the current week
            weekStart = weekStart.minusDays(weekStart.getDayOfWeek().getValue() - 1);
        }
        
        List<Menu> weeklyMenu = menuService.getWeeklyMenu(weekStart);
        model.addAttribute("weeklyMenu", weeklyMenu);
        model.addAttribute("weekStart", weekStart);
        model.addAttribute("weekDays", WeekDay.values());
        model.addAttribute("mealTypes", MealType.values());
        
        return "menu";
    }
    
    /**
     * Display today's menu
     */
    @GetMapping("/menu/today")
    public String showTodaysMenu(Model model, HttpSession session) {
        User user = (User) session.getAttribute("user");
        if (user != null) {
            model.addAttribute("user", user);
        }
        
        List<Menu> todaysMenu = menuService.getTodaysMenu();
        model.addAttribute("todaysMenu", todaysMenu);
        model.addAttribute("today", LocalDate.now());
        
        return "menu-today";
    }
    
    /**
     * Display menu for a specific day
     */
    @GetMapping("/menu/day")
    public String showMenuForDay(@RequestParam("day") WeekDay day,
                                Model model, HttpSession session) {
        User user = (User) session.getAttribute("user");
        if (user != null) {
            model.addAttribute("user", user);
        }
        
        // Get menu for each meal type for the requested day
        Arrays.stream(MealType.values()).forEach(mealType -> {
            Menu menu = menuService.getMenu(day, mealType).orElse(null);
            model.addAttribute(mealType.name().toLowerCase(), menu);
        });
        
        model.addAttribute("day", day);
        
        return "menu-day";
    }
}