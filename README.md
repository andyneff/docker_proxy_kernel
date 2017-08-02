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

2. Add connection.json

```
TODO: Currently entrypoint in POC. /tmp/connection.json
```

3. Add new kernel.json

```
{
 "display_name": "docker_test",
 "argv": [
  "/home/me/my_venv/bin/python", "-m", "docker_proxy_kernel", "{connection_file}",
  "/opt/bash/bin/python", "-m", "ipykernel", "-f", "/tmp/connection.json"
 ],
 "env": {
  "docker_image": "kernel:latest"
 },
 "language": "python"
}
```

4. Customizing the kernel on the docker side

{
 "display_name": "docker_test",
 "argv": [
  "/home/andy/note2/bin/python", "-m", "docker_proxy_kernel", "{connection_file}",
  "/opt/bash/bin/python", "-m", "ipykernel"
 ],
 "env": {
  "docker_image": "kernel:latest",
  "IPYTHON_CONTROL_PORT": "50011",
  "IPYTHON_HB_PORT": "50001",
  "IPYTHON_IOPUB_PORT": "50002",
  "IPYTHON_SHELL_PORT": "50003",
  "IPYTHON_STDIN_PORT": "50004"
 },
 "language": "python"
}


## Running in an existing container (More difficult)

1. Start docker 

...

## Using ssh

See `remote_kernel` or `rk` projects.