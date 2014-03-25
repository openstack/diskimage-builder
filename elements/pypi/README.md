Inject a PyPI mirror
====================

Use a custom PyPI mirror to build images. The default is to bind mount one from
~/.cache/image-create/pypi/mirror into the build environment. The element
temporarily overwrites /root/.pip.conf and .pydistutils.cfg to use it.

When online, the official pypi.python.org pypi index is supplied as an
extra-url, so uncached dependencies will still be available. When offline, only
the mirror is used - be warned that a stale mirror will cause build failures.
To disable the pypi.python.org index without using --offline (e.g. when working
behind a corporate firewall that prohibits pypi.python.org) set
DIB\_NO\_PYPI\_PIP to any non-empty value.

To use an arbitrary mirror set PYPI\_MIRROR\_URL=http[s]://somevalue/

Additional mirrors can be added by exporting PYPI\_MIRROR\_URL\_1=... etc. Only
the one mirror can be used by easy-install, but since wheels need to be in the
first mirror to be used, the last listed mirror is used as the pydistutils
index. NB: The sort order for these variables is a simple string sort - if
you have more than 9 additional mirrors, some care will be needed.

A typical use of this element is thus:
export PYPI\_MIRROR\_URL=http://site/pypi/Ubuntu-13.10
export PYPI\_MIRROR\_URL\_1=http://site/pypi/

[pypi-mirror](https://git.openstack.org/cgit/openstack-infra/pypi-mirror) can
be useful in making a partial PyPI mirror suitable for building images. For
instance:

 * sudo apt-get install  libxml2-dev libxslt-dev libmysqlclient-dev libpq-dev \
   libnspr4-dev pkg-config libsqlite3-dev libzmq-dev libffi-dev libldap2-dev \
   libsasl2-dev

 * pip install git+https://git.openstack.org/openstack-infra/pypi-mirror

 * cat << EOF > mirror.yaml
   cache-root: /home/USER/.cache/image-create/pypi/download

   mirrors:
    - name: openstack
      projects:
        - https://git.openstack.org/openstack/requirements
      output: /home/USER/.cache/image-create/pypi/mirror
   EOF

 * mkdir -p /home/USER/.cache/image-create/pypi/{download,mirror}

 * run-mirror -b remotes/origin/master --verbose -c mirror.yaml
   # This creates and updates the mirror.

If you have additional packages that are not identified in the global openstack
requirements project, you can include them:

 * pip install -d ~/.cache/image-create/pypi/download/pip/openstack \
   heat-cfntools distribute os-apply-config
   run-mirror -b remotes/origin/master --verbose -c mirror.yaml --no-download
