Invocation
==========

The scripts can generally just be run. Options can be set on the command line
or by exporting variables to override those present in lib/img-defaults. -h to
get help.
The image building scripts expect to be able to invoke commands with sudo, so if you
want them to run non-interactively, you should either run them as root, with
sudo -E, or allow your build user to run any sudo command without password.

Using the variable ELEMENTS\_PATH will allow to specify multiple elements locations.
It's a colon (:) separated path list, and it will work in a first path/element found,
first served approach. The included elements tree is used when no path is supplied,
and is added to the end of the path if a path is supplied.

By default, the image building scripts will not overwrite existing disk images,
allowing you to compare the newly built image with the existing one. To change
that behaviour, set the variable OVERWRITE\_OLD\_IMAGE to any value that isn't
0.
