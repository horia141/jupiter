const { outDir, packagerConfig, rebuildConfig, plugins } = require("./forge.config.common");

module.exports = {
  outDir: outDir,
  packagerConfig: {
    ...packagerConfig,
    osxSign: {
        provisioningProfile: "../../secrets/Thrive_MacOS.provisionprofile",
        identity: "Developer ID Application: Horia-Mihai Coman",
        type: "distribution",
        verbose: true,
        hardenedRuntime: true,
        continueOnError: false
      },
    osxNotarize: {
      appleId: process.env.APPLE_ID,
      teamId: process.env.APPLE_TEAM_ID,
      appleIdPassword: process.env.APPLE_NOTARIZATION_PASSWORD,
      verbose: true,
      wait: false,
      continueOnError: false
    }
  },
  rebuildConfig: rebuildConfig,
  makers: [
    {
      name: "@electron-forge/maker-dmg",
      config: {
        icon: "assets/jupiter.icns",
      }
    },
  ],
  plugins: plugins,
};
