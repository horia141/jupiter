const {
  outDir,
  packagerConfig,
  hooks,
  rebuildConfig,
  plugins,
} = require("./forge.config.common.cjs");

module.exports = {
  outDir: outDir,
  packagerConfig: {
    ...packagerConfig,
    osxSign: process.env.QUICK
      ? undefined
      : {
          provisioningProfile: "../../secrets/Thrive_MacOS.provisionprofile",
          identity: "Apple Distribution: Horia-Mihai Coman",
          type: "distribution",
          verbose: true,
          hardenedRuntime: true,
          continueOnError: false,
        },
  },
  hooks: hooks,
  rebuildConfig: rebuildConfig,
  makers: [
    {
      name: "@electron-forge/maker-pkg",
      config: {
        identity: "Mac Developer Installer: Horia-Mihai Coman",
      },
    },
  ],
  plugins: plugins,
};
