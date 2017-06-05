=============
dib-run-parts
=============

.. warning::

   This element is deprecated and is left only for compatibility.
   Please read the notes.

This element install the ``dib-utils`` package to provide
``dib-run-parts``.

Previously this element was a part of most base images and copied the
internal version of ``dib-run-parts`` to ``/usr/local/bin`` during the
build.  Due to a (longstanding) oversight this was never removed and
stayed in the final image.  The image build process now uses a private
copy of ``dib-run-parts`` during the build, so this element has become
deprecated.

For compatibility this element simply installs the ``dib-utils``
package, which will provide ``dib-run-parts``.  However, this is
probably better expressed as a dependency in individual elements.
