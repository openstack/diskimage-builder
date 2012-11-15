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

        disk-image-create base mysql haproxy-mysql haproxy-api local-boot \
        rabbitmq -o baremetal-spof

 * baremetal demo node build (archive the resulting image).

        disk-image-create base vm glance nova-bm swift cinder quantum \
        -o bootstrap-prod

 * ramdisk deploy image buil

        ramdisk-image-create deploy
        
 * Tempest w/baremetal using libvirt networking as the power API.
   take a bootstrap baremetal devstack from above, N VM 'bare metal' nodes,
   and run tempest in that environment.

Copyright
=========

Copyright 2012 Hewlett-Packard Development Company, L.P.
Copyright (c) 2012 NTT DOCOMO, INC. 

All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
