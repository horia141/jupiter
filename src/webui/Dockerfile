FROM node:22.14
LABEL maintainer='horia141@gmail.com'

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
COPY src/webui/Config.project.live src/webui/Config.project
COPY src/webui/package.json src/webui/package.json
COPY src/webui/tsconfig.json src/webui/tsconfig.json
COPY src/webui/remix.config.js src/webui/remix.config.js
COPY src/webui/remix.env.d.ts src/webui/remix.env.d.ts
COPY src/webui/from-electron.d.ts src/webui/from-electron.d.ts

RUN npm install

# hadolint ignore=DL3003
RUN cd gen/ts/webapi-client && npx tsc

COPY src/webui/app src/webui/app
COPY src/webui/public/favicon.ico src/webui/public/favicon.ico
COPY src/webui/public/logo.png src/webui/public/logo.png
COPY src/webui/public/pomodoro-notification.mp3 src/webui/public/pomodoro-notification.mp3

ARG PORT=10020
ENV HOST=0.0.0.0
ENV PORT=$PORT
EXPOSE $PORT

WORKDIR /jupiter/src/webui

RUN npx remix build

# ENTRYPOINT [ "dumb-init", "npx", "remix", "dev" ]
ENTRYPOINT [ "dumb-init", "npx", "remix-serve", "build" ]
