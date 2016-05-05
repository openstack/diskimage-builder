dib-lint
========

dib-lint provides a way to check for common errors in diskimage-builder
elements.  To use it, simply run the ``dib-lint`` script in a directory
containing an ``elements`` directory.  The checks will be run against
every file found under ``elements``.

The following is a list of what is currently caught by dib-lint:

* executable: Ensure any files that begin with #! are executable
* indent: Ensure that all source code is using an indent of four spaces
* element-deps ordering: Ensure all element-deps files are alphabetized
* /bin/bash: Ensure all scripts are using bash explicitly
* sete: Ensure all scripts are set -e
* setu: Ensure all scripts are set -u
* setpipefail: Ensure all scripts are set -o pipefail
* dibdebugtrace: Ensure all scripts respect the DIB_DEBUG_TRACE variable
* tabindent: Ensure no tabs are used for indentation
* newline: Ensure that every file ends with a newline
* mddocs: Ensure that only markdown-formatted documentation is used
* yaml validation: Ensure that any yaml files in the repo have valid syntax

Some of the checks can be omitted, either for an entire project or for an
individual file.  Project exclusions go in tox.ini, using the following
section format::

    [dib-lint]
    ignore=sete setpipefail

This will cause the set -e and set -o pipefail checks to be ignored.

File-specific exclusions are specified as a comment in the relevant file,
using the following format::

    # dib-lint: disable=sete setpipefail

This will exclude the same tests, but only for the file in which the comment
appears.

Only some of the checks can be disabled.  The ones available for exclusion are:

* executable
* indent
* sete
* setu
* setpipefail
* dibdebugtrace
* tabindent
* newline
* mddocs
