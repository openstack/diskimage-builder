CI needs for image building
===========================

Eventually, if/when TripleO becomes an official Openstack project, all CI for
it should be on Openstack systems. Until then we still need CI.

Jenkins
-------

* Jenkins from jenkins apt repo.
* IRC notification service, notify-only on #triple on freenode, port 7000 ssl.
* Github OAuth plugin, permit all from tripleo organisation, and organisation
  members as service admins.
* Grant jenkin builders sudo [may want lxc containers or cloud instances for
  security isolation]
* Jobs to build:
 * bootstrap VM from-scratch (archive bootstrap.qcow2).

        disk-image-create vm devstack -o bootstrap -a i386

 * devstack nova-bm execution (archive the resulting image).
   Chained off of the bootstrap vm build

        ssh into the node, run demo/scripts/demo

 * bootstrap VM via image-build chain (archive bm-cloud.qcow2).

        disk-image-create vm glance nova-bm swift mysql haproxy-api \
        haproxy-mysql cinder quantum rabbitmq -o bootstrap-prod

 * baremetal SPOF node build (archive the resulting image).

        disk-image-create mysql haproxy-mysql haproxy-api local-boot \
        rabbitmq -o baremetal-spof

 * baremetal demo node build (archive the resulting image).

        disk-image-create vm glance nova-bm swift cinder quantum \
        -o bootstrap-prod

 * ramdisk deploy image buil

        ramdisk-image-create deploy
        
 * Tempest w/baremetal using libvirt networking as the power API.
   take a bootstrap baremetal devstack from above, N VM 'bare metal' nodes,
   and run tempest in that environment.
