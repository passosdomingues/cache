import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.transaction.annotation.EnableTransactionManagement;

/**
 * @brief Main Spring Boot application class for Bluevelvet Music Store
 * @details This is the entry point for the enterprise-grade e-commerce platform
 * featuring Spring Boot 3.2, Jakarta EE, Spring Data JPA, and Spring Security with OAuth2
 * 
 * @author Rafael Passos Domingues
 * @version 1.0.0
 * @since 2025-01-01
 */
@SpringBootApplication
@EnableJpaRepositories(basePackages = "repository")
@EnableTransactionManagement
@ComponentScan(basePackages = "utils")
public class BluevelvetMusicStoreApplication {

    /**
     * @brief Application entry point
     * @param args Command line arguments
     */
    public static void main(String[] args) {
        SpringApplication.run(BluevelvetMusicStoreApplication.class, args);
    }

}
