import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  // Utilise la même adresse que notre backend pour les appels locaux.
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
  },
});
