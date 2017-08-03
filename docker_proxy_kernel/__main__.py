#!/usr/bin/env python

# from ipykernel.kernelapp import IPKernelApp
# from .kernel import BashKernel
# IPKernelApp.launch_instance(kernel_class=BashKernel)

import json
import shlex
import sys

from subprocess import Popen
from os import environ as env
from uuid import uuid4

import jupyter_client.session
import jupyter_client.manager


class DockerProxyKernel(object):
  def __init__(self):
    pass

  def stop_kernel(self):
    ''' Stop the kernel running in the docker

    Since this is a proxy kernel, instead of handling the shutdown locally,
    just send this signal along, since any kernel can be used in the container,
    not just ipykernel.
    '''

    kernal_manager = jupyter_client.manager.KernelManager(
        iopub_port=self.iopub_port, hb_port=self.hb_port,
        shell_port=self.shell_port, stdin_port=self.stdin_port,
        control_port=self.control_port, transport='tcp',
        session=jupyter_client.session.Session(
            key=b"87e8bcbe-3224ff63a4f5f5d049ef6ce5",
            signature_scheme='hmac-sha256'))

    kernal_manager.request_shutdown()

  def start_kernel(self, connection_file,
                   docker_control_port=10000, docker_hb_port=10001,
                   docker_iopub_port=10002):
    ''' Start the kernel in a docker

    Args:
        connection_file - JSON file containing the connection information

    Environment Variables:
        IPYTHON_DOCKER_IMAGE - Required: Name of the docker image to be run

        IPYTHON_DOCKER_ARGUMENTS - A sting that will be turned into an array of
                                   arguments to send to the docker command
                                   using shlex.split. Default: None
                                   Example: '-e TEST="test this"'.
        DOCKER_EXE - Name of the docker executable, can be a full path.
                     Default: docker
        IPYTHON_CONTROL_PORT - The control port of the kernel on the docker
                               side. Default: 10000
        IPYTHON_HB_PORT - The hb port of the kernel on the docker side.
                          Default: 10001
        IPYTHON_IOPUB_PORT - The iopub port of the kernel on the docker side.
                             Default: 10002
        IPYTHON_SHELL_PORT - The shell port of the kernel on the docker side.
                             Default: 10003
        IPYTHON_STDIN_PORT - The stdin port of the kernel on the docker side.
                             Default: 10004
    '''

    # Load json config
    with open(connection_file, 'r') as fid:
      config = json.load(fid)

      # Add docker settings
      config.update({
          'docker_control_port': env.get('IPYTHON_CONTROL_PORT', '10000'),
          'docker_hb_port': env.get('IPYTHON_HB_PORT', '10001'),
          'docker_iopub_port': env.get('IPYTHON_IOPUB_PORT', '10002'),
          'docker_shell_port': env.get('IPYTHON_SHELL_PORT', '10003'),
          'docker_stdin_port': env.get('IPYTHON_STDIN_PORT', '10004')})

      if 'IPYTHON_DOCKER_IMAGE' in env:
        docker_exe = env.get('DOCKER_EXE', 'docker')

        docker_image = env['IPYTHON_DOCKER_IMAGE']

        docker_name = uuid4()

        docker_arguments = shlex.split(env.get('IPYTHON_DOCKER_ARGUMENTS', ''))

        command = [docker_exe, 'run', '-i', '--rm',
                   '-p', '{control_port}:{docker_control_port}'.format(
                       **config),
                   '-p', '{hb_port}:{docker_hb_port}'.format(**config),
                   '-p', '{iopub_port}:{docker_iopub_port}'.format(**config),
                   '-p', '{shell_port}:{docker_shell_port}'.format(**config),
                   '-p', '{stdin_port}:{docker_stdin_port}'.format(**config),
                   '--name={}'.format(docker_name),
                   docker_image] + docker_arguments + \
                  ["--control={docker_control_port}".format(**config),
                   "--hb={docker_hb_port}".format(**config),
                   "--iopub={docker_iopub_port}".format(**config),
                   "--shell={docker_shell_port}".format(**config),
                   "--stdin={docker_stdin_port}".format(**config),
                   "--ip=0.0.0.0",
                   "--transport=tcp",
                   "--Session.signature_scheme=hmac-sha256",
                   "--Session.key=b'{key}'".format(**config)]

      elif 'DOCKER_COMPOSE_SERVICE' in env:
        docker_compose_exe = env.get('DOCKER_COMPOSE_EXE', 'docker-compose')
        command = [docker_compose_exe, 'run', '-T', '--rm']

    try:
      Popen(command).wait()
    except KeyboardInterrupt:
      print('KeyboardInterrupt!!!')
