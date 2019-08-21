# ansible_pvesh
## A wrapper for the Proxmox API on command line

This module was inspired by the great work of [lae](https://github.com/lae). It extends his approach to use the shell wrapper for the Proxmox API.

This way it is not neccessary anymore to provide user/password/url to use the API of proxmox. The regular ssh login is sufficient to use the API. 

This module enables the configuration of a Proxmox cluster with all features of the official API. You will need to study the documentation, which can be found here: [Proxmox API viewer](https://pve.proxmox.com/pve-docs/api-viewer/)

### Syntax of the module

The module tries to be as simple as possible. The mandatory keys are the `command` to use and the `path` to work on. All other keys are summarized in `options`. So a basic usage would look like:

    - name:
      pvesh:
        command: create
        path: access/users
        options:
          userid: myUser
          comment: an example User for demonstration
          email: example@mydomain.net

### ToDo

* Add ansible specific meta data in module
* Add `state` as key
* Validate if an item exists before trying to add/modify it
* ???
