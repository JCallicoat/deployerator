#!/usr/bin/env python

import re
import sys
import json
import argparse

computers = []
with open('/tmp/deploy.json') as fh:
  computers = json.loads(fh.read())
ids = [str(c['server']) for c in computers]

# generate ssh keys on all hosts if they do not exist
with open('/tmp/script.sh', 'w') as fh:
  fh.write('''
  #!/bin/bash
  ssh-keygen -f /root/.ssh/id_rsa -t rsa -N \'\'
  ''')
ch.run_script(ids, '/tmp/script.sh')
# ch.run_command(ids, 'ssh-keygen -f /root/.ssh/id_rsa -t rsa -N ""')

# get the public keys so we can add them to .authorized_keys
for computer in computers:
  tmpfile = '/tmp/{}_id_rsa.pub'.format(computer['server'])
  ch.copy_file('{}:/root/.ssh/id_rsa.pub'.format(computer['server']), tmpfile, True)
  with open(tmpfile) as fh:
    computer['public_key'] = fh.read().strip()

def prep_common(computer):
  print('--------\nSTART COMMON PREP ON {}'.format(computer['server_name']))
  print(computer['public_key'])
  # set /etc/hosts
  # setup dsh / groups
  print('END COMMON PREP ON {}\n--------'.format(computer['server_name']))

def prep_controller(computer):
  print('START CONTROLLER PREP ON {}'.format(computer['server_name']))
  print('END CONTROLLER PREP ON {}'.format(computer['server_name']))

def prep_compute(computer):
  print('START COMPUTE PREP ON {}'.format(computer['server_name']))
  print('END COMPUTE PREP ON {}'.format(computer['server_name']))

def prep_cinder(computer):
  print('START CINDER PREP ON {}'.format(computer['server_name']))
  print('END CINDER PREP ON {}'.format(computer['server_name']))

def prep_swift(computer):
  print('START SWIFT PREP ON {}'.format(computer['server_name']))
  print('END SWIFT PREP ON {}'.format(computer['server_name']))


controller_re = r'controller|infra'
compute_re = r'compute|cpu'
cinder_re = r'cinder'
swift_re = r'swift'

for computer in computers:
  prep_common(computer)
  if re.search(controller_re, computer['server_name']):
    prep_controller(computer)
  elif re.search(compute_re, computer['server_name']):
    prep_compute(computer)
  elif re.search(cinder_re, computer['server_name']):
    prep_cinder(computer)
  elif re.search(swift_re, computer['server_name']):
    prep_swift(computer)
  else:
    print('WTF KIND OF THING ARE YOU GIVING ME?!!')
    print(json.dumps(computer, indent=4))
