..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==============================================
Example Spec - The title of your specification
==============================================

Introduction paragraph -- why are we doing anything? A single paragraph of
prose that operators can understand. The title and this first paragraph
should be used as the subject line and body of the commit message
respectively.

Some notes about the diskimage-bulider spec process:

* Not all changes need a spec. For more information see
  <add_url_here>

* The aim of this document is first to define the problem we need to solve,
  and second agree the overall approach to solve that problem.

* This is not intended to be extensive documentation for a new feature.

* You should aim to get your spec approved before writing your code.
  While you are free to write prototypes and code before getting your spec
  approved, its possible that the outcome of the spec review process leads
  you towards a fundamentally different solution than you first envisaged.

* But, API changes are held to a much higher level of scrutiny.
  As soon as an API change merges, we must assume it could be in production
  somewhere, and as such, we then need to support that API change forever.
  To avoid getting that wrong, we do want lots of details about API changes
  upfront.

Some notes about using this template:

* Your spec should be in ReSTructured text, like this template.

* Please wrap text at 79 columns.

* Please do not delete any of the sections in this template.  If you have
  nothing to say for a whole section, just write: None

* For help with syntax, see http://sphinx-doc.org/rest.html

* If you would like to provide a diagram with your spec, ascii diagrams are
  required.  http://asciiflow.com/ is a very nice tool to assist with making
  ascii diagrams.  The reason for this is that the tool used to review specs is
  based purely on plain text.  Plain text will allow review to proceed without
  having to look at additional files which can not be viewed in gerrit.  It
  will also allow inline feedback on the diagram itself.


Problem description
===================

A detailed description of the problem. What problem is this blueprint
addressing?

Use Cases
---------

What use cases does this address? What impact on actors does this change have?
Ensure you are clear about the actors in each use case: Developer, End User,
etc.

Proposed change
===============

Here is where you cover the change you propose to make in detail. How do you
propose to solve this problem?

If this is one part of a larger effort make it clear where this piece ends. In
other words, what's the scope of this effort?

At this point, if you would like to just get feedback on if the problem and
proposed change fit in diskimage-builder, you can stop here and post this for
review to get preliminary feedback. If so please say:
Posting to get preliminary feedback on the scope of this spec.

Alternatives
------------

What other ways could we do this thing? Why aren't we using those? This doesn't
have to be a full literature review, but it should demonstrate that thought has
been put into why the proposed solution is an appropriate one.

API impact
----------

Describe how this will effect our public interfaces. Will this be adding new
environment variables? Deprecating existing ones? Adding a new command line
argument?

Security impact
---------------

Describe any potential security impact on the system.

Other end user impact
---------------------

Aside from the API, are there other ways a user will interact with this
feature?

Performance Impact
------------------

Describe any potential performance impact on the system, for example
how often will new code be called, does it perform any intense processing
or data manipulation.

Implementation
==============

Assignee(s)
-----------

Who is leading the writing of the code? Or is this a blueprint where you're
throwing it out there to see who picks it up?

If more than one person is working on the implementation, please designate the
primary author and contact.

Primary assignee:
  <launchpad-id or None>

Other contributors:
  <launchpad-id or None>

Work Items
----------

Work items or tasks -- break the feature up into the things that need to be
done to implement it. Those parts might end up being done by different people,
but we're mostly trying to understand the timeline for implementation.


Dependencies
============

* Include specific references to specs in diskimage-builder or in other
  projects, that this one either depends on or is related to.

* If this requires functionality of another project that is not currently used
  by diskimage-builder document that fact.


Testing
=======

Please discuss the important scenarios needed to test here, as well as
specific edge cases we should be ensuring work correctly. For each
scenario please specify if this requires specialized hardware, or software.

Is this untestable in gate given current limitations (specific hardware /
software configurations available)? If so, are there mitigation plans (gate
enhancements, etc).


Documentation Impact
====================

Which audiences are affected most by this change, and which documentation
files need to be changed. Do we need to add information about this change to
the developer guide, the user guide, certain elements, etc.

References
==========

Please add any useful references here. You are not required to have any
reference. Moreover, this specification should still make sense when your
references are unavailable. Examples of what you could include are:

* Links to mailing list or IRC discussions

* Links to notes from a summit session

* Links to relevant research, if appropriate

* Related specifications as appropriate

* Anything else you feel it is worthwhile to refer to
