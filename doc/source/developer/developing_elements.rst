.. _developing-elements:

Developing Elements
===================

Conform to the following conventions:

* Use the environment for overridable defaults, prefixing environment variable
  names with ``DIB_``. For example:

  .. sourcecode:: sh

      DIB_MYDEFAULT=${DIB_MYDEFAULT:-default}

  If you do not use the ``DIB`` prefix you may find that your overrides are
  discarded as the build environment is sanitised.

* Consider that your element co-exists with many others and try to guard
  against undefined behaviours. Some examples:

  * Two elements use the source-repositories element, but use the same filename
    for the source-repositories config file. Files such as these (and indeed the
    scripts in the various .d directories :ref:`listed below
    <phase-subdirectories>`) should be named such that they are unique. If they
    are not unique, when the combined tree is created by disk-image-builder for
    injecting into the build environment, one of the files will be overwritten.

  * Two elements copy different scripts into ``/usr/local/bin`` with the same
    name.  If they both use ``set -e`` and ``cp -n`` then the conflict will be
    caught and cause the build to fail.

* If your element mounts anything into the image build tree (``$TMP_BUILD_DIR``)
  then it will be automatically unmounted when the build tree is unmounted - and
  not remounted into the filesystem image - if the mount point is needed again,
  your element will need to remount it at that point.

* If caching is required, elements should use a location under
  ``$DIB_IMAGE_CACHE``.

* Elements should allow for remote data to be cached. When ``$DIB_OFFLINE`` is
  set, this cached data should be used if possible.
  See the :ref:`dev-global-image-build-variables` section of this document for
  more information.

* Elements in the upstream diskimage-builder elements should not create
  executables which run before 10- or after 90- in any of the phases if
  possible. This is to give downstream elements the ability to easily make
  executables which run after our upstream ones.

.. _phase-subdirectories:

Phase Subdirectories
^^^^^^^^^^^^^^^^^^^^

Make as many of the following subdirectories as you need, depending on what
part of the process you need to customise. The subdirectories are executed in
the order given here. Scripts within the subdirectories should be named with a
two-digit numeric prefix, and are executed in numeric order.

Only files which are marked executable (+x) will be run, so other files can be
stored in these directories if needed. As a convention, we try to only store
executable scripts in the phase subdirectories and store data files elsewhere in
the element.

The phases are:

#. ``root.d``
#. ``extra-data.d``
#. ``pre-install.d``
#. ``install.d``
#. ``post-install.d``
#. ``block-device.d``
#. ``finalise.d``
#. ``cleanup.d``

``root.d``
  Create or adapt the initial root filesystem content. This is where
  alternative distribution support is added, or customisations such as
  building on an existing image.

  Only one element can use this at a time unless particular care is taken not
  to blindly overwrite but instead to adapt the context extracted by other
  elements.

  * runs: **outside chroot**
  * inputs:

    * ``$ARCH=i386|amd64|armhf``
    * ``$TARGET_ROOT=/path/to/target/workarea``

``extra-data.d``
  Pull in extra data from the host environment that hooks may
  need during image creation. This should copy any data (such as SSH keys,
  http proxy settings and the like) somewhere under ``$TMP_HOOKS_PATH``.

  * runs: **outside chroot**
  * inputs: ``$TMP_HOOKS_PATH``
  * outputs: None

``pre-install.d``
  Run code in the chroot before customisation or packages are installed. A good
  place to add apt repositories.

  * runs: **in chroot**

``install.d``
  Runs after ``pre-install.d`` in the chroot. This is a good place to
  install packages, chain into configuration management tools or do other image
  specific operations.

  * runs: **in chroot**

``post-install.d``
  Run code in the chroot. This is a good place to perform tasks you want to
  handle after the OS/application install but before the first boot of the
  image.  Some examples of use would be:

    Run ``chkconfig`` to disable unneeded services

    Clean the cache left by the package manager to reduce the size of the image.

  * runs: **in chroot**

``block-device.d``
  Customise the block device that the image will be made on (for example to
  make partitions). Runs after the target tree has been fully populated but
  before the ``cleanup.d`` phase runs.

  * runs: **outside chroot**
  * inputs:

    * ``$IMAGE_BLOCK_DEVICE={path}``
    * ``$TARGET_ROOT={path}``

  * outputs: ``$IMAGE_BLOCK_DEVICE={path}``

