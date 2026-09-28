import { defineConfig } from "vite";
export default defineConfig({
  base: "./",
  build: { outDir: "../src/email_in_chat/static", emptyOutDir: true },
});
