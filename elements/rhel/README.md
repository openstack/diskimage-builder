Overrides:
* Set DIB_CLOUD_IMAGES to a URL for downloading base Red Hat Enterprise Linux cloud image.
* Set DIB_CLOUD_RELEASE to a use a non-default name for the Red Hat Enterprise Linux cloud image.
* Set DIB_RHSM_USER and DIB_RHSM_PASSOWRD for the RHN user to be used for a subscription registration.
  If these are set, the image building process will register the system with RHN
  and apply the associated Red Hat Enterprise Linux Server subscription so the
  latest package updates can be applied. At the end of the image building
  process, the system will be unregistered from RHN.
* Set DIB_RHSM_POOL to a subscription pool if you want the system to not use
  the auto attach feature of subscription-manager
