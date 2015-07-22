CI needs for image building
===========================

Eventually, if/when TripleO becomes an official OpenStack project, all CI for
it should be on OpenStack systems. Until then we still need CI.

Jenkins
-------

* Jenkins from jenkins apt repo.
* IRC notification service, notify-only on #triple on freenode, port 7000 ssl.
* Github OAuth plugin, permit all from tripleo organisation, and organisation
  members as service admins.
* Grant jenkins builders sudo [may want lxc containers or cloud instances for
  security isolation]
* Jobs to build:
 * base ubuntu VM.

        disk-image-create vm base -o base -a i386

 * ramdisk deploy image build

        ramdisk-image-create deploy
        
Copyright
=========

Copyright 2012, 2013 Hewlett-Packard Development Company, L.P.
Copyright (c) 2012 NTT DOCOMO, INC. 

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
