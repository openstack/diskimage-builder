================
package-installs
================

The package-installs element allows for a declarative method of installing and
uninstalling packages for an image build. This is done by creating a
package-installs.yaml or package-installs.json file in the element directory.

In order to work on Gentoo hosts you will need to manually install
`dev-python/pyyaml`.

example ``package-installs.yaml``

.. code-block:: YAML

  libxml2:
  grub2:
    phase: pre-install.d
  networkmanager:
    uninstall: True
  os-collect-config:
    installtype: source
  linux-image-amd64:
    arch: amd64
  dmidecode:
    not-arch: ppc64, ppc64le
  lshw:
    arch: ppc64, ppc64le
  python-dev:
    dib_python_version: 2
  python3-dev:
    dib_python_version: 3
  package-a:
    when: DIB_USE_PACKAGE_A = 1
  package-b:
    when: DIB_USE_PACKAGE_A != 1

example package-installs.json

.. code-block:: json

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
    dib_python_version: (2 or 3 depending on DIB_PYTHON_VERSION, see dib-python)

Setting the installtype property causes the package only to be installed if
the specified installtype would be used for the element. See the
diskimage-builder docs for more information on installtypes.

The ``arch`` property is a comma-separated list of architectures to
install for.  The ``not-arch`` is a comma-separated list of
architectures the package should be excluded from.  Either ``arch`` or
``not-arch`` can be given for one package - not both.  See
documentation about the ARCH variable for more information.

The ``when`` property is a simple ``=`` or ``!=`` match on a value in
an environment variable.  If the given environment variable matches
the operation and value, the package is installed.  If the variable is
not available in the environment, an exception is raised (thus
defaults will likely need to be provided in ``environment.d`` files or
similar for flags used here).  For example, to install an extra
package when a feature is enabled::

  package:
    when: DIB_FEATURE_FLAG=1

To install ``package`` when ``DIB_FEATURE_FLAG=0`` but
``other_package`` when ``DIB_FEATURE_FLAG=1`` (i.e. toggle between two
packages), you can use something like::

  package:
    when: DIB_FEATURE_FLAG=0
  other_package:
    when: DIB_FEATURE_FLAG!=0

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
