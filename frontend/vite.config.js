import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173,
        proxy: {
            '/health': 'http://127.0.0.1:8000',
            '/projects': 'http://127.0.0.1:8000',
            '/documents': 'http://127.0.0.1:8000',
            '/users': 'http://127.0.0.1:8000',
            '/issues': 'http://127.0.0.1:8000',
            '/plans': 'http://127.0.0.1:8000'
        }
    }
});
