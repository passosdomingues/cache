/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025 December 10 (Wed)
 * @brief Main application class for Blue Velvet Music Store.
 * @us US-0000 Project Configuration - Granularity: Application Entry Point
 */
package com.bluevelvet;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * @brief Entry point for the Spring Boot application.
 */
@SpringBootApplication
public class BlueVelvetMusicStoreApplication {

	/**
	 * @brief Main method to start the application.
	 * @param args Command line arguments.
	 */
	public static void main(String[] args) {
		SpringApplication.run(BlueVelvetMusicStoreApplication.class, args);
	}

}
