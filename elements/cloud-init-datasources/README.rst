======================
cloud-init-datasources
======================

Configures cloud-init to only use an explicit list of data sources.

Cloud-init contains a growing collection of data source modules and most
are enabled by default.  This causes cloud-init to query each data source
on first boot.  This can cause delays or even boot problems depending on your
environment.

Including this element without setting `DIB_CLOUD_INIT_DATASOURCES` will cause
image builds to fail.

Environment Variables
---------------------

DIB_CLOUD_INIT_DATASOURCES
  :Required: Yes
  :Default: None
  :Description: A comma-separated list of valid data sources to limit the data
    sources that will be queried for metadata on first boot.
  :Example: ``DIB_CLOUD_INIT_DATASOURCES="Ec2"`` will enable only the Ec2 data
    source.
  :Example: ``DIB_CLOUD_INIT_DATASOURCES="Ec2, ConfigDrive, OpenStack"`` will
    enable the Ec2, ConfigDrive and OpenStack data sources.

