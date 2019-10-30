vhd creation
============

There is currently a hard dependency on the patched version of
``vhd-utils`` to create Xenserver VHD compatible images.  The main
target for these images is the Rackspace Public Cloud.

This note should explain the current issues.

The patch to include ``convert`` as an option to ``vhd-utils``,
avaialble at https://github.com/citrix-openstack/xenserver-utils/, is
built by infra into a PPA available at
https://launchpad.net/~openstack-ci-core/+archive/ubuntu/vhd-util.

Upstream Xen has actually removed all the code related to ``blktap2``
with
https://xenbits.xen.org/gitweb/?p=xen.git;a=commit;h=5c883cf036cf5ab8b1b79390549e2475f7a568dd.
The tools have been removed from Debuntu with
https://bugs.debian.org/917907. So this patch is even less trivial to
apply; the project has seemingly been split into
https://github.com/xapi-project/blktap/ but support status is unclear.

It is tempting to use ``qemu-img`` image conversion routines.  Indeed
this supports converting RAW images to VPC output.  However, VPC is a
fairly flexible standard across a number of different hypervisors.
The main standard is available from Microsoft at
https://www.microsoft.com/en-us/download/confirmation.aspx?id=23850
and is what ``qemu-img`` impelements.

However, trying to boot an image created with this results in a
"resize" error.  This is described in
https://bugs.launchpad.net/nova/+bug/862653 but comes down to the
following in
https://github.com/xapi-project/blktap/blob/master/vhd/lib/vhd-util-resize.c#L1055::

  if (!vhd_creator_tapdisk(&vhd)) {
     printf("%s not created by xen; resize not supported\n", name);
     err = -EINVAL;
  }

It seems that Xen will refuse to grow a image without a creator
``tap\0``.  It is tempting to patch ``qemu-img`` to do this (patch
follows for those interested).  However, if you look at the output
with ``vhd-util read -p -n ./<file>.vhd`` you will notice it complains
about an invalid ``batmap``.  The ``batmap`` appears to be a Xen
extension to the VPC standard.  Checking ``vhd_has_batmap`` at
https://github.com/xen-project/xen/blob/365aabb6e5023cee476adf81106729efd49c644f/tools/blktap2/vhd/lib/libvhd.c#L1193
it seems we can fool Xen by setting the vhd version tags low enough
that it thinks the image doesn't have a ``batmap`` (i.e. presumably
created with tools before ``batmap``'s existed).

Side note: there is a bunch of qemu work to implement overlay VHD
disks with
https://patchwork.ozlabs.org/project/qemu-devel/list/?submitter=64750
which has never merged.  This also seems to include a ``batmap``
implementation.

With the full patch applied below, we get images that appear fairly
similar from (patched) ``vhd-util`` and ``qemu-img``; generated from
the same ``.raw`` file.

qemu-img output::

   VHD Footer Summary:
   -------------------
   Cookie              : conectix
   Features            : (0x00000002) <RESV>
   File format version : Major: 1, Minor: 0
   Data offset         : 512
   Timestamp           : Wed Oct 30 06:25:41 2019
   Creator Application : 'tap'
   Creator version     : Major: 1, Minor: 0
   Creator OS          : Unknown!
   Original disk size  : 16667 MB (17477591040 Bytes)
   Current disk size   : 16667 MB (17477591040 Bytes)
   Geometry            : Cyl: 33865, Hds: 16, Sctrs: 63
                       : = 16667 MB (17477591040 Bytes)
   Disk type           : Dynamic hard disk
   Checksum            : 0xffffec8c|0xffffec8c (Good!)
   UUID                : 1bfda481-dd4d-43aa-8f3a-84689b5ab3d7
   Saved state         : No
   Hidden              : 0

   VHD Header Summary:
   -------------------
   Cookie              : cxsparse
   Data offset (unusd) : 18446744073709
   Table offset        : 1536
   Header version      : 0x00010000
   Max BAT size        : 8334
   Block size          : 2097152 (2 MB)
   Parent name         : 
   Parent UUID         : 00000000-0000-0000-0000-000000000000
   Parent timestamp    : Sat Jan  1 00:00:00 2000
   Checksum            : 0xfffff3c9|0xfffff3c9 (Good!)

vhd-utils output::

   VHD Footer Summary:
   -------------------
   Cookie              : conectix
   Features            : (0x00000002) <RESV>
   File format version : Major: 1, Minor: 0
   Data offset         : 512
   Timestamp           : Tue Oct  8 09:18:54 2019
   Creator Application : 'tap'
   Creator version     : Major: 1, Minor: 3
   Creator OS          : Unknown!
   Original disk size  : 16668 MB (17477664768 Bytes)
   Current disk size   : 16668 MB (17477664768 Bytes)
   Geometry            : Cyl: 33865, Hds: 16, Sctrs: 63
                       : = 16667 MB (17477591040 Bytes)
   Disk type           : Dynamic hard disk
   Checksum            : 0xffffeebb|0xffffeebb (Good!)
   UUID                : 14f2710a-b9b8-48f7-94bb-005ba6d566b2
   Saved state         : No
   Hidden              : 0

   VHD Header Summary:
   -------------------
   Cookie              : cxsparse
   Data offset (unusd) : 18446744073709
   Table offset        : 1536
   Header version      : 0x00010000
   Max BAT size        : 8334
   Block size          : 2097152 (2 MB)
   Parent name         : 
   Parent UUID         : 00000000-0000-0000-0000-000000000000
   Parent timestamp    : Sat Jan  1 00:00:00 2000
   Checksum            : 0xfffff3c9|0xfffff3c9 (Good!)

   VHD Batmap Summary:
   -------------------
   Batmap offset       : 35840
   Batmap size (secs)  : 3
   Batmap version      : 0x00010002
   Checksum            : 0xfffbf214|0xfffbf214 (Good!)

