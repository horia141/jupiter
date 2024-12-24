const { FusesPlugin } = require("@electron-forge/plugin-fuses");
const { FuseV1Options, FuseVersion } = require("@electron/fuses");

require("dotenv").config({
  path: ["Config.project", "../Config.global", "../../secrets/Config.secrets"],
});

module.exports = {
  outDir: "../../.build-cache/desktop",
  packagerConfig: {
    name: process.env.PUBLIC_NAME,
    appBundleId: process.env.BUNDLE_ID,
    appCategoryType: "public.app-category.productivity",
    appCopyright: process.env.COPYRIGHT,
    appVersion: process.env.VERSION,
    buildVersion: process.env.VERSION,
    asar: true,
    icon: "assets/jupiter.icns",
    overwrite: true,
    platform: ["darwin", "mas"],
  },
  rebuildConfig: {},
  plugins: [
    {
      name: "@electron-forge/plugin-auto-unpack-natives",
      config: {},
    },
    new FusesPlugin({
      version: FuseVersion.V1,
      [FuseV1Options.RunAsNode]: false,
      [FuseV1Options.EnableCookieEncryption]: true,
      [FuseV1Options.EnableNodeOptionsEnvironmentVariable]: false,
      [FuseV1Options.EnableNodeCliInspectArguments]: false,
      [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
      [FuseV1Options.OnlyLoadAppFromAsar]: true,
    }),
  ],
};
