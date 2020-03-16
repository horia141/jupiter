# Installation

There's just one way of installing jupiter right now, via GitHub, but more will come.

## Docker

You need to make sure you have a recent Docker installed. After that it's straightforward:

```bash
$ docker pull horia141/jupiter:latest
```

This will get you the latest version of the code. After this you can:

```bash
$ cd ~/my-jupiter-work-dir # A dir where you manage your Jupiter tasks.
$ docker run \
    -it --rm --name jupiter-app -v $(pwd):/data --env TZ=Europe/Bucharest \
    horia141/jupiter:latest upsert-tasks \
    /data/tasks-work.yaml
```

## GitHub

You need to make sure you have a recent Python3 installed. Jupiter has been tested on Python 3.6. Docker is also
useful to have on board.

From GitHub you can just clone the repository like so:

```bash
$ git clone git@github.com:horia141/jupiter.git jupiter
```

This will get you the `master` version of the code.

After this, you can build a Docker image with Jupiter like so:

```bash
$ cd jupiter
$ make docker-build
```

This will chug for a while and produce a local image called `jupiter`. You can use this to run commands like so:

```bash
$ cd ~/my-jupiter-work-dir # A dir where you manage your Jupiter tasks.
$ docker run \
    -it --rm --name jupiter-app -v $(pwd):/data --env TZ=Europe/Bucharest \
    jupiter upsert-tasks \
    /data/tasks-work.yaml
```

Alternatively, you can use the scripts locally, like so:

```bash
$ cd jupiter
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Now, instead of running the Docker image, you can directly run the scripts, like so:

```bash
$ cd ~/my-jupier-work-dir
$ python ~/jupiter/src/jupiter.py upsert-tasks /data/user.yaml /data/tasks-work.yaml
```
