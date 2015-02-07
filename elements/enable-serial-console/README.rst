=====================
enable-serial-console
=====================
Start getty on active serial consoles.

With ILO and other remote admin environments, having a serial console can be
useful for debugging and troubleshooting.

For upstart:
  If ttyS1 exists, getty will run on that, otherwise on ttyS0.

For systemd:
  We dynamically start a getty on any active serial port via udev rules.
