FROM node:19.3
LABEL maintainer='horia141@gmail.com'

# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install -y --no-install-recommends dumb-init && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /jupiter

COPY LICENSE LICENSE
COPY package.json package.json
COPY package-lock.json package-lock.json
COPY gen gen
COPY src/Config.global src/Config.global
COPY src/webui/README.md src/webui/README.md
COPY src/webui/Config.project.docker src/webui/Config.project
COPY src/webui/package.json src/webui/package.json
COPY src/webui/tsconfig.json src/webui/tsconfig.json
COPY src/webui/remix.config.js src/webui/remix.config.js
COPY src/webui/remix.env.d.ts src/webui/remix.env.d.ts

RUN npm install --ws --include-workspace-root

# hadolint ignore=DL3003
RUN cd gen && npx tsc

COPY src/webui/app src/webui/app
COPY src/webui/public/favicon.ico src/webui/public/favicon.ico
COPY src/webui/public/pomodoro-notification.mp3 src/webui/public/pomodoro-notification.mp3

ARG PORT=10020
ENV PORT=$PORT
EXPOSE $PORT

ENV HOST 0.0.0.0
EXPOSE 10020
EXPOSE 8002

WORKDIR /jupiter/src/webui

RUN npm run build

# ENTRYPOINT [ "dumb-init", "npx", "remix", "dev" ]
ENTRYPOINT [ "dumb-init", "npx", "remix-serve", "build" ]
