=========
pip-cache
=========
# Use a cache for pip

Using a download cache speeds up image builds.

Including this element in an image build causes
$HOME/.cache/image-create/pip to be bind mounted as /tmp/pip inside
the image build chroot.  The $PIP_DOWNLOAD_CACHE environment variable
is then defined as /tmp/pip, which causes pip to cache all downloads
to the defined location.

Note that pip and its use of $PIP_DOWNLOAD_CACHE is not concurrency
safe.  Running multiple instances of diskimage-builder concurrently
can cause issues.  Therefore, it is advised to only have one instance
of diskimage-builder that includes the pip-cache element running at a
time.

The pip concurrency issue is being tracked upstream at
https://github.com/pypa/pip/issues/1141
