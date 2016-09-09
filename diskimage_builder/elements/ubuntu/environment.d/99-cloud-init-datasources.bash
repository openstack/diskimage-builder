# NOTE(adam_g): Until (LP: #1316475) is resolved in Ubuntu, default to only
# allowing the Ec2 data source from being queried on first boot, unless
# specified otherwise.
export DIB_CLOUD_INIT_DATASOURCES=${DIB_CLOUD_INIT_DATASOURCES:-"Ec2"}
