#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '0.2',
    'status': ['preview'],
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
                        result=result,
                        command=command)
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
                    result=result,
                    command=command)


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
                result=result,
                command=command)


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
                     default={},
                     required=False),
        )

    ansible = AnsibleModule(
        argument_spec=args,
        supports_check_mode=True)

    handler = ansible.params['handler']
    path = ansible.params['path']
    options = ansible.params['options']

    result = execute_pvesh(handler, path, **options)
    status = result['status']
    command = result['command']
    result_final = result['result']

    check_status = map_status(status, handler)
    if check_status == 'ok':
        changed = False
    elif check_status == 'changed':
        changed = True
    elif check_status == 'failed':
        ansible.fail_json(msg=result.get('stderr_message'),
                          status=status,
                          result=result_final,
                          command=' '.join(command))

    ansible_result = dict(
        status=status,
        changed=changed,
        result=result_final,
        command=' '.join(command))

    ansible.exit_json(**ansible_result)

if __name__ == '__main__':
    main()
