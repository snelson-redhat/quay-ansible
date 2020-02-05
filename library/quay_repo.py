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
module: quay_repo
short_description: Create and delete a Quay Repo
description:
     - Create and delete a repository in Quay.io or Quay Enterprise.
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
    default: present
    choices: ['present', 'absent']
  name:
    description:
     - String, this is the name of the repo.
    required: True
  repo_kind:
    description:
     - String, this is the type of repo
    default: image
    choices: ['image', 'application']
  namespace:
    description:
     - String, Namespace of the Repo
  visibility:
    description:
     - String, Visibility of the Repo
  repository:
    description:
     - String, Name of the Repo
  description:
    description:
     - String, Name of the Repo
requirements:
  - "python >= 2.7"
'''


EXAMPLES = '''
- name: create a new quay repo
  quay_repo:
    auth: XXX
    name: repo_name
    state: present
  register: my_repo

- debug:
    msg: "ID is {{ my_repo.data }}"

- name: ensure a quay repo is present
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
from ansible.module_utils.quay.repository import QuayRepository  # pylint: disable=import-error, no-name-in-module


def main():
    def _present():
        result["original_message"] = "Creating Repository: %s" % repo_name
        if repo_exists is False:
            # Gather data
            body = dict(module.params)

            # Make Change
            result['data'] = quay_repo.create(body)

            # Validate Change
            check_exists = quay_repo.exists(repo_name)
            if check_exists is False:
                module.fail_json(msg="Repository Creation Failed!")
            else:
                result['message'] = "Repository Created!"
                result['changed'] = True
        else:
            result['message'] = "Repository Already Present!"
        module.exit_json(**result)

    def _absent():
        result["original_message"] = "Deleting Repository: %s" % repo_name
        if repo_exists is True:
            # Make Change
            result['data'] = quay_repo.delete(repo_name)

            # Validate Change
            check_exists = quay_repo.exists(repo_name)
            if check_exists is False:
                result['message'] = "Repository Deleted!"
                result['changed'] = True
            else:
                module.fail_json(msg="Repository Deletion Failed!")
        else:
            result['message'] = "Repository Already Deleted!"
        module.exit_json(**result)

    argument_spec = dict(
        # Quay API parameters
        auth=dict(type='str', fallback=(env_fallback, ['QUAY_AUTH_TOKEN'])),
        endpoint=dict(type='str', default='quay.io'),

        # Module parameters
        name=dict(type='str'),
        state=dict(type='str', default='present', choices=['absent', 'present']),

        # Creation parameters
        repo_kind=dict(type='str', default='image', choices=['image', 'application']),
        visibility=dict(type='str', default='public', choices=['public', 'private']),
        description=dict(type='str', default=''),
        namespace=dict(type='str'),
        repository=dict(type='str'),
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        required_one_of=(['name']),
        required_together=([
            ('namespace', 'repository')
        ]),
    )

    if module.check_mode:
        module.exit_json(**result)

    try:
        state = module.params.pop('state')
        auth = module.params.pop('auth')
        endpoint =  module.params.pop('endpoint')
        repo_name = module.params.pop('name')

        if module.params['namespace'] is None or module.params['repository'] is None:
            namespace = '/'.join(repo_name.split('/')[0:-1])
            repository = repo_name.split('/').pop()
            module.params.update(dict(
                namespace=str(namespace),
                repository=str(repository),
            ))

        quay_helper = QuayHelper(module, auth, endpoint)
        quay_repo = QuayRepository(module, quay_helper)

        repo_exists = quay_repo.exists(repo_name)

        if state == 'present':
            _present()
        elif state == 'absent':
            _absent()
        else:
            module.fail_json(msg="Invalid given state!")

    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())


if __name__ == "__main__":
    main()
