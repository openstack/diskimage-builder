Install Types
=============

Install types permit elements to be installed from different sources, such as
git repositories, distribution packages, or pip. The default install type
is 'source' but it can be modified on the disk-image-create command line
via the --install-type option. For example you can set:

    --install-type=package

to enable package installs by default. Alternately, you can also
set DIB\_DEFAULT\_INSTALLTYPE.

Many elements expose different install types. The different implementations
live under `<install-dir-prefix>-<install-type>-install` directories under an
element's install.d. The base element enables the chosen install type by
symlinking the correct hook scripts under install.d directly.
`<install-dir-prefix>` can be a string of alphanumeric and '-' characters, but
typically corresponds to the element name.

For example, the nova element would provide:

    nova/install.d/nova-package-install/74-nova
    nova/install.d/nova-source-install/74-nova

The following symlink would be created for the package install type:

    install.d/74-nova -> nova-package-install/74-nova

Or, for the source install type:

    install.d/74-nova -> nova-source-install/74-nova

All other scripts that exist under install.d for an element will be executed as
normal. This allows common install code to live in a script under install.d.

To set the install type for an element define an environment variable
`DIB_INSTALLTYPE_<install_dir_prefx>`. Note that if you used `-` characters in
your install directory prefix, those need to be replaced with `_` in the
environment variable.

For example, to enable the package install type for the set of nova elements
that use `nova` as the install type prefix, define the following:

    export DIB_INSTALLTYPE_nova=package
