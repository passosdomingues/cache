-- ============================================================================
-- Bluevelvet Music Store - Database Initialization Script
-- @author Rafael Passos Domingues
-- @version 1.0.0
-- ============================================================================

-- Create roles table
CREATE TABLE IF NOT EXISTS roles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    picture_url VARCHAR(500),
    oauth_provider VARCHAR(50),
    oauth_provider_id VARCHAR(255),
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    INDEX idx_user_email (email),
    INDEX idx_user_oauth_id (oauth_provider_id),
    INDEX idx_user_is_active (is_active),
    INDEX idx_user_deleted_at (deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create user_roles junction table
CREATE TABLE IF NOT EXISTS user_roles (
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    image_file_name VARCHAR(255),
    image_url VARCHAR(500),
    parent_id BIGINT,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_category_name (name),
    INDEX idx_category_parent_id (parent_id),
    INDEX idx_category_is_active (is_active),
    INDEX idx_category_deleted_at (deleted_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default roles
INSERT INTO roles (name, description) VALUES
('ADMIN', 'Administrator with full access'),
('MANAGER', 'Category manager with limited access'),
('USER', 'Regular user with read-only access'),
('GUEST', 'Guest user with minimal access')
ON DUPLICATE KEY UPDATE description=VALUES(description);

-- Insert sample categories
INSERT INTO categories (name, description, image_file_name, is_active, display_order) VALUES
('T-Shirts', 'Band and artist t-shirts', 'tshirts.jpg', TRUE, 1),
('Vinyl Records', 'Classic and modern vinyl records', 'vinyl.jpg', TRUE, 2),
('CDs', 'Compact discs and albums', 'cd.jpg', TRUE, 3),
('Instruments', 'Musical instruments and equipment', 'instruments.jpg', TRUE, 4),
('Books', 'Music books and biographies', 'books.jpg', TRUE, 5),
('Accessories', 'Music accessories and merchandise', 'accessories.jpg', TRUE, 6),
('Headphones', 'Audio equipment and headphones', 'headphones.jpg', TRUE, 7),
('Posters', 'Band posters and artwork', 'posters.jpg', TRUE, 8),
('Collectibles', 'Rare collectibles and memorabilia', 'collectibles.jpg', TRUE, 9),
('Digital', 'Digital downloads and streaming', 'digital.jpg', TRUE, 10)
ON DUPLICATE KEY UPDATE display_order=VALUES(display_order);

-- Insert subcategories for T-Shirts
INSERT INTO categories (name, description, parent_id, is_active, display_order) VALUES
('Metal T-Shirts', 'Heavy metal band t-shirts', (SELECT id FROM categories WHERE name = 'T-Shirts'), TRUE, 1),
('Rock T-Shirts', 'Rock band t-shirts', (SELECT id FROM categories WHERE name = 'T-Shirts'), TRUE, 2),
('Pop T-Shirts', 'Pop artist t-shirts', (SELECT id FROM categories WHERE name = 'T-Shirts'), TRUE, 3)
ON DUPLICATE KEY UPDATE display_order=VALUES(display_order);

-- Insert subcategories for Instruments
INSERT INTO categories (name, description, parent_id, is_active, display_order) VALUES
('Guitars', 'Acoustic and electric guitars', (SELECT id FROM categories WHERE name = 'Instruments'), TRUE, 1),
('Basses', 'Bass guitars and equipment', (SELECT id FROM categories WHERE name = 'Instruments'), TRUE, 2),
('Drums', 'Drum kits and percussion', (SELECT id FROM categories WHERE name = 'Instruments'), TRUE, 3),
('Keyboards', 'Keyboards and synthesizers', (SELECT id FROM categories WHERE name = 'Instruments'), TRUE, 4)
ON DUPLICATE KEY UPDATE display_order=VALUES(display_order);

-- Create audit log table (optional but recommended)
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    entity_type VARCHAR(100) NOT NULL,
    entity_id BIGINT NOT NULL,
    action VARCHAR(50) NOT NULL,
    user_id BIGINT,
    old_values JSON,
    new_values JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_user (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- End of initialization script
-- ============================================================================
