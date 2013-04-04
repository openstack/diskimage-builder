Command line utilities to simplify instalation of OpenStack services.

## os-svc-install
Given a git repo url, pip-install the repo and all of its python dependencies into a virtualenv under /opt/stack/venvs.

## os-svc-daemon
Given a system service command line and run-as user, generate and install system service start script.


## example usage
```bash
# clone nova.git from github, and install it and its dependencies to /opt/stack/venvs/nova
os-svc-install -u nova -n nova-all -c 'nova-all --someoption' -r https://github.com/openstack/nova.git

# install a system-start script for nova-api
os-svc-daemon nova-api nova /opt/stack/venvs/nova/bin/nova-api --config-dir /etc/nova
```

