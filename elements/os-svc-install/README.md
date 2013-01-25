Installs 'os-svc-install', a script to perform one-line installs of init-controlled openstack services from github.


Example Usage
--------------
`os-svc-install -u nova -n nova-all -c 'nova-all --someoption' -r https://github.com/openstack/nova.git`

The above command will pip-install the repo specified by '-r', and create a service start script called nova-all (from `-n`), which starts the command specified by `-c` as user `-u`