This does upload and boot in RAX, but the root disk does not appear to
grow correctly.

Emperically, it also seems that fixed sized disks (generated with
``subformat=fixed``) will not import (at least into Rackspace).  I
also tried resizing the dynamic ``vhd`` (with ``vhd-util
resize --debug -n ./test.vhd -s $((32 * 1024 * 1024 )) -j
resize.log``), which looked correct in ``vhd-util`` output (``Current
disk size`` grew) but Rackspace would not import this image.

qemu patch
==========

Applies against qemu at HEAD
``16884391c750d0c5e863f55ad7aaaa146fc5181e``

::

   diff --git a/block/vpc.c b/block/vpc.c
   index a655502..d1716f0 100644
   --- a/block/vpc.c
   +++ b/block/vpc.c
   @@ -60,6 +60,7 @@ enum vhd_type {
    #define VHD_MAX_GEOMETRY      (VHD_CHS_MAX_C * VHD_CHS_MAX_H * VHD_CHS_MAX_S)

    #define VPC_OPT_FORCE_SIZE "force_size"
   +#define VPC_OPT_XENSERVER_COMPAT "xenserver_compat"

    /* always big-endian */
    typedef struct vhd_footer {
   @@ -1042,12 +1043,16 @@ static int coroutine_fn vpc_co_create(BlockdevCreateOptions *opts,
        memset(buf, 0, 1024);

        memcpy(footer->creator, "conectix", 8);
   -    if (vpc_opts->force_size) {
   +    if (vpc_opts->xenserver_compat) {
   +        memcpy(footer->creator_app, "tap\0", 4);
   +        memcpy(footer->creator_os, "\0\0\0\0", 4);
   +    } else if (vpc_opts->force_size) {
            memcpy(footer->creator_app, "qem2", 4);
   +        memcpy(footer->creator_os, "Wi2k", 4);
        } else {
            memcpy(footer->creator_app, "qemu", 4);
   +        memcpy(footer->creator_os, "Wi2k", 4);
        }
   -    memcpy(footer->creator_os, "Wi2k", 4);

        footer->features = cpu_to_be32(0x02);
        footer->version = cpu_to_be32(0x00010000);
   @@ -1058,9 +1063,14 @@ static int coroutine_fn vpc_co_create(BlockdevCreateOptions *opts,
        }
        footer->timestamp = cpu_to_be32(time(NULL) - VHD_TIMESTAMP_BASE);

   -    /* Version of Virtual PC 2007 */
   -    footer->major = cpu_to_be16(0x0005);
   -    footer->minor = cpu_to_be16(0x0003);
   +    if (vpc_opts->xenserver_compat) {
   +        footer->major = cpu_to_be16(0x0001);
   +        footer->minor = cpu_to_be16(0x0000);
   +    } else {
   +        /* Version of Virtual PC 2007 */
   +        footer->major = cpu_to_be16(0x0005);
   +        footer->minor = cpu_to_be16(0x0003);
   +    }
        footer->orig_size = cpu_to_be64(total_size);
        footer->current_size = cpu_to_be64(total_size);
        footer->cyls = cpu_to_be16(cyls);
   @@ -1101,6 +1111,7 @@ static int coroutine_fn vpc_co_create_opts(const char *filename,

        static const QDictRenames opt_renames[] = {
            { VPC_OPT_FORCE_SIZE,           "force-size" },
   +        { VPC_OPT_XENSERVER_COMPAT,     "xenserver-compat" },
            { NULL, NULL },
        };

   @@ -1220,6 +1231,11 @@ static QemuOptsList vpc_create_opts = {
                        "specified, rather than using the nearest CHS-based "
                        "calculation"
            },
   +        {
   +            .name = VPC_OPT_XENSERVER_COMPAT,
   +            .type = QEMU_OPT_BOOL,
   +            .help = "Set creator to tap"
   +        },
            { /* end of list */ }
        }
    };
   diff --git a/qapi/block-core.json b/qapi/block-core.json
   index aa97ee2..68daa3c 100644
   --- a/qapi/block-core.json
   +++ b/qapi/block-core.json
   @@ -4669,6 +4669,7 @@
    # @force-size       Force use of the exact byte size instead of rounding to the
    #                   next size that can be represented in CHS geometry
    #                   (default: false)
   +# @xenserver-compat Xenserver comapt
    #
    # Since: 2.12
    ##
   @@ -4676,7 +4677,9 @@
      'data': { 'file':                 'BlockdevRef',
                'size':                 'size',
                '*subformat':           'BlockdevVpcSubformat',
   -            '*force-size':          'bool' } }
   +            '*force-size':          'bool',
   +            '*xenserver-compat':    'bool'
   +  } }

    ##
    # @BlockdevCreateOptions:
