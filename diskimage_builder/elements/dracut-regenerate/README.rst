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
