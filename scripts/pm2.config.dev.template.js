module.exports = {
    apps : [{
      name   : "${NAMESPACE}:webapi",
      cwd: "src/webapi",
      interpreter: "none",
      script: "python",
      args: " -W always::DeprecationWarning -m watchfiles jupiter.webapi.jupiter.sync_main . ../core",
      log_file: "$WEBAPI_LOG_FILE",
      env: {
        PY_COLORS: "1",
        SQLITE_DB_URL: "$WEBAPI_SQLITE_DB_URL",
        PORT: "$WEBAPI_PORT",
        SQLALCHEMY_WARN_20: "1"
      }
    }, {
        name: "${NAMESPACE}:webui",
        cwd: "src/webui",
        interpreter: "none",
        script: "remix",
        args: "dev",
        log_file: "$WEBUI_LOG_FILE",
        env: {
            LOCAL_OR_SELF_HOSTED_WEBAPI_SERVER_URL: "$WEBAPI_SERVER_URL",
            PORT: "$WEBUI_PORT"
        }
    }]
  }