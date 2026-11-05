#!/bin/bash
# Same bwrap line as run_sandbox.sh (same isolation, same core cap), running
# nanoda.sh instead of replay.sh; the host's Rust toolchain is bound READ-ONLY
# at its own path (binaries only), cargo writes to a private CARGO_HOME.
R=/home/al/dev/untrusted/replay
RT=/home/al/.rustup/toolchains/stable-x86_64-unknown-linux-gnu
exec taskset -c 0-7 nice -n 19 bwrap \
  --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64 --ro-bind /bin /bin --ro-bind /sbin /sbin \
  --ro-bind /etc /etc --ro-bind /run/systemd/resolve /run/systemd/resolve --proc /proc --dev /dev --tmpfs /tmp --tmpfs /var \
  --tmpfs /home --bind $R/home /home/al --bind $R /replay --ro-bind $RT $RT \
  --unshare-pid --unshare-ipc --unshare-uts --die-with-parent \
  --setenv HOME /home/al --setenv USER al --setenv TERM dumb \
  --chdir /replay -- /bin/bash /replay/nanoda.sh
