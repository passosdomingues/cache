-- Create database if not exists (adjust database name as needed)
CREATE DATABASE IF NOT EXISTS user_management_db;
USE user_management_db;

-- Drop tables if they exist (in correct order due to foreign key constraints)
DROP TABLE IF EXISTS ROLE_USER;
DROP TABLE IF EXISTS USER;
DROP TABLE IF EXISTS ROLE;

-- Create ROLE table
CREATE TABLE ROLE (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create USER table
CREATE TABLE USER (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    password VARCHAR(255),
    enabled BOOLEAN DEFAULT TRUE,
    photos VARCHAR(255)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create ROLE_USER junction table
CREATE TABLE ROLE_USER (
    user_id INT,
    role_id INT,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES USER(user_id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES ROLE(role_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Populate ROLE table
INSERT INTO ROLE (name, description) VALUES
('Administrator', 'Manage everything'),
('Sales Manager', 'Manage product price, customers, shipping, orders and sales report'),
('Editor', 'Manage categories, brands, products, articles and menus'),
('Shipping Manager', 'View products, view orders and update order status'),
('Assistant', 'Manage questions and reviews');

-- Populate USER table
INSERT INTO USER (email, first_name, last_name, password, enabled, photos) VALUES
('florentino@gmail.com', 'Florentino', 'Ariza', 'ariza000', TRUE, 'florentino.png'),
('fermina@yahoo.com', 'Fermina', 'Daza', 'daza123', FALSE, 'fermina.png'),
('hahari@hotmail.com', 'Yuval', 'Harari', 'haharisapiens', TRUE, 'yuval.png'),
('zola@gmail.com', 'Émile', 'Zola', 'zolagerminal', TRUE, 'emile.png'),
('kundera@gmail.com', 'Milan', 'Kundera', 'kunderamilan', FALSE, 'milan.png'),
('faulkner@gmail.com', 'William', 'Faulkner', 'faulknerw', TRUE, 'william.png'),
('fitzgerald@example.com', 'Francis', 'Fitzgerald', 'fitzgeraldscott', TRUE, 'francis.png'),
('saramago@yahoo.com.br', 'José', 'Saramago', 'saramago2022', TRUE, 'jose.png'),
('frankl@example.com', 'Viktor', 'Frankl', 'franklv', TRUE, 'viktor.png'),
('conrad@aol.com', 'Joseph', 'Conrad', 'conradj', TRUE, 'joseph.jpg'),
('verne@gmail.com', 'Júlio', 'Verne', 'verne80', FALSE, 'julio.png'),
('more@yahoo.com.br', 'Thomas', 'More', 'more1513', TRUE, 'thomas.png'),
('huxley@aol.com', 'Aldous', 'Huxley', 'huxleybrave', TRUE, 'aldous.png'),
('burgess@gmail.com', 'Antony', 'Burgess', 'burgessorange', TRUE, 'antony.png'),
('bradburry@hotmail.com', 'Ray', 'Bradburry', 'bradburry451', TRUE, 'ray.jpg'),
('azimov@gmail.com', 'Isaac', 'Azimov', 'azimovrobot', FALSE, 'isaac.png'),
('queiroz@yahoo.com.br', 'Rachel', 'Queiroz', 'queiroz15', TRUE, 'raquel.png'),
('dostoievski@gmail.com', 'Fiodor', 'Dostoievski', 'dostoievskipunish', TRUE, 'fiodor.jpg'),
('steinbeck@gmail.com', 'John', 'Steinbeck', 'steinbeckpearl', TRUE, 'john.png'),
('lispector@yahoo.com.br', 'Clarice', 'Lispector', 'lispectorestrela', TRUE, 'clarice.png');

-- Populate ROLE_USER table (assign roles to users)
INSERT INTO ROLE_USER (user_id, role_id) VALUES
(1, 1),  -- Florentino: Administrator
(2, 1),  -- Fermina: Administrator
(3, 3),  -- Yuval: Editor
(4, 3),  -- Émile: Editor
(4, 5),  -- Émile: Assistant
(5, 3),  -- Milan: Editor
(6, 3),  -- William: Editor
(7, 3),  -- Francis: Editor
(8, 2),  -- José: Sales Manager
(9, 2),  -- Viktor: Sales Manager
(10, 3), -- Joseph: Editor
(10, 2), -- Joseph: Sales Manager
(11, 2), -- Júlio: Sales Manager
(12, 2), -- Thomas: Sales Manager
(13, 4), -- Aldous: Shipping Manager
(13, 5), -- Aldous: Assistant
(14, 4), -- Antony: Shipping Manager
(14, 3), -- Antony: Editor
(15, 4), -- Ray: Shipping Manager
(16, 4), -- Isaac: Shipping Manager
(17, 4), -- Rachel: Shipping Manager
(17, 3), -- Rachel: Editor
(18, 5), -- Fiodor: Assistant
(18, 2), -- Fiodor: Sales Manager
(19, 5), -- John: Assistant
(19, 3), -- John: Editor
(19, 2), -- John: Sales Manager
(20, 5); -- Clarice: Assistant

-- Verification queries (optional)
SELECT 'USER table count: ' AS description, COUNT(*) AS count FROM USER
UNION ALL
SELECT 'ROLE table count: ', COUNT(*) FROM ROLE
UNION ALL
SELECT 'ROLE_USER table count: ', COUNT(*) FROM ROLE_USER;