const { outDir, packagerConfig, rebuildConfig, plugins } = require("./forge.config.common");

module.exports = {
  outDir: outDir,
  packagerConfig: {
    ...packagerConfig,
    osxSign: {
      provisioningProfile: "../../secrets/Thrive_MacOS.provisionprofile",
      identity: "Apple Distribution: Horia-Mihai Coman",
      type: "distribution",
      verbose: true,
      hardenedRuntime: true,
      continueOnError: false
    }
  },
  rebuildConfig: rebuildConfig,
  makers: [
    {
      name: '@electron-forge/maker-pkg',
      config: {
        identity: 'Mac Developer Installer: Horia-Mihai Coman',
      }
    }
  ],
  plugins: plugins
};
