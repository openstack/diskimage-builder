Image building tools for OpenStack
==================================

These tools are the components of TripleO
(https://wiki.openstack.org/wiki/TripleO) that are responsible for
building disk images.

This repository has the core functionality for building disk images, file
system images and ramdisk images for use with OpenStack (both virtual and bare
metal). The core functionality includes the various operating system specific
modules for disk/filesystem images, and deployment and hardware inventory
ramdisks.

The TripleO project also develops elements that can be used to deploy
OpenStack itself. These live in the TripleO elements repository
(https://git.openstack.org/cgit/openstack/tripleo-image-elements).

Online documentation:

* http://docs.openstack.org/developer/diskimage-builder/

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
