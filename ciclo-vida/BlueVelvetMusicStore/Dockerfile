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
RUN apk add --no-cache wget
COPY --from=build /app/build/libs/*.jar app.jar
EXPOSE 8080
HEALTHCHECK --interval=10s --timeout=5s --start-period=40s --retries=5 \
    CMD wget --quiet --tries=1 --spider http://localhost:8080/ || exit 1
ENTRYPOINT ["java", "-jar", "app.jar"]
