#!/bin/bash
R=/home/al/dev/untrusted/replay
exec taskset -c 0-7 nice -n 19 bwrap \
  --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64 --ro-bind /bin /bin --ro-bind /sbin /sbin \
  --ro-bind /etc /etc --ro-bind /run/systemd/resolve /run/systemd/resolve --proc /proc --dev /dev --tmpfs /tmp --tmpfs /var \
  --tmpfs /home --bind $R/home /home/al --bind $R /replay \
  --unshare-pid --unshare-ipc --unshare-uts --die-with-parent \
  --setenv HOME /home/al --setenv USER al --setenv TERM dumb \
  --chdir /replay -- /bin/bash /replay/replay.sh
