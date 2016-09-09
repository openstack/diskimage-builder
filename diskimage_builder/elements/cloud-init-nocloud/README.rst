==================
cloud-init-nocloud
==================
Configures cloud-init to only use on-disk metadata/userdata sources. This
will avoid a boot delay of 2 minutes while polling for cloud data sources
such as the EC2 metadata service.

Empty on-disk sources are created in /var/lib/cloud/seed/nocloud/.

