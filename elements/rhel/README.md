# Overrides:

## General
* Downloading the Red Hat Enterprise Linux cloud image requires a valid Red Hat Network login and a subscription to Red Hat Enterprise Linux 6 Server product.
* diskimage-builder does not integrate directly with RHN, so a manual download is required.  Please visit https://rhn.redhat.com/rhn/software/channel/downloads/Download.do?cid=16952 to download the qcow2 file.
* Set DIB_CLOUD_IMAGES to "file:///download_path"
* Overriding of DIB_RELEASE is necessary when a new version of the RHEL qcow2 image is available and the default image has not yet been updated in diskimage-builder.

## Red Hat Subscription Manager (RHSM)

Certificate-based Red Hat Subscription Management (RHSM) is the default registration type.

* Set DIB_RHSM_USER and DIB_RHSM_PASSWORD to register the system with RHSM during the image building process. This will apply the associated Red Hat Enterprise Linux Server subscription so the latest package updates can be applied. At the end of the image building process, the system will be unregistered from RHSM.
* Set DIB_RHSM_POOL to a subscription pool if you do not want the system to use the `--auto-attach` feature of `subscription-manager`.
* Set DIB_RHSM_REPOS to a space-separated list of Red Hat repositories to enable.

## Red Hat Network (RHN)

Set `DIB_REG_TYPE=rhn` for Red Hat Network (RHN classic) registration. The image building process will register the system to RHN and apply the associated Red Hat Enterprise Linux Server subscription so the latest package updates can be applied. At the end of the image building process, the system will be unregistered from RHN.

* For RHN username/password authentication set DIB_RHSM_USER and DIB_RHSM_PASSWORD. To use a Satellite server activation key set DIB_SAT_KEY. If adding RHN channels username and password must be set.
* When registering to Satellite set DIB_SAT_URL to the Satellite server URL and DIB_SAT_CERT_RPM_URL to the Satellite certificate.
* Set DIB_RHN_CHANNELS to a space-separated list of RHN channels to add. Example: `DIB_RHN_CHANNELS=rhel-x86_64-server-6 rhel-x86_64-server-6-rhscl-1`. RHN username/password is required for this.
