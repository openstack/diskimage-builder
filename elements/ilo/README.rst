===
ilo
===
Ramdisk support for applying HP iLO firmware.

The firmware files are copied in via an extra-data hook: the variable
DIB\_ILO\_FIRMWARE\_PATH specifies a directory, and every file in that directory
will be unpacked into a same-named directory in the ramdisk (using
--unpack=...). If the path is not specified, a diagnostic is output but no
error is triggered.

During ramdisk init every found firmware installer will be executed using
--silent --log=log The log is displayed after the firmware has executed.

If the firmware exits with status 0 (ok), status 2 (same or older version) or 4
(ilo not detected) a diagnostic message is logged and init proceeds.

Any other status code is treated as an error.
