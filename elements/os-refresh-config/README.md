Install os-refresh-config.

os-refresh-config uses run-parts to run scripts in a pre-defined set
of directories. Its intended purpose is to quiesce (pre-configure.d),
configure (configure.d), migrate (migration.d), and then activate
(post-configure.d) a configuration on first boot or in response to Heat
Metadata changes.

To cause a script to be run on every os-refresh-config run, install
it into one of the following directories:
````
/opt/stack/os-refresh-config/pre-configure.d
/opt/stack/os-refresh-config/configure.d
/opt/stack/os-refresh-config/migration.d
/opt/stack/os-refresh-config/post-configure.d
```

If you want to have os-refresh-config run on any updates to a particular
Resource in the heat stack, you will need at the minimum the following snippet
of json in this instance's Metadata:

{
  "OpenStack::Config": {
    "heat":
      "access_key_id": {"Ref": "ApiKeyResource"},
      "secret_key": {"Fn::GetAtt": [ "ApiKeyResource", "SecretAccessKey" ]},
      "refresh": [ {"resource": "SomeResource"} ],
      "stack": {Ref: 'AWS::Stack'},
      "region": {Ref: 'AWS::Region'}
    }
  }
}
