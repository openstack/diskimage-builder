===================
source-repositories
===================
With this element other elements can register their installation source by
placing their details in the file ``source-repository-*``.

source-repository-* file format
-------------------------------

The plain text file format is space separated and has four mandatory fields
optionally followed by fields which are type dependent::

  <name> <type> <destination> <location> [<ref>]

``name``
  Identifier for the source repository. Should match the file suffix.

``type``
  Format of the source. Either ``git``, ``tar``, ``package`` or ``file``.

``destination``
  Base path to place sources.

``location``
  Resource to fetch sources from. For ``git`` the location is cloned. For
  ``tar`` it is extracted.

``ref`` (optional). Meaning depends on the ``type``:
  ``file``: unused/ignored.

  ``git``: a git reference to fetch. A value of "``*``" prunes and fetches all
  heads and tags. Defaults to ``master`` if not specified.

  ``tar``:
    | "``.``" extracts the entire contents of the tarball.
    | "``*``" extracts the contents within all its subdirectories.
    | A subdirectory path may be used to extract only its contents.
    | A specific file path within the archive is **not supported**.

The lines in the source-repository scripts are eval'd, so they may contain
environment variables.

The ``package`` type indicates the element should install from packages onto
the root filesystem of the image build during the ``install.d`` phase.  If the
element provides an <element-name>-package-install directory, symlinks will be
created for those scripts instead.

``git`` and ``tar`` are treated as source installs.  If the element provides an
<element-name>-source-install directory under it's ``install.d`` hook directory,
symlinks to the scripts in that directory will be created under ``install.d`` for
the image build.

For example, the nova element would provide::

    nova/install.d/nova-package-install/74-nova
    nova/install.d/nova-source-install/74-nova

source-repositories will create the following symlink for the package install
type::

    install.d/74-nova -> nova-package-install/74-nova

Or, for the source install type::

    install.d/74-nova -> nova-source-install/74-nova

All other scripts that exist under ``install.d`` for an element will be executed as
normal. This allows common install code to live in a script outside of
<element-name>-package-install or <element-name>-source-install.

If multiple elements register a source location with the same <destination>
then source-repositories will exit with an error. Care should therefore be taken
to only use elements together that download source to different locations.

The repository paths built into the image are stored in
etc/dib-source-repositories, one repository per line. This permits later review
of the repositories (by users or by other elements).

The repository names and types are written to an environment.d hook script at
01-source-repositories-environment. This allows later hook scripts during the
install.d phase to know which install type to use for the element.


An example of an element "custom-element" that wants to retrieve the ironic
source from git and pbr from a tarball would be:

*Element file: elements/custom-element/source-repository-ironic*::

    ironic git /usr/local/ironic git://git.openstack.org/openstack/ironic.git

*File : elements/custom-element/source-repository-pbr*::

    pbr tar /usr/local/pbr http://tarballs.openstack.org/pbr/pbr-master.tar.gz .

diskimage-builder will then retrieve the sources specified and place them
at the directory ``<destination>``.


Override per source
-------------------

A number of environment variables can be set by the process calling
diskimage-builder which can change the details registered by the element, these
are:

    ``DIB_REPOTYPE_<name>``     : change the registered type

    ``DIB_REPOLOCATION_<name>`` : change the registered location

    ``DIB_REPOREF_<name>``      : change the registered reference

For example if you would like diskimage-builder to get ironic from a local
mirror you would override the ``<location>`` field and could set:

.. sourcecode:: sh

    DIB_REPOLOCATION_ironic=git://localgitserver/ironic.git

*As you can see above, the \<name\> of the repo is used in several bash
variables. In order to make this syntactically feasible, any characters not in
the set \[A-Za-z0-9_\] will be converted to \_*

*For instance, a repository named "diskimage-builder" would set a variable called
"DIB_REPOTYPE_diskimage_builder"*


Alternatively if you would like to use the keystone element and build an image with
keystone from a stable branch *stable/grizzly* then you would set:

.. sourcecode:: sh

    DIB_REPOREF_keystone=stable/grizzly

If you wish to build an image using code from a Gerrit review, you can set
``DIB_REPOLOCATION_<name>`` and ``DIB_REPOREF_<name>`` to the values given by
Gerrit in the fetch/pull section of a review. For example, setting up Nova with
change 61972 at patchset 8:

.. sourcecode:: sh

    DIB_REPOLOCATION_nova=https://review.openstack.org/openstack/nova
    DIB_REPOREF_nova=refs/changes/72/61972/8


Alternate behaviors
-------------------

Override git remote
^^^^^^^^^^^^^^^^^^^

The base url for all git repositories can be set by use of:

    ``DIB_GITREPOBASE``

So setting ``DIB_GITREPOBASE=https://github.com/`` when the repo location is
set to http://git.openstack.org/openstack/nova.git will result in use of the
https://github.com/openstack/nova.git repository instead.

Disable external fetches
^^^^^^^^^^^^^^^^^^^^^^^^

When doing image builds in environments where external resources are not allowed,
it is possible to disable fetching of all source repositories by including an
element in the image that sets ``NO_SOURCE_REPOSITORIES=1`` in an
``environment.d`` script.
