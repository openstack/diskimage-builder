Tested Distributions
--------------------

``diskimage-builder`` can create many different types of targets
composed of many different elements.  For any release, the project
considers the elements tested by the OpenDev gate
continuous-integration jobs as stable.

Practically, this means a change can not commit unless it has
successfully built the elements described below under test.

Build Host
==========

The build-host is the platform used to create images.  Unfortunately
there is no concise answer as to the support status of all possible
build-hosts.  ``diskimage-builder`` has a complex relationship with
the build-host depending on which target elements are being built.

Image-based elements take an upstream ``.qcow2`` image, extract and
customise it.  Since ``diskimage-builder`` chroots into an
already-complete environment, these elements generally work on any
build-host, but there are complexities; for example some images ship
an XFS-filesystem with options that some stable-distribution
build-hosts can not read (and hence the build-host can not mount and
extract the image).

As another example, the ``-minimal`` elements run tools such as
``yum``, ``dnf``, ``apt`` on the build-host to create an initial
``chroot`` environment.  Thus some combinations will not work; for
example ``fedora-minimal`` for the latest versions may require a RPM
that is not packaged on current stable versions of Ubuntu.  Some
versions of Ubuntu ship a ``debootstrap`` that has bugs preventing
building other distributions, etc.

Finally the ``containerfile`` elements use ``podman`` to extract a
container-image and then customise that.  Distributions vary in their
podman version and various bugs related to this.

The images used by the OpenDev's `Zuul <https://zuul-ci.org>`__ system
are built by `Nodepool <https://zuul-ci.org/docs/nodepool/>`__.  Thus
the simplest way to have the most supported build-host environment is
to use ``diskimage-buidler`` installed in the `nodepool-builder
container image
<https://quay.io/repository/zuul-ci/nodepool?tab=tags&tag=latest>`__.
You can run ``disk-image-create`` directly from this container, e.g.

::

       docker run --rm --privileged --network host \
            --env DIB_SHOW_IMAGE_USAGE=1 \
            --env TMPDIR=/opt/dib_tmp \
            -v nested_var_lib_containers:/var/lib/containers \
            -v /var/run/dib_output:/var/run/dib_output \
            -v /opt/dib_tmp:/opt/dib_tmp \
            quay.io/zuul-ci/nodepool-builder \
            disk-image-create -x -t qcow2 \
            --no-tmpfs \
            -o /var/run/dib_output/image -n <element(s)>

The platform this container image is built upon is by extension the
most-supported build host.  Inspecting the `Dockerfile
<https://opendev.org/zuul/nodepool/src/branch/master/Dockerfile>`__ is
a good way to start building customised build-host environments.  This
is currently based on Debian Bullsye.

Other distributions are not tested as build-hosts in the
``diskimage-builder`` gate.

Testing and Targets
===================

The stable targets are those that are tested; as noted no change can
commit which would break this testing.

There are two main testing paths:

* end-to-end tests build an image, import it to an OpenStack
  environment, boot it and confirm basic operation.  These tests use
  the ``nodepool-builder`` container environment to build the image to
  be tested.
* functional tests build a complete output image.  They do not perform
  boot tests.  These tests run on Debian Bullseye.

The canonical list of tests and the elements they build for any releae
is kept in `.zuul.yaml/jobs.yaml
<https://opendev.org/openstack/diskimage-builder/src/branch/master/.zuul.d/jobs.yaml>`__.
If this document differs to the defined tests, the Zuul configuration
is correct.

As of Feburary 2022, the default end-to-end testing covers the
following elements on x86-64

* ``centos-minimal``: 8-stream and 9-stream
* ``fedora-containerfile``: the latest Fedora.
* ``ubuntu-minimal``: Ubuntu Xenial, Bionic and Focal
* ``opensuse-minimal``: Leap 15.3 and Tumbleweed (non-voting)
* ``gentoo``: (non-voting)
* ``debian-minimal``: Bullseye
* ``rocky-container``: Rocky Linux 8

We run functional (build-only) tests on the following elements and
versions:

* ``containerfile``: Ubuntu Focal
* ``openeuler-minimal``: 22.03-LTS
* ``centos`` : (image-based build) 8-stream and 9-stream
* ``fedora`` : (image-based build) latest
* ``opensuse`` : 15.5
* ``ubuntu`` : Bionic and Focal

For ARM64, we also run functional tests on

* ``ubuntu-minimal`` : Bionic and Focal
* ``debian-minimal`` : Bullseye
* ``centos-minimal`` : 8-stream and 9-stream
* ``openeuler-minimal``: 22.03-LTS

For additional details, see the ``README`` file of the relevant
elements.

``diskimage-builder`` is used in a range of other projects that do
their own testing, separate to the ``diskimage-buidler`` CI gate
testing.  These have different combinations of host/target elements
they keep stable.  Updates to this document are welcome.
