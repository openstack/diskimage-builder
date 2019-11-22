=================
dracut-regenerate
=================
Adds the possibility of regenerating dracut on image build time, giving the
possibility to load extra modules.
It relies on the ``DIB_DRACUT_ENABLED_MODULES`` setting, that will accept
a yaml blob with the following format::

  - name: <module1>
    packages:
      - <package1>
      - <package2>
  - name: <module2>
    packages:
      - <package3>
      - <package4>

By default, this element will bring lvm and crypt modules.

Also adds the ability to copy specific files into /etc/dracut.conf.d directory
to allow any dracut settings to be configured. To achieve that the files to be
copied need to be placed inside an specific dracut.d directory of the element.
