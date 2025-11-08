# Frontend dev image for Vite + React
FROM node:20-alpine

# Create app dir
WORKDIR /app

# Install deps using lockfile for deterministic installs
COPY package.json package-lock.json ./
RUN npm install

# Copy the rest of the source (vite does HMR; compose will also bind-mount)
COPY . .

# Expose Vite dev port
EXPOSE 5173

# Run Vite dev server (host so containers/host can reach it)
CMD ["npm","run","dev","--","--host"]
