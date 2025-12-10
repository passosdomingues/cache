# @author Rafael Passos Domingues
# @lastUpdate 2025 December 10 (Wed)
# @brief Multi-stage Dockerfile for Frontend (Node Build -> Nginx).
# @us US-0000 Project Configuration - Granularity: Containerization
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
