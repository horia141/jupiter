# Installation

## Web Application

The simplest way to use Thrive is by using the [web application](https://jupiter-webui.onrender.com/).
If this is the first time you're visiting you'll be prompted to create an account.

By using the web application you will be running in [hosted mode](../concepts/hosted-vs-local-mode.md).

## MacOS Dmg Local

For MacOS, a simple way of installing the Thrive CLI is via a `dmg` archive published
together with a release. You can check them [in the release page](https://github.com/horia141/jupiter/releases).

![Releases](../assets/install-release.png)

You can then download and install it into your `Applications` folder by dragging and dropping it
like any other application.

Invoking this is a bit tricky however:

```bash
$ mkdir my-thrive-work-dir # A dir where you manage local Thrive data.
$ cd my-thrive-work-dir
$ /Applications/Thrive.app/Contents/MacOS/thrive init --help
```

You can of course add an alias to your shell about it.

By using this approach you will be running in [local mode](../concepts/hosted-vs-local-mode.md).

## GitHub (Advanced)

Another way to install it is from "sources" on GitHub.

You need to make sure you have a recent Python3 installed. Thrive has been tested on Python 3.10. Docker is also
useful to have on board.

From GitHub you can just clone the repository like so:

```bash
$ git clone git@github.com:horia141/jupiter.git jupiter
```

This will get you the `master` version of the code.

After this, you can build a Docker image with Thrive like so:

```bash
$ cd thrive
$ make docker-build
```

This will chug for a while and produce a local image called `thrive-cli`. You can use this to run commands like so:

```bash
$ mkdir ~/my-thrive-work-dir # A dir where you manage local Thrive data.
$ cd ~/my-thrive-work-dir
$ docker run -it --rm --name thrive-app -v $(pwd):/data thrive-cli init --help
```

Alternatively, you can use the scripts locally, like so:

```bash
$ cd thrive
$ mkdir .build-cache
$ ./scripts/setup-for-dev.sh # Hopefully this is simple!
```

Now, instead of running the Docker image, you can directly run the scripts, like so:

```bash
$ mkdir ~/my-jupier-work-dir
$ ./scripts/run-dev.sh
```

By using this approach you will be running in [local mode](../concepts/hosted-vs-local-mode.md).