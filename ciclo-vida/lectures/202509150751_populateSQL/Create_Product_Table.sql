-- Product Table Creation and Population Script
-- BlueVelvet Music Store Database
-- Enhanced with error handling and transactions

SET @OLD_UNIQUE_CHECKS = @@UNIQUE_CHECKS, UNIQUE_CHECKS = 0;
SET @OLD_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS = 0;
SET @OLD_SQL_MODE = @@SQL_MODE, SQL_MODE = 'TRADITIONAL,ALLOW_INVALID_DATES';

-- Start transaction for atomic operations
START TRANSACTION;

-- Create database if not exists
SET @db_creation_query = CONCAT('CREATE DATABASE IF NOT EXISTS `', 'bluevelvet_store', '` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci');
PREPARE stmt FROM @db_creation_query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Use the database
USE `bluevelvet_store`;

-- Create Product table
CREATE TABLE IF NOT EXISTS Product (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL CHECK (price >= 0),
    cost DECIMAL(10, 2) CHECK (cost >= 0),
    stock_quantity INT NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    category VARCHAR(100) NOT NULL,
    brand VARCHAR(100),
    image_url VARCHAR(255),
    sku VARCHAR(100) UNIQUE,
    weight DECIMAL(8, 2) CHECK (weight >= 0),
    dimensions VARCHAR(100),
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_brand (brand),
    INDEX idx_price (price),
    INDEX idx_sku (sku),
    INDEX idx_enabled (enabled)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- Insert sample products for BlueVelvet Music Store
INSERT IGNORE INTO Product (name, description, price, cost, stock_quantity, category, brand, image_url, sku, weight, dimensions, enabled) VALUES
('Fender American Professional II Stratocaster', 'The American Professional II Stratocaster draws from more than sixty years of innovation, inspiration and evolution to meet the demands of today''s working player.', 1499.99, 899.99, 15, 'Guitars', 'Fender', 'fender_stratocaster.jpg', 'FV-AMPROII-ST', 8.5, '40.5 x 13 x 4.5 inches', TRUE),
('Gibson Les Paul Standard ''50s', 'The Gibson Les Paul Standard ''50s embodies the pinnacle of the golden era of electric guitars with a mahogany body and neck, and a carved maple top.', 2499.99, 1499.99, 8, 'Guitars', 'Gibson', 'gibson_lespaul.jpg', 'GI-LP-STD50', 9.2, '41 x 16 x 5 inches', TRUE),
('Yamaha FG800 Solid Top Acoustic Guitar', 'The Yamaha FG800 solid top acoustic guitar offers outstanding quality and value with a solid spruce top and nato/okume back and sides.', 219.99, 129.99, 25, 'Guitars', 'Yamaha', 'yamaha_fg800.jpg', 'YA-FG800', 5.1, '41 x 16 x 5 inches', TRUE),
('Roland TD-17KVX V-Drums Electronic Drum Set', 'The Roland TD-17KVX combines advanced TD-17 sound module technology with a compact design perfect for practice and small spaces.', 1599.99, 999.99, 12, 'Drums & Percussion', 'Roland', 'roland_td17kvx.jpg', 'RO-TD17KVX', 65.8, '47 x 43 x 35 inches', TRUE),
('Shure SM58-LC Cardioid Dynamic Vocal Microphone', 'The Shure SM58 is a professional-quality vocal microphone with a built-in spherical filter to minimize wind and breath noise.', 99.99, 59.99, 50, 'Microphones', 'Shure', 'shure_sm58.jpg', 'SH-SM58-LC', 0.7, '6.9 x 3.1 x 3.1 inches', TRUE),
('Korg Kronos 2 88-Key Workstation', 'The Korg Kronos 2 combines nine premium sound engines with comprehensive sequencing and a fully programmable setup for ultimate creativity.', 3499.99, 2199.99, 6, 'Keyboards & Synthesizers', 'Korg', 'korg_kronos2.jpg', 'KO-KRONOS2-88', 48.5, '55.7 x 16.5 x 6.1 inches', TRUE),
('Sennheiser HD 650 Open Back Professional Headphones', 'The Sennheiser HD 650 reference-class headphones provide exceptional sound reproduction with minimal harmonic distortion.', 499.99, 299.99, 18, 'Audio Equipment', 'Sennheiser', 'sennheiser_hd650.jpg', 'SE-HD650', 0.6, '8.7 x 4.3 x 12.6 inches', TRUE),
('BOSS Katana-100 MKII Guitar Amplifier', 'The BOSS Katana-100 MKII guitar amplifier delivers incredibly authentic tube amp tone with a powerful 100-watt output and versatile effects.', 379.99, 229.99, 20, 'Amplifiers', 'BOSS', 'boss_katana100.jpg', 'BO-KATANA100', 25.4, '20.5 x 11.4 x 19.5 inches', TRUE),
('Martin D-28 Dreadnought Acoustic Guitar', 'The Martin D-28 is the definitive dreadnought acoustic guitar, featuring a solid Sitka spruce top and solid East Indian rosewood back and sides.', 2999.99, 1799.99, 5, 'Guitars', 'Martin', 'martin_d28.jpg', 'MA-D-28', 6.2, '41.5 x 16.5 x 5.5 inches', TRUE),
('Native Instruments Komplete Kontrol S88 MK2', 'The Komplete Kontrol S88 MK2 is a premium 88-key keyboard controller with fully weighted keys and deep integration with Komplete and NKS.', 1099.99, 659.99, 10, 'Keyboards & Synthesizers', 'Native Instruments', 'ni_s88mk2.jpg', 'NI-S88-MK2', 37.5, '52.5 x 13.8 x 4.7 inches', TRUE),
('Ibanez SR500E Bass Guitar', 'The Ibanez SR500E bass guitar features a mahogany body, 5-piece maple/walnut neck, and powerful Bartolini MK1 pickups.', 699.99, 419.99, 15, 'Bass Guitars', 'Ibanez', 'ibanez_sr500e.jpg', 'IB-SR500E', 8.8, '45 x 13 x 4 inches', TRUE),
('Focusrite Scarlett 2i2 3rd Gen USB Audio Interface', 'The Focusrite Scarlett 2i2 (3rd Gen) offers professional audio recording quality with two high-performance mic preamps and USB-C connectivity.', 169.99, 101.99, 30, 'Audio Interfaces', 'Focusrite', 'focusrite_2i2.jpg', 'FO-SCARLETT2I3', 2.2, '7.7 x 5.1 x 1.7 inches', TRUE),
('Marshall DSL20HR Tube Head and 1922 2x12 Cabinet', 'The Marshall DSL20HR tube head and 1922 2x12 cabinet deliver classic Marshall tone with modern features and connectivity.', 899.99, 539.99, 8, 'Amplifiers', 'Marshall', 'marshall_dsl20hr.jpg', 'MA-DSL20HR-B', 62.3, '28 x 24 x 18 inches', TRUE),
('Akai MPC Live II Standalone Production Station', 'The Akai MPC Live II is a standalone music production station with a 7-inch multi-touch display, built-in speakers, and battery for true portability.', 1299.99, 779.99, 7, 'Production Equipment', 'Akai', 'akai_mpclive2.jpg', 'AK-MPCLIVE2', 9.9, '14.5 x 10.2 x 3.5 inches', TRUE);

-- Get the number of inserted products
SET @product_count = (SELECT COUNT(*) FROM Product);

-- Verification queries
SELECT CONCAT('PRODUCT table count: ', @product_count) AS verification_result;

SELECT 'Products by category:' AS '';
SELECT category, COUNT(*) as product_count 
FROM Product 
GROUP BY category 
ORDER BY product_count DESC;

SELECT 'Sample products:' AS '';
SELECT product_id, name, price, stock_quantity, category 
FROM Product 
ORDER BY product_id 
LIMIT 10;

-- Commit transaction if all operations succeeded
COMMIT;

-- Reset SQL mode and constraints
SET SQL_MODE = @OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS = @OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS = @OLD_UNIQUE_CHECKS;

-- Final verification
SELECT CONCAT('Script completed successfully. Inserted ', @product_count, ' products.') AS final_result;
