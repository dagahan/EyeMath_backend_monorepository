import { defineConfig } from "vite"
export default defineConfig({
  root: ".",
  server: { port: 5500, open: true },
  build: { outDir: "/dist", emptyOutDir: true },
})
