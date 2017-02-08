python-brickclient
==================

* This element is aimed for providing cinder local attach/detach
  functionality.

* Currently the feature has a dependency on a known bug
  `<https://launchpad.net/bugs/1623549>`__, which has been resolved
  and will be part of the upstream with the next release of
  ``python-brick-cinderclient-ext``.  Note: Current version of
  ``python-brick-cinderclient-ext`` i.e. 0.2.0 requires and update to
  be made in Line32 for
  ``/usr/share/python-brickclient/venv/lib/python2.7/site-packages/brick_cinderclient_ext/__init__.py``:
  update ``brick-python-cinderclient-ext`` to
  ``python-brick-cinderclient-ext``.

Usage
-----

Pass the below shell script to parameter ``user-data`` and set
``config-drive=true`` at the time of provisioning the node via
nova-boot to make cinder local attach/detach commands talk to your
cloud controller.

.. code-block:: bash

   #!/bin/bash
   FILE="/etc/bash.bashrc"
   [ ! -f "$FILE" ] && touch "$FILE"
   echo 'export OS_AUTH_URL="http://<controller_ip>:5000/v2.0"' >> "$FILE"
   echo 'export OS_PASSWORD="password"'  >> "$FILE"
   echo 'export OS_USERNAME="demo"' >> "$FILE"
   echo 'export OS_TENANT_NAME="demo"'  >> "$FILE"
   echo 'export OS_PROJECT_NAME="demo"' >> "$FILE"
   exec bash

 To attach: ``/usr/share/python-brickclient/venv/bin/cinder local-attach <volume_id>``
 To detach: ``/usr/share/python-brickclient/venv/bin/cinder local-detach <volume_id>``

Alternatively, the same action can be completed manually at the node
which does not require setting up of config drive such as:

.. code-block:: bash

   /usr/share/python-brickclient/venv/bin/cinder \
     --os-username demo --os-password password \
     --os-tenant-name demo --os-project-name demo \
     --os-auth-url=http://<controller_ip>:5000/v2.0 local-attach <volume_id>
