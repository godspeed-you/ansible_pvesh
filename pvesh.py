#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['stableinterface'],
    'supported_by': 'godspeed-you'
}

DOCUMENTATION = """
---
"""

EXAMPLES = """
---
"""

RETURN = """
---
"""

import subprocess
import json
from ansible.module_utils.basic import AnsibleModule

def execute_pvesh(handler, api_path, **params):
    command = [
        "/usr/bin/pvesh",
        handler.lower(),
        api_path,
        "--output=json"]
    for parameter, value in params.items():
        command += ["-%s" % parameter, "%s" % value]

    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (result, stderr) = pipe.communicate()

    if len(stderr) >= 1:
        try: # Sometimes pvesh is very kind and provides already a status code
            return dict(status=int(stderr[:4]),
                        stderr_message=stderr[:4],
                        result=result)
        except ValueError:
            status = 512

        if stderr.startswith("No '%s' handler defined for '%s'" % (handler, api_path)):
            status = 405
        elif "already exists" in stderr:
            status = 304
        elif "does not exist" in stderr or \
                "no such" in stderr or \
                "not found" in stderr:
            status = 404

        return dict(status=status,
                    stderr_message=stderr,
                    result=result)


    if handler in ['set', 'create', 'delete']:
        if not result:
            status = 204
        else:
            status = 201
    else:
        status = 200

    try:
        result = json.loads(result)
    except ValueError:
        pass

    return dict(status=status,
                stderr_message='',
                result=result)


def map_status(status, command):
    """ Each status code leads to a specific ansible status. We map that here!"""
    status_map = {'get': {200: 'ok'},
                  'set': {201: 'changed', 204: 'changed'},
                  'create': {201: 'changed', 204: 'changed', 304: 'ok'},
                  'delete': {201: 'changed', 204: 'changed', 404: 'ok'}}
    return status_map[command].get(status, 'failed')


def main():
    """ Main function to provide pvesh functionality as an Ansible module."""
    args = dict(
        handler=dict(type='str',
                     choices=['create', 'delete', 'get', 'ls', 'set', ],
                     required=True,
                     aliases=['command']),
        path=dict(type='str',
                  required=True),
        options=dict(type='dict',
                     required=False),
        )

    ansible = AnsibleModule(
        argument_spec=args,
        supports_check_mode=True)

    handler = ansible.params['handler']

    result = execute_pvesh(handler,
                           ansible.params['path'],
                           **ansible.params['options'])

    check_status = map_status(result['status'], handler)
    if check_status == 'ok':
        changed = False
    elif check_status == 'changed':
        changed = True
    elif check_status == 'failed':
        ansible.fail_json(msg=result.get('stderr_message'),
                          status=result.get('status'),
                          result=result['result'])

    ansible_result = dict(
        changed=changed,
        result=result,)

    ansible.exit_json(**ansible_result)

if __name__ == '__main__':
    main()
