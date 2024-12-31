const { FusesPlugin } = require("@electron-forge/plugin-fuses");
const { FuseV1Options, FuseVersion } = require("@electron/fuses");
const fs = require('fs').promises;
const plist = require('plist');
const path = require('path');

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
    extraResource: ["README.md", "LICENSE"],
    derefSymlinks: false,
  },
  rebuildConfig: {},
  hooks: {
    packageAfterCopy: async (config, buildPath, electronVersion, platform, arch) => {
        if (platform !== 'darwin' && platform !== 'mas') {
            return; // Only modify Info.plist on macOS
          }
        
          const plistPath = path.join(buildPath, '..', '..', 'Info.plist');
          
          try {
            // Check if the plist file exists
            await fs.access(plistPath);
            console.log(`Found Info.plist at ${plistPath}`);
        
            // Read the plist file
            const plistContent = await fs.readFile(plistPath, 'utf8');
            const plistData = plist.parse(plistContent);
        
            // Add the allow-jit entitlement
            plistData['com.apple.security.cs.allow-jit'] = true;
        
            // Write back the modified plist
            await fs.writeFile(plistPath, plist.build(plistData));
            console.log('Modified Info.plist successfully.');
          } catch (err) {
            console.error(`Error modifying Info.plist: ${err.message}`);
            // Throw the error to prevent hanging
            throw err;
          }
      }
  },
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
