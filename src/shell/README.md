# Thrive Shell

The local pages and server logic shared by the desktop (Electron) and mobile
(Capacitor) apps:

- `pages/`: the loading, error and server picker pages, with their scripts
  and `shell.css`. They reach the platform only through an adapter, which each
  app's build aliases as `#adapter` (see `pages/shell.js`).
- `lib/check-server.js`: checks that an address is a compatible Thrive server.
  The desktop main process and the mobile adapter both use it.
- `vite.js`: `shellViteConfig`, which each app's `vite.config.ts` calls to
  build the pages into its own `dist`.
