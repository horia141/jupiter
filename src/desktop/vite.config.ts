import { config } from "dotenv";
import { defineConfig } from "vite";
import handlebars from "vite-plugin-handlebars";

config({
  path: ["Config.project", "../Config.global", "../../secrets/Config.secrets"],
});

export default defineConfig({
  root: "./src", // Source folder
  base: "./",
  build: {
    outDir: "../dist", // Output folder
    emptyOutDir: true, // Clean the output folder before building
    rollupOptions: {
      input: ["./src/index.html", "./src/error.html"],
      preserveEntrySignatures: "strict",
    },
  },
  plugins: [
    handlebars({
      context: {
        title: process.env.PUBLIC_NAME,
      },
    }),
  ],
});