``finalise.d``
  Perform final tuning of the root filesystem. Runs in a chroot after the root
  filesystem content has been copied into the mounted filesystem: this is an
  appropriate place to reset SELinux metadata, install grub bootloaders and so
  on.

  Because this happens inside the final image, it is important to limit
  operations here to only those necessary to affect the filesystem metadata and
  image itself. For most operations, ``post-install.d`` is preferred.

  * runs: **in chroot** 

``cleanup.d``
  Perform cleanup of the root filesystem content. For instance, temporary
  settings to use the image build environment HTTP proxy are removed here in
  the dpkg element.

  * runs: outside chroot
  * inputs:

    * ``$ARCH=i386|amd64|armhf``
    * ``$TARGET_ROOT=/path/to/target/workarea``


Other Subdirectories
^^^^^^^^^^^^^^^^^^^^

Elements may have other subdirectories that are processed by specific elements
rather than the diskimage-builder tools themselves.

One example of this is the ``bin`` directory.  The `rpm-distro`,
:doc:`../elements/dpkg/README` and :doc:`../elements/opensuse/README` elements
install all files found in the ``bin`` directory into ``/usr/local/bin`` within
the image as executable files.

Environment Variables
^^^^^^^^^^^^^^^^^^^^^

To set environment variables for other hooks, add a file to your element
``environment.d``.

This directory contains bash script snippets that are sourced before running
scripts in each phase.

DIB exposes an internal ``$IMAGE_ELEMENT`` variable which provides elements
access to the full set of elements that are included in the image build. This
can be used to process local in-element files across all the elements
(``pkg-map`` for example).

Dependencies
^^^^^^^^^^^^

Each element can use the following files to define or affect dependencies:

``element-deps``
  A plain text, newline separated list of elements which will be added to the
  list of elements built into the image at image creation time.

``element-provides``
  A plain text, newline separated list of elements which are provided by this
  element.  These elements will be excluded from elements built into the image
  at image creation time.

  For example if element A depends on element B and element C includes element B
  in its ``element-provides`` file and A and C are included when building an
  image, then B is not used.

Operating system elements
^^^^^^^^^^^^^^^^^^^^^^^^^

Some elements define the base structure for an operating system -- for example,
the ``opensuse`` element builds a base openSUSE system. Such elements have
more requirements than the other elements:

* they must have ``operating-system`` in their element-provides, so this
  indicates they are an "operating system".

* they must export the ``DISTRO_NAME`` environment variable with the name
  of the distribution built, using an environment.d script. For example,
  the ``opensuse`` element exports ``DISTRO_NAME=opensuse``.

Ramdisk Elements
^^^^^^^^^^^^^^^^

Ramdisk elements support the following files in their element directories:

``binary-deps.d``
  Text files listing executables required to be fed into the ramdisk. These
  need to be present in ``$PATH`` in the build chroot (i.e. need to be installed
  by your elements as described above).

``init.d``
  POSIX shell script fragments that will be appended to the default script
  executed as the ramdisk is booted (``/init``).

``ramdisk-install.d``
  Called to copy files into the ramdisk. The variable ``$TMP_MOUNT_PATH`` points
  to the root of the tree that will be packed into the ramdisk.

``udev.d``
  ``udev`` rules files that will be copied into the ramdisk.

Element coding standard
^^^^^^^^^^^^^^^^^^^^^^^

- lines should not include trailing whitespace.
- there should be no hard tabs in the file.
- indents are 4 spaces, and all indentation should be some multiple of
  them.
- `do` and `then` keywords should be on the same line as the if, while or
  for conditions.

.. _dev-global-image-build-variables:

Global image-build variables
----------------------------

``DIB_OFFLINE``
  This is always set. When not empty, any operations that perform remote data
  access should avoid it if possible. If not possible the operation should still
  be attempted as the user may have an external cache able to keep the operation
  functional.

``DIB_IMAGE_ROOT_FS_UUID``
  This contains the UUID of the root filesystem, when diskimage-builder is
  building a disk image. This works only for ext filesystems.

``DIB_IMAGE_CACHE``
  Path to where cached inputs to the build process are stored. Defaults to
  ``~/.cache/image_create``.

Structure of an element
-----------------------

The above-mentioned global content can be further broken down in a way that
encourages composition of elements and reusability of their components. One
possible approach to this would be to label elements as either a "driver",
"service", or "config" element. Below are some examples.

- Driver-specific elements should only contain the necessary bits for that
  driver::

      elements/
         driver-mellanox/
            init           - modprobe line
            install.d/
               10-mlx      - package installation

