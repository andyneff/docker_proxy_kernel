FROM nvidia/cuda

SHELL ["bash", "-xveuEc"]

RUN apt-get update; \
    apt-get install --no-install-recommends virtualenv python3-dev -y

RUN virtualenv /opt/docker_venv -p `which python3`; \
    PS1=: ;\
    source /opt/docker_venv/bin/activate; \
    pip --no-cache-dir install ipykernel

RUN PS1=: ;\
    source /opt/docker_venv/bin/activate; \
    pip --no-cache-dir install bash_kernel

# Sample kernel.json
#{
# "display_name": "docker_test",
# "argv": [
#  "/home/user/venv/bin/python", "-m", "docker_proxy_kernel",
#  "-f", "{connection_file}",
#  "--image", "test_kernel:latest",
#  "--docker", "nvidia-docker",
#  "--cmd", "['/opt/docker_venv/bin/python', '-m', 'ipykernel']"
# ],
# "env": {},
# "language": "python"
#}
