================
package-installs
================

The package-installs element allows for a declarative method of installing and
uninstalling packages for an image build. This is done by creating a
package-installs.yaml or package-installs.json file in the element directory.

In order to work on Gentoo hosts you will need to manually install
`dev-python/pyyaml`.

example package-installs.yaml::

 libxml2:
 grub2:
   phase: pre-install.d
 networkmanager:
   uninstall: True
 os-collect-config:
   installtype: source
 linux-image-amd64:
   arch: amd64

example package-installs.json::

    {
    "libxml2": null,
    "grub2": {"phase": "pre-install.d"},
    "networkmanager": {"uninstall": true}
    "os-collect-config": {"installtype": "source"}
    }


Setting phase, uninstall, or installtype properties for a package overrides
the following default values::

    phase: install.d
    uninstall: False
    installtype: * (Install package for all installtypes)
    arch: * (Install package for all architectures)

Setting the installtype property causes the package only to be installed if
the specified installtype would be used for the element. See the
diskimage-builder docs for more information on installtypes.

Setting the arch property causes the package only to be installed for the
specified target architecture. See documentation about the ARCH variable
for more information.

DEPRECATED: Adding a file under your elements pre-install.d, install.d, or
post-install.d directories called package-installs-<element-name> will cause
the list of packages in that file to be installed at the beginning of the
respective phase.  If the package name in the file starts with a "-", then
that package will be removed at the end of the install.d phase.

Using post-install.d for cleanup
================================

Package removal is done in post-install.d at level 95.  If you a
running cleanup functions before this, you need to be careful not
to clean out any temporary files relied upon by this element.
For this reason, generally post-install cleanup functions should
occupy the higher levels between 96 and 99.
