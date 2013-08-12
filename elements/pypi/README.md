Inject a PyPI mirror
====================

Bind mounts a PyPI mirror from ~/.cache/image-create/pypi/mirror into the build
environment and temporarily overwrites /root/.pip.conf and .pydistutils.cfg to
use it.

When online, the master pypi index is supplied as an extra-url, so uncached
dependencies will still be available. When offline, only the mirror is used - a
stale mirror will cause build failures.

[jeepyb](https://github.com/openstack-infra/jeepyb) can be useful in making a
partial PyPI mirror suitable for building images. For instance:

 * sudo apt-get install  libxml2-dev libxslt-dev libmysqlclient-dev libpq-dev \
   libnspr4-dev pkg-config libsqlite3-dev libzmq-dev libffi-dev libldap2-dev \
   libsasl2-dev

 * pip install git+https://github.com/openstack-infra/jeepyb

 * cat << EOF > mirror.yaml
   cache-root: /home/USER/.cache/image-create/pypi/download

   mirrors:
    - name: openstack
      projects:
        - https://github.com/openstack/requirements
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
