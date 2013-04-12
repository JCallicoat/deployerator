import re
import json
import xmlrpclib

# let hammertime do the heavy lifting for us!
from hammertime.config import HammerTimeConfig
from hammertime.core import HammerTimeCore
from hammertime.login import HammerTimeLogin
from hammertime.ipcommander import HammerTimeIPCommander
from hammertime.cache import HammerTimeCache


class CoreHelper(object):

  config = HammerTimeConfig(
   {
   'nocolor': True,
   'skiproot': False,
   'show_passwords': False,
   'expect_timeout': 60,
   'ssh_args': '',
   'terminal': None,
   'quiet': False,
   }
  )

  cache = HammerTimeCache(config)
  core = HammerTimeCore(cache)
  ipc = HammerTimeIPCommander()

  login = HammerTimeLogin(core=core, ipc=ipc, config=config, rack=False,
                          sudo_make_me_a_sandwich=True, root_access='su',
                          port=22, no_sqlite=False)

  os_re = r'(compute|controller|cpu|infra|cinder|swift)'

  def try_method(self, method, *args, **kwargs):
    try:
      return method(*args, **kwargs)
    except xmlrpclib.Fault:
      self.core.reAuth()
      try:
        return method(*args, **kwargs)
      except xmlrpclib.Fault:
        return None

  def get_stack_servers(self, accounts=[], ids_only=False):
    if not accounts:
      return []

    # core.computerItems = [ "lead_tech", "lead_tech_id",
    # "account_manager", "old_status_number", "emergency_instructions",
    # "port", "customer_name", "business_development_id",
    # "attached_devices", "server_name", "offline_date",
    # "is_hypervisor", "online_date", "gateway", "platform",
    # "platform_instructions", "attribute_icons", "managed_storage_type",
    # "is_uk_account", "icon", "account_manager_id",
    # "date_contract_received", "status", "due_date", "service_level",
    # "primary_ip", "old_status", "segment", "platform_model",
    # "is_virtual_machine", "status_number", "customer", "datacenter",
    # "non_networked_net_devices", "os_group", "has_managed_storage",
    # "is_critical_sites_device", "server", "server_number",
    # "business_development", "has_managed_backup", "customer_type",
    # "team", "os", "has_openstack_role" ]
    include = ['server', 'server_name', 'has_openstack_role', 'os']
    devices = self.try_method(self.core.getDetailsByAccounts, accounts,
                              self.core.getComputerExcludeItems(include))

    computers = []
    for device in devices:
      if device.get('has_openstack_role', None):
        if re.search(self.os_re, device['server_name']):
          if ids_only:
            computers.append(str(device['server']))
          else:
            secrets = self.try_method(self.core.getSecrets,
                                      device['server'])
            device['admin_user'] = secrets['admin']['user_id']
            device['admin_pass'] = secrets['admin']['password']
            device['primary_ip'] = self.try_method(self.ipc.primaryIp,
                                                   device['server'])
            computers.append(device)

    return computers

  def run_command(self, computers, command):
    return self.login.script(','.join(computers), command, False)

  def run_script(self, computers, script):
    return self.login.script(','.join(computers), script, True)

  def copy_file(self, copy_from, copy_to, echo=False):
    return self.login.copy(copy_from, copy_to, echo)

