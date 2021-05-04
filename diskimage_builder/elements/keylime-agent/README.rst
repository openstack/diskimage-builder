=============
keylime-agent
=============

Presently, we rely upon a certain level of trust for users that leverage
baremetal resources. While we do perform cleaning between deployments,
a malicious attacker could potentially modify firmware of attached devices
in ways that may or may not be readily detectable.

The solution that has been proposed for this is the use of a measured launch
environments with engagement of Trusted Platform Management (TPM) modules to
help ensure that the running system profile is exactly as desired or approved,
by the attestation service.

To leverage TPM's for attestation, we propose Keylime,
an open source remote boot attestation and
runtime integrity measurement system. Keylime agent is a component of the
Keylime suite which runs on the baremetal node we are attesting
during cleaning and deployment steps. Keylime regisrar is
a database of all agents registered with Keylime
and hosts the public keys of the TPM vendors.

In order to enhance the ramdisk to support TPM 2.0 and Keylime,
this keylime-agent element is proposed. This element provides
configurations for Keylime agent to communicate with Keylime server.
Keylime agent runs as a system service to collect
Integrity Measurement Architecture (IMA) measurement lists and
send the measurements to the Keylime verifier for attestation.

Environment Variables
---------------------

DIB_KEYLIME_AGENT_REGISTRAR_IP
  :Required: Yes
  :Default: 0
  :Description: The IP address of Keylime registrar server
    which Keylime agent communicates with.

DIB_KEYLIME_AGENT_REGISTRAR_PORT
  :Required: Yes
  :Default: 8890
  :Description: The port of Keylime registrar server
    which Keylime agent communicates with.

**REFERENCES**

[1] github.com/keylime/
[2] review.opendev.org/c/openstack/ironic-specs/+/576718




