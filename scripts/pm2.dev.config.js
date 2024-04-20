module.exports = {
    apps : [{
      name   : "webapi",
      cwd: "src/webapi",
      script: "python -m watchfiles jupiter.webapi.jupiter.sync_main . ../core",
      env: {
        SQLITE_DB_URL: "sqlite+aiosqlite:///../../.build-cache/juiter-fixed.sqlite"
      }
    },{
        name: "webui",
        cwd: "src/webui",
        script: "npm run dev",
        env: {
            PORT: "10020"
        }
    }]
  }