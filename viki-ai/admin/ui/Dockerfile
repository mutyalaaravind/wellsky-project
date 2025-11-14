# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage with NGINX
FROM nginx:1.25.0-alpine

# Copy build files to nginx html directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY assets/nginx/default.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]