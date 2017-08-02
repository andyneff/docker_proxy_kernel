import json
import sys
from subprocess import Popen
from os import environ as env

if __name__ == '__main__':
  # Get client (host) side information
  with open(sys.argv[1], 'r') as fid:
    config = json.load(fid)

  config.update({
      'docker_control_port': env.get('IPYTHON_CONTROL_PORT', '10000'),
      'docker_hb_port': env.get('IPYTHON_HB_PORT', '10001'),
      'docker_iopub_port': env.get('IPYTHON_IOPUB_PORT', '10002'),
      'docker_shell_port': env.get('IPYTHON_SHELL_PORT', '10003'),
      'docker_stdin_port': env.get('IPYTHON_STDIN_PORT', '10004')})

  if 'docker_image' in env:
    docker_image = env['docker_image']

    command = ['docker', 'run', '-i', '--rm',
               '-p', '{control_port}:{docker_control_port}'.format(**config),
               '-p', '{hb_port}:{docker_hb_port}'.format(**config),
               '-p', '{iopub_port}:{docker_iopub_port}'.format(**config),
               '-p', '{shell_port}:{docker_shell_port}'.format(**config),
               '-p', '{stdin_port}:{docker_stdin_port}'.format(**config),
               docker_image] + sys.argv[2:] + \
              ["--control={docker_control_port}".format(**config),
               "--hb={docker_hb_port}".format(**config),
               "--iopub={docker_iopub_port}".format(**config),
               "--shell={docker_shell_port}".format(**config),
               "--stdin={docker_stdin_port}".format(**config),
               "--ip=0.0.0.0",
               "--transport=tcp",
               "--Session.signature_scheme=hmac-sha256",
               "--Session.key={key}".format(**config)]

  elif 'docker_container' in env:
    docker_container = env['docker_container']
  elif 'docker_compose_service' in env:
    command = []

  Popen(command).wait()
