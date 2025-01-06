import { defineConfig } from 'vite';
import handlebars from 'vite-plugin-handlebars';
import { config } from "dotenv";
import { Env, Hosting } from '../../gen/ts/webapi-client/dist';

config({
    path: ["Config.project", "../Config.global", "../../secrets/Config.secrets"],
});

const WEBUI_URL =
  process.env.ENV == Env.PRODUCTION && process.env.HOSTING === Hosting.HOSTED_GLOBAL
    ? process.env.HOSTED_GLOBAL_WEBUI_SERVER_URL
    : process.env.LOCAL_WEBUI_SERVER_URL;

export default defineConfig({
    root: './src', // Source folder
    build: {
        outDir: '../dist', // Output folder
        emptyOutDir: true, // Clean the output folder before building
        rollupOptions: {
            input: ['./src/index.html', './src/error.html'],
            preserveEntrySignatures: 'strict',
        },
    },
    plugins: [
        handlebars({
            context: {
                title: process.env.PUBLIC_NAME,
                clientVersion: process.env.VERSION,
                webUiUrl: WEBUI_URL,
            }
        }),
    ]
});