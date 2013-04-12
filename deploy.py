#!/usr/bin/env python

import os
import re
import sys
import json
import argparse

from paramiko import SSHClient, SSHConfig, ProxyCommand, AutoAddPolicy, \
                     SSHException


config = SSHConfig()
with open(os.path.expanduser('~/.ssh/config')) as fh:
    config.parse(fh)


def ssh_command(computer, command):
    global config
    opts = config.lookup(computer['primary_ip'])

    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    try:
        ssh.connect(computer['primary_ip'],
                    username=computer['admin_user'],
                    password=computer['admin_pass'],
                    sock=ProxyCommand(opts['proxycommand']))
        stdin, stdout, stderr = ssh.exec_command(command)
        stdin.close()
        result = stdout.read()
        ssh.close()
    except SSHException:
        print('DANGER WILL ROBINSON!!!!!!!'
              'ERROR CONNECTING TO {}\nSKIPPING HOST!'\
              .format(computer['primary_ip']))
        computer['skip'] = True
        result = []
    return result


computers = []
try:
    with open('/tmp/deploy.json') as fh:
        computers = json.loads(fh.read())
except Exception as e:
    sys.exit('ARGGGGGGGGGG! {}'.format(e.message))


# generate ssh keys on all hosts if they do not exist
# get the public keys so we can add them to .authorized_keys
for computer in computers:
    if not ssh_command(computer, 'ls /root/.ssh/id_rsa'):
        print(ssh_command(computer,
                          'ssh-keygen -f /root/.ssh/id_rsa -t rsa -N ""'))
    computer['public_key'] = ssh_command(computer,
                                         'cat /root/.ssh/id_rsa')

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
    if computer.get('skip'):
        continue
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
