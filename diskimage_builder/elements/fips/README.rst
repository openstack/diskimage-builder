====
fips
====

This image element attempts to setup the image so it will boot and operate
in what is often referred to as "FIPS mode", where cryptography policies
and algorithms are enforced to only those which are FIPS approved and
certified. In this context, FIPS is an abbreviation for
Federal Information Processing Standard, specifically publication number
140. You can learn more about FIPS policies at
https://csrc.nist.gov/publications/fips

This element is a best-effort element and additional software or elements
may be processed after the fact which may impact the work of this element.
It is **generally** regarded as critical to enable FIPS as early as possible,
as cryptography policy can be applied, but may not be fully enforced without
the kernel also operating in FIPS mode.

If you intend to utilize this element to generate production FIPS images,
it is highly recommended you do so on a host which has already had FIPS
enabled for itself.

Additionally, not all distributions are explicitly supported. Unsupported
distributions will error providing appropriate guidance, if available.
