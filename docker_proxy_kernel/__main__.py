#!/usr/bin/env python

from .kernel import DockerProxyKernel
from .parser import get_parser

from .parentpoller import setup_parent_poller

# get and parse arguments
inputs = get_parser().parse_args()

# Start proxy kernel setup
kernel = DockerProxyKernel()
kernel.register_signals()

# Start parent poller
setup_parent_poller(lambda: kernel.stop_kernel(None, None))

# Start kernel and wait for docker run to die off
kernel.start_kernel(cmd=inputs.cmd,
                    connection_file=inputs.connection_file,
                    docker_image=inputs.image,
                    docker_control_port=inputs.control,
                    docker_hb_port=inputs.hb,
                    docker_iopub_port=inputs.iopub,
                    docker_shell_port=inputs.shell,
                    docker_stdin_port=inputs.stdin,
                    docker=inputs.docker,
                    docker_arguments=inputs.docker_args)
