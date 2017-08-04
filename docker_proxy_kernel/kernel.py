#!/usr/bin/env python
import json
import signal

import six
from subprocess import Popen
from uuid import uuid4

import jupyter_client.session
import jupyter_client.manager


class DockerProxyKernel(object):
  def __init__(self):
    pass

  def register_signals(self, signals=['CTRL_C_EVENT', 'SIGTERM', 'SIGINT']):
    for s in signals:
      if hasattr(signal, s):
        signal.signal(getattr(signal, s), self.stop_kernel)

  def stop_kernel(self, signum, frame):
    ''' Stop the kernel running in the docker

    Since this is a proxy kernel, instead of handling the shutdown locally,
    just send this signal along, since any kernel can be used in the container,
    not just ipykernel.
    '''

    kernal_manager = jupyter_client.manager.KernelManager(
        iopub_port=self.config['iopub_port'],
        hb_port=self.config['hb_port'],
        shell_port=self.config['shell_port'],
        stdin_port=self.config['stdin_port'],
        control_port=self.config['control_port'],
        transport=self.config['transport'],
        session=jupyter_client.session.Session(
            key=six.b(self.config['key']),
            signature_scheme=self.config['signature_scheme']))

    kernal_manager.request_shutdown()

    # If this isn't enough, start adding docker kills, and more aggressive
    # ideas

  def start_kernel(self, connection_file, docker_image,
                   docker_control_port=10000, docker_hb_port=10001,
                   docker_iopub_port=10002, docker_shell_port=10003,
                   docker_stdin_port=10005, docker='docker',
                   docker_arguments=[], cmd=[]):
    ''' Start the kernel in a docker

    Args:
        connection_file - JSON file containing the connection information

    '''

    # Load json config
    with open(connection_file, 'r') as fid:
      self.config = json.load(fid)

      # Add docker settings
      self.config.update({'docker_control_port': docker_control_port,
                          'docker_hb_port': docker_hb_port,
                          'docker_iopub_port': docker_iopub_port,
                          'docker_shell_port': docker_shell_port,
                          'docker_stdin_port': docker_stdin_port})

      docker_name = uuid4()

      if docker_image:

        command = docker + \
            ['run', '-i', '--rm',
             '-p', '{control_port}:{docker_control_port}'.format(
                 **self.config),
             '-p', '{hb_port}:{docker_hb_port}'.format(**self.config),
             '-p', '{iopub_port}:{docker_iopub_port}'.format(**self.config),
             '-p', '{shell_port}:{docker_shell_port}'.format(**self.config),
             '-p', '{stdin_port}:{docker_stdin_port}'.format(**self.config),
             '--name={}'.format(docker_name)] + docker_arguments + \
            [docker_image] + cmd + \
            ["--control={docker_control_port}".format(**self.config),
             "--hb={docker_hb_port}".format(**self.config),
             "--iopub={docker_iopub_port}".format(**self.config),
             "--shell={docker_shell_port}".format(**self.config),
             "--stdin={docker_stdin_port}".format(**self.config),
             "--ip=0.0.0.0", "--transport={transport}".format(**self.config),
             "--Session.signature_scheme={signature_scheme}".format(
                 **self.config),
             "--Session.key=b'{key}'".format(**self.config)]
      else:
        raise Exception('No docker_image argument')

    try:
      Popen(command).wait()
    except KeyboardInterrupt:
      self.stop_kernel()