- An element that installs and configures Nova might be a bit more complex,
  containing several scripts across several phases::

      elements/
         service-nova/
            source-repository-nova - register a source repository
            pre-install.d/
               50-my-ppa           - add a PPA
            install.d/
               10-user             - common Nova user accts
               50-my-pack          - install packages from my PPA
               60-nova             - install nova and some dependencies

- In the general case, configuration should probably be handled either by the
  meta-data service (eg, o-r-c) or via normal CM tools
  (eg, salt). That being said, it may occasionally be desirable to create a
  set of elements which express a distinct configuration of the same software
  components.

In this way, depending on the hardware and in which availability zone it is
to be deployed, an image would be composed of:

 * zero or more driver-elements
 * one or more service-elements
 * zero or more config-elements

It should be noted that this is merely a naming convention to assist in
managing elements. Diskimage-builder is not, and should not be, functionally
dependent upon specific element names.

diskimage-builder has the ability to retrieve source code for an element and
place it into a directory on the target image during the extra-data phase. The
default location/branch can then be overridden by the process running
diskimage-builder, making it possible to use the same element to track more
then one branch of a git repository or to get source for a local cache. See
:doc:`../elements/source-repositories/README` for more information.

Debugging elements
------------------

The build-time environment and command line arguments are captured by the
:doc:`../elements/base/README` element and written to ``/etc/dib_environment``
and ``/etc/dib_arguments`` inside the image.

Export ``break`` to drop to a shell during the image build. Break points can be
set either before or after any of the hook points by exporting
"break=[before|after]-hook-name". Multiple break points can be specified as a
comma-delimited string. Some examples:

* ``break=before-block-device-size`` will break before the block device size
  hooks are called.

* ``break=before-pre-install`` will break before the pre-install hooks.

* ``break=after-error`` will break after an error during an in target hookpoint.

Images are built such that the Linux kernel is instructed not to switch into
graphical consoles (i.e. it will not activate KMS). This maximises
compatibility with remote console interception hardware, such as HP's iLO.
However, you will typically only see kernel messages on the console - init
daemons (e.g. upstart) will usually be instructed to output to a serial
console so nova's console-log command can function. There is an element in the
tripleo-image-elements repository called "remove-serial-console" which will
force all boot messages to appear on the main console.

Ramdisk images can be debugged at run-time by passing ``troubleshoot`` as a
kernel command line argument, or by pressing "t" when an error is reached. This
will spawn a shell on the console (this can be extremely useful when network
interfaces or disks are not detected correctly).

Testing Elements
----------------

An element can have functional tests encapsulated inside the element itself. The
tests can be written either as shell or python unit tests.

shell
"""""

In order to create a test case, follow these steps:

* Create a directory called ``test-elements`` inside your element.

* Inside the test-elements directory, create a directory with the name of your
  test case. The test case directory should have the same structure as an
  element. For example::

    elements/apt-sources/test-elements/test-case-1

* Assert state during each of the element build phases you would like to test.
  You can exit 1 to indicate a failure.

* To exit early and indicate a success, touch a file
  ``/tmp/dib-test-should-fail`` in the image chroot, then exit 1.

Tests are run with ``tools/run_functests.sh``.  Running
``run_functests.sh -l`` will show available tests (the example above
would be called ``apt-sources/test-case-1``, for example).  Specify
your test (or a series of tests as separate arguments) on the command
line to run it.  If it should not be run as part of the default CI
run, you can submit a change with it added to ``DEFAULT_SKIP_TESTS``
in that file.

python
""""""

To run functional tests locally, install and start docker, then use
the following tox command::

    tox -efunc

Note that running functional tests requires *sudo* rights, thus you may be
asked for your password.

To run functional tests for one element, append its name to the command::

    tox -efunc ironic-agent

Additionally, elements can be tested using python unittests. To create a
a python test:

* Create a directory called ``tests`` in the element directory.

* Create an empty file called ``__init__.py`` to make it into a python
  package.

* Create your test files as ``test\whatever.py``, using regular python test
  code.

To run all the tests use testr - ``testr run``. To run just some tests provide
one or more regex filters - tests matching any of them are run -
``testr run apt-proxy``.

Third party elements
--------------------

Additional elements can be incorporated by setting ``ELEMENTS_PATH``, for
example if one were building tripleo-images, the variable would be set like:

  .. sourcecode:: sh

      export ELEMENTS_PATH=tripleo-image-elements/elements
      disk-image-create rhel7 cinder-api
