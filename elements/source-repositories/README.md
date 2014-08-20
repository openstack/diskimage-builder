With this element other elements can register their installation source by
placing their details in the file source-repository-\*. An example
of an element "custom-element" that wants to retrieve the ironic source
from git and pbr from a tarball would be

*File : elements/custom-element/source-repository-ironic*

    #<name> <type> <destination> <location> [<ref>]
    # <ref> defaults to master if not specified
    ironic git /usr/local/ironic git://git.openstack.org/openstack/ironic.git

*File : elements/custom-element/source-repository-pbr*

    # <ref> is defined as "*" by default, although this behavior is deprecated.
    # A value of "." extracts the entire contents of the tarball.
    # A value of "*" extracts the contents within all its subdirectories.
    # A value of a subdirectory path may be used to extract only its contents.
    # A value of a specific file path within the archive is not supported.
    pbr tar /usr/local/pbr http://tarballs.openstack.org/pbr/pbr-master.tar.gz .

diskimage-builder will then retrieve the sources specified and place them
at the directory \<destination\>

A number of environment variables can be set by the process calling
diskimage-builder which can change the details registered by the element, these are

    DIB_REPOTYPE_<name>     : change the registered type
    DIB_REPOLOCATION_<name> : change the registered location
    DIB_REPOREF_<name>      : change the registered reference

For example if you would like diskimage-builder to get ironic from a local
mirror you could set DIB_REPOLOCATION_ironic=git://localgitserver/ironic.git

*As you can see above, the \<name\> of the repo is used in several bash
variables. In order to make this syntactically feasible, any characters not in
the set \[A-Za-z0-9_\] will be converted to \_*

*For instance, a repository named "diskimage-builder" would set a variable called
"DIB_REPOTYPE_diskimage_builder"*


Alternatively if you would like to use the keystone element and build an image with
keystone from a stable branch then you would set DIB_REPOREF_keystone=stable/grizzly

If you wish to build an image using code from a gerrit review, you can set 
DIB_REPOLOCATION_<name> and DIB_REPOREF_<name> to the values given by gerrit in the
fetch/pull section of a review. For example:

    DIB_REPOLOCATION_nova=https://review.openstack.org/openstack/nova
    DIB_REPOREF_nova=refs/changes/72/61972/8

Additionally, the lines in the source-repository scripts are eval'd, so they
may contain environment variables.

Git sources will be cloned to \<destination\>

Tarballs will be extracted to \<destination\>.

The package type indicates the element should install from packages onto the
root filesystem of the image build during the install.d phase.

Git and Tarballs are treated as source installs.  If the element provides an
<element-name>-source-install directory under it's install.d hook directory,
symlinks to the scripts in that directory will be created under install.d for
the image build.  Alternatively for the package install type, if the element
provides an <element-name>-package-install directory, symlinks will be created
for those scripts instead.

For example, the nova element would provide:

    nova/install.d/nova-package-install/74-nova
    nova/install.d/nova-source-install/74-nova

source-repositories will create the following symlink for the package install
type:

    install.d/74-nova -> nova-package-install/74-nova

Or, for the source install type:

    install.d/74-nova -> nova-source-install/74-nova

All other scripts that exist under install.d for an element will be executed as
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

The base url for all git repositories can be set by use of:

    DIB_GITREPOBASE

So setting DIB\_GITREPOBASE=https://github.com/ when the repo location is set
to http://git.openstack.org/openstack/nova.git will result in use of the
https://github.com/openstack/nova.git repository.
