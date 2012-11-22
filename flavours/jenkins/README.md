Provisions a jenkins for doing tests of openstack cloud images
==============================================================

After deploying the image, jenkins should be available on port 8080.

*The following is fiction*

To use this, add a new application at
`https://github.com/organizations/$ORGANISATION/settings/applications` and grab
the client id and secret it provides.

Config options
--------------

XXX: These should be passed in via cloud-init or salt, not on image build. For
now, export before building the image.

* export `GITHUB_ORGANISATION` to set the which organisation to look for github
  committers from.

* export `GITHUB_ADMINS` to set a list of github users to be jenkins admins.

* export `GITHUB_CLIENT_ID` to set the github OAuth client id.

* export `GITHUB_SECRET` to set the github OAuth secret.
