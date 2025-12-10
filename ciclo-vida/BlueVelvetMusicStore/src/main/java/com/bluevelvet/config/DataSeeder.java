package com.bluevelvet.config;

import com.bluevelvet.entity.Category;
import com.bluevelvet.entity.Product;
import com.bluevelvet.repository.CategoryRepository;
import com.bluevelvet.repository.ProductRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

/**
 * @author Rafael Passos Domingues
 * @lastUpdate 2025-12-10
 * @brief Data seeder to populate initial categories and products
 * @us US-0000 Project Configuration - Granularity: Data Seeding
 */
@Configuration
public class DataSeeder {

        @Bean
        CommandLineRunner initDatabase(CategoryRepository categoryRepository, ProductRepository productRepository) {
                return args -> {
                        // Only seed if database is empty
                        if (categoryRepository.count() > 0) {
                                return;
                        }

                        // Create Categories
                        Category guitars = createCategory("Guitars", "Electric and acoustic guitars", true, null);
                        Category keyboards = createCategory("Keyboards", "Pianos and synthesizers", true, null);
                        Category drums = createCategory("Drums", "Acoustic and electronic drum kits", true, null);
                        Category microphones = createCategory("Microphones", "Studio and live microphones", true, null);
                        Category accessories = createCategory("Accessories", "Cables, stands, and more", true, null);

                        List<Category> categories = Arrays.asList(guitars, keyboards, drums, microphones, accessories);
                        categoryRepository.saveAll(categories);

                        // Create Products
                        List<Product> products = Arrays.asList(
                                        // Guitars
                                        createProduct("Fender Stratocaster",
                                                        "Classic electric guitar with versatile tone and iconic design. Features three single-coil pickups and a smooth maple neck.",
                                                        new BigDecimal("1499.00"), guitars, true, true,
                                                        "https://via.placeholder.com/400x400/1E90FF/FFFFFF?text=Fender+Stratocaster"),

                                        createProduct("Gibson Les Paul Standard",
                                                        "Premium electric guitar with rich, warm tone. Mahogany body with maple top and dual humbucking pickups.",
                                                        new BigDecimal("2499.00"), guitars, true, true,
                                                        "https://via.placeholder.com/400x400/8B4513/FFFFFF?text=Gibson+Les+Paul"),

                                        createProduct("Taylor 214ce Acoustic",
                                                        "Beautiful acoustic-electric guitar with solid Sitka spruce top. Perfect for stage and studio.",
                                                        new BigDecimal("899.00"), guitars, true, true,
                                                        "https://via.placeholder.com/400x400/D2691E/FFFFFF?text=Taylor+Acoustic"),

                                        createProduct("Ibanez RG Series",
                                                        "High-performance electric guitar designed for rock and metal. Fast neck and powerful pickups.",
                                                        new BigDecimal("699.00"), guitars, true, true,
                                                        "https://via.placeholder.com/400x400/FF4500/FFFFFF?text=Ibanez+RG"),

                                        // Keyboards
                                        createProduct("Yamaha P-125 Digital Piano",
                                                        "88-key weighted digital piano with authentic piano sound. Portable and perfect for beginners.",
                                                        new BigDecimal("649.99"), keyboards, true, true,
                                                        "https://via.placeholder.com/400x400/000000/FFFFFF?text=Yamaha+Piano"),

                                        createProduct("Roland JUNO-DS61 Synthesizer",
                                                        "Versatile 61-key synthesizer with hundreds of sounds. Great for live performance and production.",
                                                        new BigDecimal("799.00"), keyboards, true, true,
                                                        "https://via.placeholder.com/400x400/DC143C/FFFFFF?text=Roland+JUNO"),

                                        createProduct("Korg Minilogue XD",
                                                        "Analog synthesizer with digital multi-engine. Compact and powerful sound design tool.",
                                                        new BigDecimal("649.00"), keyboards, true, true,
                                                        "https://via.placeholder.com/400x400/4B0082/FFFFFF?text=Korg+Minilogue"),

                                        // Drums
                                        createProduct("Roland TD-17KV Electronic Drum Kit",
                                                        "Complete electronic drum kit with mesh heads. Perfect for practice and recording.",
                                                        new BigDecimal("1199.99"), drums, true, true,
                                                        "https://via.placeholder.com/400x400/2F4F4F/FFFFFF?text=Roland+Drums"),

                                        createProduct("Pearl Export 5-Piece Drum Set",
                                                        "Professional acoustic drum kit with hardware included. Great tone and durability.",
                                                        new BigDecimal("899.00"), drums, true, true,
                                                        "https://via.placeholder.com/400x400/696969/FFFFFF?text=Pearl+Drums"),

                                        createProduct("Alesis Nitro Mesh Kit",
                                                        "Affordable electronic drum kit with mesh heads. Ideal for beginners.",
                                                        new BigDecimal("399.00"), drums, true, true,
                                                        "https://via.placeholder.com/400x400/708090/FFFFFF?text=Alesis+Drums"),

                                        // Microphones
                                        createProduct("Shure SM7B",
                                                        "Industry-standard dynamic microphone for vocals and instruments. Used in top studios worldwide.",
                                                        new BigDecimal("399.00"), microphones, true, true,
                                                        "https://via.placeholder.com/400x400/000000/FFFFFF?text=Shure+SM7B"),

                                        createProduct("Audio-Technica AT2020",
                                                        "Versatile condenser microphone for studio recording. Excellent value and sound quality.",
                                                        new BigDecimal("99.00"), microphones, true, true,
                                                        "https://via.placeholder.com/400x400/4682B4/FFFFFF?text=AT2020"),

                                        createProduct("Rode NT1-A",
                                                        "Ultra-quiet condenser microphone with warm sound. Perfect for vocals and acoustic instruments.",
                                                        new BigDecimal("229.00"), microphones, true, true,
                                                        "https://via.placeholder.com/400x400/FFD700/000000?text=Rode+NT1-A"),

                                        // Accessories
                                        createProduct("Mogami Gold Instrument Cable 20ft",
                                                        "Professional-grade instrument cable with superior shielding. Lifetime warranty.",
                                                        new BigDecimal("79.99"), accessories, true, true,
                                                        "https://via.placeholder.com/400x400/FFD700/000000?text=Mogami+Cable"),

                                        createProduct("K&M Guitar Stand",
                                                        "Sturdy and reliable guitar stand with padded yoke. Folds for easy transport.",
                                                        new BigDecimal("29.99"), accessories, true, true,
                                                        "https://via.placeholder.com/400x400/A9A9A9/FFFFFF?text=Guitar+Stand"),

                                        createProduct("Ernie Ball Regular Slinky Strings",
                                                        "Classic electric guitar strings with balanced tone. Trusted by professionals.",
                                                        new BigDecimal("5.99"), accessories, true, true,
                                                        "https://via.placeholder.com/400x400/FF6347/FFFFFF?text=Guitar+Strings"));

                        productRepository.saveAll(products);

                        System.out.println(
                                        " Database seeded with " + categories.size() + " categories and "
                                                        + products.size() + " products");
                };
        }

        private Category createCategory(String name, String imageFileName, boolean enabled, Category parent) {
                Category category = new Category();
                category.setName(name);
                category.setImageFileName(imageFileName);
                category.setEnabled(enabled);
                category.setParent(parent);
                return category;
        }

        private Product createProduct(String name, String description, BigDecimal price,
                        Category category, boolean enabled, boolean inStock, String... imageUrls) {
                Product product = new Product();
                product.setName(name);
                product.setDescription(description);
                product.setPrice(price);
                product.setCategory(category);
                product.setEnabled(enabled);
                product.setInStock(inStock);
                product.setCreatedTime(LocalDateTime.now());
                product.setUpdatedTime(LocalDateTime.now());

                // Add images
                if (imageUrls != null && imageUrls.length > 0) {
                        for (String url : imageUrls) {
                                product.getImages().add(url);
                        }
                }

                return product;
        }
}
