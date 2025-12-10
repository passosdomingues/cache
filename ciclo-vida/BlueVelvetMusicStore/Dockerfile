# @author Rafael Passos Domingues
# @lastUpdate 2025 December 10 (Wed)
# @brief Multi-stage Dockerfile for Backend (Gradle Build).
# @us US-0000 Project Configuration - Granularity: Containerization
FROM eclipse-temurin:17-jdk-alpine AS build
WORKDIR /app
COPY . .
RUN ./gradlew bootJar --no-daemon

FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=build /app/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
