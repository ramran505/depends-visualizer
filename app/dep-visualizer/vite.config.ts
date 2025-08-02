import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import path from "path";

export default defineConfig({  
  plugins: [ tailwindcss() ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
server: {
    fs: {
      // Allow serving files from one level up (e.g., ../output)
      allow: [
        path.resolve(__dirname, ".."), // <- this line allows accessing ../output
      ],
    },
  },
})