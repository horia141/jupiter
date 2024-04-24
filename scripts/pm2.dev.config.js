module.exports = {
    apps : [{
      name   : "webapi",
      cwd: "src/webapi",
      interpreter: "none",
      script: "script",
      args: "-qF /dev/null python -m watchfiles jupiter.webapi.jupiter.sync_main . ../core",
      env: {
        PY_COLORS: "1",
        SQLITE_DB_URL: "sqlite+aiosqlite:///../../.build-cache/juiter-fixed.sqlite"
      }
    },{
        name: "webui",
        cwd: "src/webui",
        interpreter: "none",
        script: "script",
        args: "-qF /dev/null npm run dev",
        env: {
            PORT: "10020"
        }
    }]
  }