src/main/java/com/university/restaurant/
├── config/
│   ├── SecurityConfig.java
│   ├── WebMvcConfig.java
│   ├── DataInitializer.java
│   └── ModelMapperConfig.java
├── controller/
│   ├── AuthController.java
│   ├── MenuController.java
│   ├── ReservationController.java
│   └── AdminController.java
├── model/
│   ├── User.java
│   ├── Menu.java
│   ├── Reservation.java
│   ├── WeekDay.java
│   └── MealType.java
├── repository/
│   ├── UserRepository.java
│   ├── MenuRepository.java
│   └── ReservationRepository.java
├── service/
│   ├── UserService.java
│   ├── MenuService.java
│   ├── ReservationService.java
│   └── EmailService.java
├── dto/
│   ├── LoginRequest.java
│   ├── MenuRequest.java
│   ├── ReservationRequest.java
│   └── UserRegistrationDto.java
├── exception/
│   ├── GlobalExceptionHandler.java
│   ├── ResourceNotFoundException.java
│   └── BusinessException.java
└── RestaurantApplication.java