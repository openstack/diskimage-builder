================================
diskimage-builder Specifications
================================

Overview
========

This directory is used to hold approved design specifications for changes to
the diskimage-builder project. Reviews of the specs are done in gerrit, using a
similar workflow to how we review and merge changes to the code itself. For
specific policies around specification review, refer to the end of this
document.

The layout of this directory is::

  specs/v<major_version>/

Where there are two sub-directories:

- specs/v<major_version>/approved: specifications approved but not yet
  implemented
- specs/v<major_version>/implemented: implemented specifications
- specs/v<major_version>/backlog: unassigned specifications

The lifecycle of a specification
--------------------------------

Developers proposing a specification should propose a new file in the
``approved`` directory. diskimage-builder-core will review the change in the
usual manner for the project, and eventually it will get merged if a consensus
is reached.

When a specification has been implemented either the developer or someone
from diskimage-builder-core will move the implemented specification from the
``approved`` directory to the ``implemented`` directory. It is important to
create redirects when this is done so that existing links to the approved
specification are not broken. Redirects aren't symbolic links, they are
defined in a file which sphinx consumes. An example is at
``specs/v1/redirects``.

This directory structure allows you to see what we thought about doing,
decided to do, and actually got done. Users interested in functionality in a
given release should only refer to the ``implemented`` directory.

Example specifications
----------------------

You can find an example spec in :doc:`v1/approved/v1-template`

Backlog specifications
----------------------

Additionally, we allow the proposal of specifications that do not have a
developer assigned to them. These are proposed for review in the same manner as
above, but are added to::

  specs/backlog/approved

Specifications in this directory indicate the original author has either
become unavailable, or has indicated that they are not going to implement the
specification. The specifications found here are available as projects for
people looking to get involved with diskimage-builder. If you are interested in
claiming a spec, start by posting a review for the specification that moves it
from this directory to the next active release. Please set yourself as the new
`primary assignee` and maintain the original author in the `other contributors`
list.

Specification review policies
=============================

There are some special review policies which diskimage-builder-core will apply
when reviewing proposed specifications. They are:

Trivial specifications
----------------------

Proposed changes which are trivial (very small amounts of code) and don't
change any of our public APIs are sometimes not required to provide a
specification. The decision of whether something is trivial or not is a
judgement made by the author or by consensus of the project cores, generally
trying to err on the side of spec creation.

Approved Specifications
=======================

.. toctree::
   :glob:

   v1/approved/*
