#!/usr/bin/env python

import os
import sys
import json

from core_helper import CoreHelper

if len(sys.argv) < 2:
    prog = os.path.basename(sys.argv[0])
    sys.exit('usage: {} ACCOUNT_NUMBER'.format(prog))

ch = CoreHelper()
computers = ch.get_stack_servers(sys.argv[1:])

print('Writing server list from CORE to /tmp/deploy.json')

try:
    with open('/tmp/deploy.json', 'w') as fh:
        data = json.dumps(computers, indent=4)
        fh.write(data)
        print(data)
except Exception as e:
    print('ARGGGGGGGGGGGGG! {}'.format(e.message))
else:
    print('OK, bye!')
