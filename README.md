# TL;DR

This gives you a way to run any jupyter kernel in a new container using a
notebook server on your host. One reason for this is to customize one notebook
server, and use it on many docker images.

# Example

## Running a new image (recommended, and only way working currently)

Docker running a new container for each ipython kernel

1. Add ipykernel to docker image. For example:

```dockerfile
RUN virtualenv /opt/bash; \
    VIRTUAL_ENV_DISABLE_PROMPT=1; \
    source /opt/bash/bin/activate; \
    pip --no-cache-dir install ipykernel
```

2. Add new kernel.json

```
{
 "display_name": "docker_test",
 "argv": [
  "/home/andy/note2/bin/python", "-m", "docker_proxy_kernel",
  "-f", "{connection_file}",
  "--image", "mykernel:latest",
  "--docker", "nvidia-docker",
  "--cmd", "['/opt/bash/bin/python', '-m', 'ipykernel']"
 ],
 "env": {},
 "language": "python"
}
```

# Other `docker_proxy_kernel` arguments

* `-h`/`--help` - Show help message and exit
* `-f CONNECTION_FILE` - Connection file
* `--image IMAGE` - Name of docker image to be run
* `--control CONTROL` - Docker control port
* `--hb HB` - Docker heart beat port
* `--iopub IOPUB` - Docker IO publish port
* `--shell SHELL` - Docker shell port
* `--stdin STDIN` - Docker stdin port
* `--docker DOCKER` - Docker executable used for running docker commands. Can
be full path, or point to a wrapper script to add arguments before the `run`
docker sub-command.
* `--cmd CMD` - The command executed in a docker. This argument must be a
python representation of a list of strings. e.g. "['sleep', '1']"
* `-- [OTHER] [DOCKER] [ARGUMENTS]` - Set of additional docker arguments that
will be inserted after the run sub-command but before the image name. This will
include anything you need to create your environment including port forwards,
mount directories, and etc...

## Using ssh

See `remote_kernel` or `rk` projects.

# Other ideas

- Connect to a running container (via `docker exec` or `import docker`). I
thought about this some, and since the notebook decides which ports it expects
to use docker exec on its own is impossible and using docker-py is no easier
than using docker cli configuration layer in kernel.json. In order to get
docker exec working, either:

    - Expose 5 ports before starting the container. And upon starting docker
      proxy kernel, start come tcp redirector to tunnel the traffic to the
      container
    - ~~Connect to the container, and use stdin/stdout to multiplex the 5 tcp
      ports in. Crazy for a number of reasons, flushing to begin with~~
    - ~~Use iptables to redirect the write port~~

- Support `docker-compose`. This would be less than straight forward. A new
  docker-compose.yml file will need to be created on the fly to add the 5 tcp
  ports that need exposing, and then start the container.
- Add a `manage` like `rk` and `remote_kernel`

# Bugs

- "I always have to change the kernel every time I want to change one of the
parameters." Yeah... I can't find any way to have notebook prompt you for a
question upon starting a kernel, and without that I can't come up with a better
experience.
- Cannot use python3/newer ipykernel on the docker side, bug in command line
argument parser