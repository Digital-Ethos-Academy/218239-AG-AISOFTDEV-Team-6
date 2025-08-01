# Stage 1: Build the application
FROM node:22-alpine AS build

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy the application code
COPY . .

# Stage 2: Run the application
FROM node:22-alpine

# Set the working directory
WORKDIR /app

# Copy the node_modules and built files from the previous stage
COPY --from=build /app .

# Create a non-root user to run the application
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Change ownership and permissions
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose the necessary port (e.g., 3000)
EXPOSE 5173

# Command to run the application
CMD ["npm", "run", "dev"]