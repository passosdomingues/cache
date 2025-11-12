# Bluevelvet Music Store - Enterprise Edition

## 📋 Overview

**Bluevelvet Music Store** is an enterprise-grade e-commerce platform for music products, built with **Spring Boot 3.2**, **Jakarta EE**, **Spring Data JPA**, and **Spring Security with OAuth2**. The application features a modern, responsive UI with dark/light mode support and comprehensive accessibility features.

**Author:** Rafael Passos Domingues  
**Version:** 1.0.0  
**License:** MIT

---

## 🎯 Key Features

### Backend Architecture
- **Spring Boot 3.2** with Jakarta EE
- **Spring Data JPA** with Hibernate for ORM
- **Spring Security** with OAuth2 authentication (Google)
- **MySQL 8.0** database with soft delete support
- **Layered Architecture:** Controller → Service → Repository
- **Global Exception Handling** with custom exceptions
- **RESTful API** with OpenAPI/Swagger documentation

### Frontend
- **Thymeleaf** templates for server-side rendering
- **Bootstrap 5** for responsive design
- **Dark/Light Mode** with persistent user preference
- **Accessibility Features:** High contrast, large text, reduced motion
- **Responsive Design** for mobile, tablet, and desktop

### Security
- **OAuth2 Authentication** with Google
- **Role-Based Access Control (RBAC)** - ADMIN, MANAGER, USER, GUEST
- **CSRF Protection** and security headers
- **Password encryption** with BCrypt
- **Session management** with concurrent session control

### Database
- **Soft Delete** pattern to preserve data integrity
- **Hierarchical Categories** with parent-child relationships
- **Audit Logging** for compliance and tracking
- **Indexed queries** for optimal performance

### DevOps
- **Docker** containerization with multi-stage builds
- **Docker Compose** for local development
- **MySQL** in Docker for consistent environments
- **Health checks** for container orchestration

---

## 🏗️ Project Structure

```
bluevelvet-music-store-enterprise/
├── src/
│   ├── main/
│   │   ├── java/com/bluevelvet/
│   │   │   ├── config/              # Spring configuration
│   │   │   ├── controller/
│   │   │   │   ├── api/            # REST API controllers
│   │   │   │   └── web/            # MVC controllers
│   │   │   ├── domain/
│   │   │   │   ├── dto/            # Data Transfer Objects
│   │   │   │   ├── entity/         # JPA entities
│   │   │   │   └── event/          # Domain events
│   │   │   ├── exception/          # Custom exceptions
│   │   │   ├── repository/         # Data access layer
│   │   │   ├── security/           # Security handlers
│   │   │   ├── service/            # Business logic
│   │   │   │   └── impl/           # Service implementations
│   │   │   └── util/               # Utility classes
│   │   └── resources/
│   │       ├── templates/          # Thymeleaf templates
│   │       ├── static/
│   │       │   ├── css/            # Stylesheets
│   │       │   ├── js/             # JavaScript
│   │       │   └── images/         # Images
│   │       └── application.yml     # Configuration
│   └── test/
│       └── java/com/bluevelvet/    # Unit tests
├── pom.xml                         # Maven configuration
├── Dockerfile                      # Docker image
├── docker-compose.yml              # Docker Compose
├── init-db.sql                     # Database initialization
└── README.md                       # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Java 21** or higher
- **Maven 3.9+**
- **Docker** and **Docker Compose** (for containerized setup)
- **MySQL 8.0+** (if running locally without Docker)
- **Google OAuth2 Credentials** (for authentication)

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/bluevelvet-music-store-enterprise.git
cd bluevelvet-music-store-enterprise
```

#### 2. Configure Environment Variables

```bash
cp .env .env
```

Edit `.env` and add your Google OAuth2 credentials:

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
DB_PASSWORD=your_secure_password
```

#### 3. Start with Docker Compose

```bash
docker-compose up -d
```

The application will be available at `http://localhost:8080`

#### 4. Or Run Locally

```bash
# Start MySQL
docker run -d --name bluevelvet-mysql \
  -e MYSQL_ROOT_PASSWORD=password \
  -e MYSQL_DATABASE=bluevelvet_db \
  -e MYSQL_USER=bluevelvet \
  -e MYSQL_PASSWORD=password \
  -p 3306:3306 \
  mysql:8.0

# Build and run the application
mvn clean install
mvn spring-boot:run
```

---

## 🔐 OAuth2 Google Setup

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google+ API

### 2. Create OAuth2 Credentials

1. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
2. Choose **Web application**
3. Add authorized redirect URIs:
   - `http://localhost:8080/login/oauth2/code/google`
   - `http://localhost:8080/oauth2/callback`
   - `https://yourdomain.com/login/oauth2/code/google`

### 3. Copy Credentials

Copy the **Client ID** and **Client Secret** to your `.env` file

---

## 📚 API Documentation

### Access Swagger UI

Navigate to `http://localhost:8080/swagger-ui.html`

### Category Endpoints

#### Get All Root Categories
```http
GET /api/v1/categories/root
Authorization: Bearer {token}
```

#### Create Category (Admin Only)
```http
POST /api/v1/categories
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Guitars",
  "description": "Acoustic and electric guitars",
  "imageFileName": "guitars.jpg",
  "isActive": true,
  "displayOrder": 1
}
```

#### Update Category (Admin Only)
```http
PUT /api/v1/categories/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description"
}
```

