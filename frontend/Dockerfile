# Build stage
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package.json .
# Note: If using npm, use 'npm install'. 
# For this task, we'll assume a standard install.
RUN npm install

# Copy source code
COPY . .

# Start the development server
CMD ["npm", "start"]