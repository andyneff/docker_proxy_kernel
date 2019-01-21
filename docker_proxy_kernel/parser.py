#!/usr/bin/env python
import argparse
import ast
import shlex


class ArgsAction(argparse.Action):
  def __init__(self, option_strings, dest, nargs=None, **kwargs):
    if nargs is not None:
      raise ValueError("nargs not allowed")
    super(ArgsAction, self).__init__(option_strings, dest, **kwargs)

  def __call__(self, parser, namespace, values, option_string=None):
    if len(values) and values[0] == '[':
      values = ast.literal_eval(values)
    else:
      values = shlex.split(values)
    setattr(namespace, self.dest, values)


def get_parser():
  parser = argparse.ArgumentParser(
      prog='docker_proxy_kernel',
      formatter_class=argparse.RawDescriptionHelpFormatter,
      description='Start a docker proxy Kernel',
      epilog='Sample Dockerfile: \n\n'
             'FROM nvidia/cuda\n'
             'RUN apt-get update && \\\n'
             '    apt-get install -y virtualenv python3-dev\n'
             'RUN virtualenv "/opt/virtual env" -p `which python3` && \\\n'
             '    PS1=: && source "/opt/virtual env/bin/activate" && \\\n'
             '    pip install ipykernel\n\n\n'
             'Example args: \n\n'
             'python -m docker_docker_proxy_kernel \\\n'
             '  --image username/project --control 32045 --hb 12342 \\\n'
             '  --iopub 36798 --shell 22131 --stdin=55237 '
             '--docker nvidia-docker \\\n'
             '  --cmd \'["/opt/virtual env/bin/python", "-m", "ipykernel"]\' '
             '\\\n'
             '  -- -p 443:443 -e IMPORTANT_VAR="just this"')
  aa = parser.add_argument
  aa('-f', dest='connection_file', type=str, help='Connection file',
     required=True)
  aa('--image', type=str, help='Name of docker image to be run', required=False)
  aa('--control', type=int, help='Docker control port', default=10000)
  aa('--hb', type=int, help='Docker heart beat port', default=10001)
  aa('--iopub', type=int, help='Docker IO publish port', default=10002)
  aa('--shell', type=int, help='Docker shell port', default=10003)
  aa('--stdin', type=int, help='Docker stdin port', default=10004)
  aa('--docker', type=str, default=['docker'], action=ArgsAction,
     help='Docker executable used for running docker commands. '
          'Can be full path')
  aa('--cmd', type=str, default=[], action=ArgsAction,
     help='The command executed in a docker. This argument must be a python '
          'representation of a list of strings. e.g. "[\'sleep\', \'1\']"')
  aa('docker_args', nargs='*', default=[],
     help='Additional docker arguments added to docker run. You will probably '
          'want to add -- before all the docker arguments.')

  return parser
