from core_helper import CoreHelper

ch = CoreHelper()
computers = ch.get_stack_servers(sys.argv[1:])

with open('/tmp/deploy.json', 'w') as fh:
  fh.write(json.dumps(computers))
