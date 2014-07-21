The package-installs element allows for a declarative method of installing and
uninstalling packages for an image build. Adding a file under your elements
pre-install.d, install.d, or post-install.d directories called
package-installs-<element-name> will cause the list of packages in that file to
be installed at the beginning of the respective phase.

If the package name in the file starts with a "-", then that package will be
removed at the end of the install.d phase.
