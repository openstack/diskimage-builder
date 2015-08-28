Image building tools for OpenStack
==================================

``diskimage-builder`` is a flexible suite of components for building a
wide-range of disk images, filesystem images and ramdisk images for
use with OpenStack.

This repository has the core functionality for building such images,
both virtual and bare metal.  Images are composed using `elements`;
while fundamental elements are provided here, individual projects have
the flexibility to customise the image build with their own elements.

For example::

  $ DIB_RELEASE=trusty disk-image-create -o ubuntu-trusty.qcow2 vm ubuntu

will create a bootable Ubuntu Trusty based ``qcow2`` image.

``diskimage-builder`` is useful to anyone looking to produce
customised images for deployment into clouds.  These tools are the
components of `TripleO <https://wiki.openstack.org/wiki/TripleO>`__
that are responsible for building disk images.  They are also used
extensively to build images for testing OpenStack itself, particularly
with `nodepool
<http://docs.openstack.org/infra/system-config/nodepool.html>`__.
Platforms supported include Ubuntu, CentOS, RHEL and Fedora.

Full documentation, the source of which is in ``doc/source/``, is
published at:

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
