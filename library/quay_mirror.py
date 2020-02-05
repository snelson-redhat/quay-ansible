#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: quay_mirror
short_description: Create a Quay Mirror
description:
     - Create and update a mirror in Quay.io or Quay Enterprise.
version_added: "2.9"
author: "Sean nelson (@audiohacked)"
options:
  auth:
    description:
     - Quay OAuth token. Can be specified in C(QUAY_API_KEY), C(QUAY_API_TOKEN), or C(QUAY_OAUTH_TOKEN) environment variables
    aliases: ['API_TOKEN']
    required: True
  state:
    description:
     - Indicate desired state of the target.
    default: enabled
    choices: ['enabled', 'disabled']
  name:
    description:
     - String, this is the name of the repo.
  is_enabled:
    description:
     - Enables the mirror Sync
  external_registry_config:
    options:
      proxy:
        options:
          https_proxy:
            description:
             - String, HTTPS Proxy
          http_proxy:
            description:
             - String, HTTP Proxy
          no_proxy:
            description:
             - String, No Proxy
  external_registry_username:
    description:
    - String, Username for External Registry
  external_registry_password:
    description:
    - String, Password for External Registry
  external_reference:
    description:
    - String, Location to Mirror
  sync_start_date:
    description:
    - String, ISO8601 Datetime
  root_rule:
    options:
    rule_type: "TAG_GLOB_CSV",
        description:
        - String, Required, Support
    rule_value:"string"
  sync_interval:
    description:
    - Integer, Sync Interval
  robot_username:
    description:
    - String, Robot Username
requirements:
  - "python >= 2.7"
'''


EXAMPLES = '''
- name: create a mirror
  quay_mirror:
    auth: XXX
    name: repo_name
    state: present
  register: my_repo

- debug:
    msg: "ID is {{ my_repo.data.repo.id }}"

- name: ensure a mirror is present
  quay_repo:
    auth: XXX
    name: repo_name
    state: present
'''


RETURN = '''
# Quay.io API info https://docs.quay.io/api/swagger/

'''

import traceback

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible.module_utils.quay.auth import QuayHelper  # pylint: disable=import-error, no-name-in-module
from ansible.module_utils.quay.mirror import QuayMirror  # pylint: disable=import-error, no-name-in-module


def main():
    def _enable():
        result["original_message"] = "Enabling Mirror: %s" % repo_name

        module.params.update(dict(
            is_enabled=True,
        ))

        # Make Change
        body = dict(module.params)
        result['data'] = quay_repo.create_mirror(repo_name, body)

        # Validate Change
        check = quay_repo.fetch_mirror(repo_name)
        if check['body']['is_enabled'] is False:
            module.fail_json(msg="Mirror Enablement Failed!")
        else:
            result['message'] = "Mirror Enabled!"
            result['changed'] = True
        module.exit_json(**result)

    def _disable():
        result["original_message"] = "Disabling Mirror: %s" % repo_name

        module.params.update(dict(
            is_enabled=False,
        ))

        # Make Change
        body = dict(module.params)
        result['data'] = quay_repo.update_mirror(repo_name, body)

        # Validate Change
        check = quay_repo.fetch_mirror(repo_name)
        if check['body']['is_enabled'] is False:
            result['message'] = "Mirrror Disabled!"
            result['changed'] = True
        else:
            module.fail_json(msg="Mirror Disablement Failed!")
        module.exit_json(**result)

    argument_spec = dict(
        # Quay API parameters
        auth=dict(type='str', fallback=(env_fallback, ['QUAY_AUTH_TOKEN'])),
        endpoint=dict(type='str', default='quay.io'),

        # Ansible parameters
        name=dict(type='str', required=True),
        state=dict(type='str', default='enabled', choices=['disabled', 'enabled']),

        # Creation parameters
        # is_enabled: true
        external_registry_config=dict(type='dict', default='{}', options=dict(
            proxy=dict(type='dict', default='{}', options=dict(
                https_proxy=dict(type='str', default=''),
                http_proxy=dict(type='str', default=''),
                no_proxy=dict(type='str', default='')
            ))
        )),
        external_registry_username=dict(type='str', default=''),
        external_registry_password=dict(type='str', default=''),
        external_reference=dict(type='str'),
        sync_start_date=dict(type='str'),
        root_rule=dict(type='dict', options=dict(
            rule_type=dict(type='str', default='TAG_GLOB_CSV'),
            rule_value=dict(type='str', required=True)
        )),
        sync_interval=dict(type='int'),
        robot_username=dict(type='str'),
    )

    result = dict(
        changed=False,
        original_message='',
        message='',
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=(['name']),
        required_if=([
            ('state', 'enabled', ['external_reference', 'root_rule']),
        ]),
        supports_check_mode=True,
    )

    if module.check_mode:
        module.exit_json(**result)

    try:
        state = module.params.pop('state')
        auth = module.params.pop('auth')
        endpoint =  module.params.pop('endpoint')
        repo_name = module.params.pop('name')

        quay_helper = QuayHelper(module, auth, endpoint)
        quay_repo = QuayMirror(module, quay_helper)

        repo_exists = quay_repo.exists(repo_name)

        if repo_exists is False:
            module.fail_json(msg="Repository Missing!")

        if state == 'enabled':
            _enable()
        elif state == 'disabled':
            _disable()
        else:
            module.fail_json(msg="Invalid given state!")
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == "__main__":
    main()
