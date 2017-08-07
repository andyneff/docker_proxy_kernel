#!/usr/bin/env python
import argparse
import json
import os
import sys

from jupyter_core.paths import jupyter_data_dir


def main():
  parser = argparse.ArgumentParser()
  aa = parser.add_argument
  aa('-n', '--name', nargs=1, required=1, help='Display name of kernel')
  aa('-i', '--image', nargs=1, required=1,
     help='Docker image used for creating docker containers to proxy into')
  aa('--kernel-dir-name', nargs=1, default=None,
     help='Optionally override the kernel directory name. Not a full path.')
  aa('other_args', nargs='*', default=[],
     help='Additional arguments to pass to kernel')
  args = parser.parse_args()

  kernel_name = args.name[0]
  kernel_dir = os.path.join(jupyter_data_dir(), 'kernels')
  if args.kernel_dir_name:
    kernel_dir = os.path.join(kernel_dir, args.kernel_dir_name)
  else:
    kernel_dir = os.path.join(kernel_dir, kernel_name.replace('/', ''))

  if not os.path.exists(kernel_dir):
    os.makedirs(kernel_dir)
  else:
    raise Exception('Kernel directory exists')

  kernel = {'display_name': kernel_name,
            'argv': [sys.executable, '-m', 'docker_proxy_kernel',
                     '-f', '{connection_file}',
                     '--image', args.image[0]] + args.other_args,
            'env': {}, 'language': 'python'}

  with open(os.path.join(kernel_dir, 'kernel.json'), 'w') as fid:
    json.dump(kernel, fid, indent=2)


if __name__ == '__main__':
  main()
