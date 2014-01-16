Start getty on ttyS0 and/or ttyS1

With ILO and other remote admin environments, having a serial console can be
useful for debugging and troubleshooting.

For upstart:
  If ttyS1 exists, getty will run on that, otherwise on ttyS0.

For systemd:
  Try to start getty on both ttyS0 and ttyS1.
