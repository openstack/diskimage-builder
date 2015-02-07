Creating Docker Images
======================

disk-image-create can be used to create a tarball suitable to be imported as a
docker image. To do this you can change the output of disk-image-create to tar
with the -t flag and run docker e.g.

```
disk-image-create -o image -t tar fedora selinux-permissive
```

Assuming you have docker running and have permission to use it, the tarball can
be imported into docker and run.

```
docker import - image:test1 < image.tar
docker  run -t -i  image:test1 /bin/bash
```
