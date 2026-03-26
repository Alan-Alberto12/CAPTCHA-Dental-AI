// Central API URL config.
// Set VITE_API_URL in your .env file (e.g. VITE_API_URL=http://127.0.0.1:8000)
// Falls back to localhost for local dev if env var is missing.
export const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
