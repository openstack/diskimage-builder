The package-installs element allows for a declarative method of installing and
uninstalling packages for an image build. This is done by creating a
package-installs.yaml or package-installs.json file in the element directory.


example package-installs.yaml::

 libxml2:
 grub2:
   phase: pre-install.d
 networkmanager:
   uninstall: True

example package-installs.json::

    {
    "libxml2": null,
    "grub2": {"phase": "pre-install.d"},
    "networkmanager": {"uninstall": true}
    }


Setting phase or uninstall properties for a package overrides the following
default values::

    phase: install.d
    uninstall: False


DEPRECATED: Adding a file under your elements pre-install.d, install.d, or
post-install.d directories called package-installs-<element-name> will cause
the list of packages in that file to be installed at the beginning of the
respective phase.  If the package name in the file starts with a "-", then
that package will be removed at the end of the install.d phase.
