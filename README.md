# Example

## Running a new image (recommended)

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
  "/home/me/my_venv/bin/python", "-m", "docker_proxy_kernel", "{connection_file}",
  "/opt/bash/bin/python", "-m", "ipykernel", "-f", "/tmp/connection.json"
 ],
 "env": {
  "IPYTHON_DOCKER_IMAGE": "kernel:latest"
 },
 "language": "python"
}
```

3. Optional: Customizing the kernel on the docker side

{
 "display_name": "docker_test",
 "argv": [
  "/home/andy/note2/bin/python", "-m", "docker_proxy_kernel", "{connection_file}",
  "/opt/bash/bin/python", "-m", "ipykernel"
 ],
 "env": {
  "IPYTHON_DOCKER_IMAGE": "kernel:latest",
  "IPYTHON_CONTROL_PORT": "50011",
  "IPYTHON_HB_PORT": "50001",
  "IPYTHON_IOPUB_PORT": "50002",
  "IPYTHON_SHELL_PORT": "50003",
  "IPYTHON_STDIN_PORT": "50004",
  "DOCKER_ARGUMENTS": "-e TEST=5 -v'/dir/with spaces':/dock/new\ dir --privileged"
 },
 "language": "python"
}

## Using docker compose

## Using nvidia-docker (or other plugins)

Add `DOCKER_EXE` to the `env` to specify `nvidia-docker`. For `docker-compose`,
use `DOCKER_COMPOSE_EXE`

## Using ssh

See `remote_kernel` or `rk` projects.

# Other ideas

- Connect to a running container (via `docker exec` or `import docker`). I
thought about this some, and since the notebook decided which ports it expects
to use
- Add a `manage` like `rk` and `remote_kernel`

# Bugs

- `jupyter notebook` hangs when Ctrl+C. Cause, probably doesn't know the docker
kernels it told to stop are stopped, so it is still waiting.
- Various other corner cases will leave a running container behind
- "I always have to change the kernel every time I want to change one of the
parameters." Yeah... I can't find any way to have notebook prompt you for a
question upon starting a kernel, and without that I can't come up with a better
experience.
- Cannot use python3/newer ipykernel on the docker side, bug in command line
argument parser
- You cannot specify a docker container name