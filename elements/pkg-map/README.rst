=======
pkg-map
=======
Map package names to distro specific packages.

Provides the following:

 * bin/pkg-map::

    usage: pkg-map [-h] [--element ELEMENT] [--distro DISTRO]

    Translate package name to distro specific name.

    optional arguments:
      -h, --help         show this help message and exit
      --element ELEMENT  The element (namespace) to use for translation.
      --distro DISTRO    The distro name to use for translation. Defaults to
                         DISTRO_NAME

 * Any element may create its own pkg-map JSON config file using
   the one of 3 sections for the distro/family/ and or default.
   The family is set automatically within pkg-map based on
   the supplied distro name. Families include:

     + redhat: includes centos, fedora, and rhel distros
     + debian: includes debian and ubuntu distros
     + suse: includes the opensuse distro

   The most specific section takes priority.
   An empty package list can be provided.
   Example for Nova and Glance (NOTE: using fictitious package names
   for Fedora and package mapping for suse family to provide a good
   example!)

   Example format::

    {
      "distro": {
        "fedora": {
          "nova_package": "openstack-compute",
          "glance_package": "openstack-image"
        }
      },
      "family": {
        "redhat": {
          "nova_package": "openstack-nova",
          "glance_package": "openstack-glance"
        },
        "suse": {
          "nova_package": ""
        }
      },
      "default": {
        "nova_package": "nova",
        "glance_package": "glance"
      }
    }

   Example commands using this format:

   pkg-map --element nova-compute --distro fedora nova_package

   Returns: openstack-compute

   pkg-map --element nova-compute --distro rhel nova_package

   Returns: openstack-nova

   pkg-map --element nova-compute --distro ubuntu nova_package

   Returns: nova

   pkg-map --element nova-compute --distro opensuse nova_package

   Returns:

 * This output can be used to filter what other tools actually install
   (install-packages can be modified to use this for example)

 * Individual pkg-map files live within each element. For example
   if you are created an Apache element your pkg-map JSON file
   should be created at elements/apache/pkg-map.