#### Delete Category (Admin Only)
```http
DELETE /api/v1/categories/{id}
Authorization: Bearer {token}
```

#### Search Categories
```http
GET /api/v1/categories/search?searchTerm=guitar&page=0&size=20
Authorization: Bearer {token}
```

---

## 🎨 Frontend Features

### Dark/Light Mode

- Toggle button in navbar
- Persistent user preference in localStorage
- Respects system theme preference
- Smooth transitions

### Accessibility

- **High Contrast Mode** for better visibility
- **Large Text** option for readability
- **Reduced Motion** for users sensitive to animations
- **Keyboard Navigation** support
- **ARIA Labels** for screen readers

### Responsive Design

- Mobile-first approach
- Breakpoints for tablet and desktop
- Touch-friendly buttons and controls
- Optimized images and assets

---

## 🗄️ Database Schema

### Users Table
```sql
- id (PK)
- email (UNIQUE)
- fullName
- pictureUrl
- oauthProvider
- oauthProviderId
- passwordHash
- isActive
- isEmailVerified
- createdAt
- updatedAt
- lastLoginAt
- deletedAt (soft delete)
```

### Roles Table
```sql
- id (PK)
- name (UNIQUE)
- description
- createdAt
- updatedAt
```

### Categories Table
```sql
- id (PK)
- name (UNIQUE)
- description
- imageFileName
- imageUrl
- parentId (FK - self-referencing)
- isActive
- displayOrder
- createdAt
- updatedAt
- deletedAt (soft delete)
```

### User_Roles Junction Table
```sql
- userId (FK)
- roleId (FK)
```

---

## 🛡️ Security Features

### Authentication
- OAuth2 with Google
- Session-based authentication
- CSRF protection
- Secure cookie handling

### Authorization
- Role-based access control (RBAC)
- Method-level security with @PreAuthorize
- Admin-only endpoints for category management

### Data Protection
- Soft delete pattern (data never permanently deleted)
- Password encryption with BCrypt
- HTTPS support (production)
- Security headers (CSP, X-Frame-Options, etc.)

---

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t bluevelvet-music-store:1.0.0 .
```

### Run with Docker Compose

```bash
docker-compose up -d
```

### Environment Variables

```env
DB_HOST=mysql
DB_PORT=3306
DB_NAME=bluevelvet_db
DB_USER=bluevelvet
DB_PASSWORD=secure_password
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
SPRING_PROFILES_ACTIVE=prod
```

### Health Check

```bash
curl http://localhost:8080/actuator/health
```

---

## 📊 Monitoring

### Actuator Endpoints

- Health: `GET /actuator/health`
- Info: `GET /actuator/info`
- Metrics: `GET /actuator/metrics`

### Logging

- Logs are written to `logs/bluevelvet.log`
- Log level configured in `application.yml`
- Rotation: 10MB per file, 30 days retention

---

## 🧪 Testing

### Run Tests

```bash
mvn test
```

### Test Coverage

```bash
mvn test jacoco:report
```

---

## 📝 Code Quality

### Code Style
- Java 21 features
- CamelCase naming convention
- Comprehensive Javadoc comments
- @param and @brief annotations

### Design Patterns
- **Repository Pattern** for data access
- **Service Layer Pattern** for business logic
- **DTO Pattern** for data transfer
- **Strategy Pattern** for authentication handlers
- **Mapper Pattern** for entity conversion

### SOLID Principles
- **S**ingle Responsibility: Each class has one reason to change
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Subtypes can replace base types
- **I**nterface Segregation: Clients depend on specific interfaces
- **D**ependency Inversion: Depend on abstractions, not concretions

---

## 🚀 Production Deployment

### Prerequisites
- SSL/TLS certificate
- Nginx reverse proxy
- MySQL database (managed service recommended)
- Environment-specific configuration

### Deployment Steps

1. **Build Docker image**
   ```bash
   docker build -t bluevelvet-music-store:1.0.0 .
   ```

2. **Push to registry**
   ```bash
   docker tag bluevelvet-music-store:1.0.0 your-registry/bluevelvet:1.0.0
   docker push your-registry/bluevelvet:1.0.0
   ```

3. **Deploy to Kubernetes or Docker Swarm**
   ```bash
   kubectl apply -f k8s/deployment.yaml
   ```

4. **Configure Nginx**
   ```nginx
   server {
       listen 443 ssl http2;
       server_name yourdomain.com;
       
       ssl_certificate /etc/nginx/ssl/cert.pem;
       ssl_certificate_key /etc/nginx/ssl/key.pem;
       
       location / {
           proxy_pass http://app:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

---

## 📖 Additional Resources

- [Spring Boot Documentation](https://spring.io/projects/spring-boot)
- [Spring Security Documentation](https://spring.io/projects/spring-security)
- [Jakarta EE Documentation](https://jakarta.ee/)
- [Docker Documentation](https://docs.docker.com/)
- [OAuth2 Specification](https://oauth.net/2/)

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👨‍💻 Author

**Rafael Passos Domingues**

- GitHub: [@rafaelpassos](https://github.com/rafaelpassos)
- Email: rafael@example.com

---

## 🙏 Acknowledgments

- Spring Framework team for excellent documentation
- Bootstrap team for responsive design framework
- Google for OAuth2 authentication
- The Java community for continuous innovation

---

**Last Updated:** January 2025  
**Status:** Production Ready ✅
