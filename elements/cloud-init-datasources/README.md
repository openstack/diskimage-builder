Configures cloud-init to only use an explicit list of data sources.

Cloud-init contains a growing collection of data source modules and most
are enabled by default.  This causes cloud-init to query each data source
on first boot.  This can cause delays or even boot problems depending on your
environment.

You must define `DIB_CLOUD_INIT_DATASOURCES` as a comma-separated list of valid
data sources to limit the data sources that will be queried for metadata on
first boot.

For instance, to enable only the Ec2 datasource:

    export `DIB_CLOUD_INIT_DATASOURCES`="Ec2"

Or to enable multiple:

    export `DIB_CLOUD_INIT_DATASOURCES`="Ec2, ConfigDrive, OpenStack"

Including this element without setting `DIB_CLOUD_INIT_DATASOURCES` will cause
image builds to fail.
