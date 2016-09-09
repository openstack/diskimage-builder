=======
svc-map
=======
Map service names to distro specific services.

Provides the following:

 * bin/svc-map

   usage: svc-map [-h] SERVICE

   Translate service name to distro specific name.

   optional arguments:
     -h, --help         show this help message and exit

 * Any element may create its own svc-map YAML config file using
   the one of 3 sections for the distro/family/ and or default.
   The family is set automatically within svc-map based on
   the supplied distro name. Families include:

     + redhat: includes centos, fedora, and rhel distros
     + debian: includes debian and ubuntu distros
     + suse: includes the opensuse distro

   The most specific section takes priority. Example for Nova and Glance
   (NOTE: default is using the common value for redhat and suse families)

   The key used for the service name should always be the same name used for
   the source installation of the service.  The svc-map script will check for
   the source name against systemd and upstart and return that name if it
   exists instead of the mapped name.

    Example format for Nova::

      nova-api:
        default: openstack-nova-api
        debian: nova-api
      nova-cert:
        default: openstack-nova-cert
        debian:  nova-cert
      nova-compute:
        default: openstack-nova-compute
        debian: nova-compute
      nova-conductor:
        default: openstack-nova-conductor
        debian: nova-conductor
      nova-consoleauth:
        default: openstack-nova-console
        debian: nova-console


    Example format for Glance::

      glance-api:
        debian: glance-api
        default: openstack-glance-api
      glance-reg:
        debian: glance-reg
        default: openstack-glance-registry


    If the distro is of the debian family the combined services file would be::

        nova-cert: nova-cert
        nova-compute: nova-compute
        glance-api: glance-api
        nova-conductor: nova-conductor
        nova-api: nova-api
        glance-reg: glance-reg
        nova-consoleauth: nova-console


    If the distro is of the suse or redhat families the combined services file would be::

        nova-cert: openstack-nova-cert
        nova-compute: openstack-nova-compute
        glance-reg: openstack-glance-registry
        nova-conductor: openstack-nova-conductor
        glance-api: openstack-glance-api
        nova-consoleauth: openstack-nova-console
        nova-api: openstack-nova-api


   Example commands using this format::

       svc-map nova-compute

       Returns: openstack-nova-compute

       svc-map nova-compute

       Returns: openstack-nova-compute

       svc-map nova-compute

       Returns: nova-compute

 * This output can be used to filter what other tools actually install
   (install-services can be modified to use this for example)

 * If you pass more than one service argument, the result for each service
   is printed on its own line.

 * Individual svc-map files live within each element. For example
   if you have created an Apache element your svc-map YAML file
   should be created at elements/apache/svc-map.
