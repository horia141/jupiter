# Self-Hosting

> This is a work in progress section on how to do self-hosting for Thrive.

Thrive natively support self-hosting, though at this moment only via the webapp surface.
This document presents a number of alternative ways to achieve this.

**Self-hosting** means you are running the Thrive application on your _own infrastructure and
servers_ rather than using the [hosted version](https://get-thriving.com). This gives you full
control over your data and the application, but requires managing the deployment
and maintenance yourself.

We've tried making the experience as smooth as possible, but realistically self-hosting
requires a modicum of tech expertise. Even if you manage to follow the instructions
below, there's aspects of reliability, data recovery, etc. that are tricky to get right,
therefore treat lightly. If you're unsure, the [hosted version](https://get-thriving.com)
aims to be respectful of you and focused on privacy.

## With A Linux VPS Via Docker (Hetzner, DigitalOcean, etc)

There's many ways to self-host Thrive, but running it on a Linux VPS via Docker is both
general and flexibile. And also sufficiently high-level that even folks that are not
software developers can follow along.

### Groundwork

A VPS (Virtual Private Server) is a virtualized server that you can rent from a
cloud provider. It runs on their hardware but gives you full control over the
operating system and software, just like having your own dedicated server.
Popular VPS providers include:

- [Hetzner](https://www.hetzner.com/)
- [DigitalOcean](https://www.digitalocean.com/)
- [Linode](https://www.linode.com/)
- [Vultr](https://www.vultr.com/)

For running Thrive, a basic VPS with 1-2 GB RAM and 1 CPU core should be sufficient
for personal use. The providers above all offer plans starting around $5-10/month.

> The big cloud providers like AWS, GCP or Azure have similar offerings (and much
> more), but they tend to require a more involved setup and have slightly higher
> prices for what we'd need.

Each provider has their own way of setting things up, but it should be
fairly straightforward to buy a VPS and get SSH and root access to it.

You'll also need Docker installed on your VPS. Docker is a platform for running
applications in containers - lightweight, isolated environments that package up
all the dependencies needed to run the software. Most VPS providers offer images
with Docker pre-installed, but if not, you can follow the
[official Docker installation guide](https://docs.docker.com/engine/install/)
for your Linux distribution.

### Preparation

In order to prepare Thrive, you need to download some configuration files to
your machine. Putting these files in your home directory should be enough:

```bash
wget https://github.com/horia141/jupiter/releases/latest/download/compose.yaml
wget https://github.com/horia141/jupiter/releases/latest/download/nginx.conf
wget https://github.com/horia141/jupiter/releases/latest/download/webui.conf
```

It's instructive to inspect them, and you are free to modify them, but
there should not be any need.

There is some configuration that's specific to your instance of Thrive that
you'll need to provide though. You'll need to create and edit an `.env` file like so:

```bash
touch .env
echo "PORT=80" >> .env
echo "AUTH_TOKEN_SECRET=$(openssl rand -base64 32)" >> .env
echo "SESSION_COOKIE_SECRET=$(openssl rand -base64 32)" >> .env
```

When inspecting the `.env` file, it should look something like this:

```bash
PORT=80
AUTH_TOKEN_SECRET=s6cfvG3E3vyzXjtIM/1I6+t9oM9pGBC6GG0O9L7XmiY=
SESSION_COOKIE_SECRET=FI3X/vjPJCUUeH+tu2OvhCQn7i1HyiVV2Vl4g/ce9DQ=
```

To check that `docker` has picked up the config and is correctly integrating
it, run `docker compose config` and check that no errors are reported.

### Running Things

Now, you just need to run things via

```bash
sudo docker compose up
```

You'll then see some output like:

```bash
[+] Running 3/3
... docker setting things up!
Attaching to frontend-1, webapi-1, webui-1
... output omitted
webui-1     | ================================================================================
webui-1     | Starting Jupiter WebUI:
webui-1     |   Version: 1.1.4
webui-1     |   Environment: production
webui-1     |   Hosting: self-hosted
webui-1     | ================================================================================
... output omitted
webapi-1    | ================================================================================
webapi-1    | Starting Jupiter WebAPI:
webapi-1    |   Version: 1.1.4
webapi-1    |   Environment: production
webapi-1    |   Hosting: self-hosted
webapi-1    | ================================================================================
... output omitted
webapi-1    | 2025-03-09 16:17:03 INFO     Uvicorn running on http://0.0.0.0:2000 (Press CTRL+C to quit)
... output omitted
webui-1     | Remix App Server started at http://localhost:2000 (http://0.0.0.0:2000)
```

This signals that the services making up Thrive are running and healthy.
It should take less than a minute to get to this output. If there's any errors,
you're free to debug them, or reach out on our channels
(GitHub issues, Discord,etc) for help.

### Testing

You can now access thrive by visiting the IP address or domain associated with your VPS.

### Backups

WIP

### Reliability

WIP

### Updating

To to a newer version of Thrive, run the following command:

```bash
docker compose pull
```

If there's new Docker images they will be pulled. You need to restart
`docker compose` to have this take effect.

## With A High-Level Hosting Service (Render, Vercel, Genezio, etc.)

WIP

## More Alternatives

Thrive is developed on MacOS with a suite of relatively cross-platform technologies,
and the hosted service runs on [render.com](https://render.com). If you need more
than the VPS setup, it's probably doable, but requires a bit of extra elbow
grease. Contact us and we'll get it sorted.
