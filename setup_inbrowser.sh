#!/bin/bash

if [ $# -ne 1 ]; then
    echo $0: usage: setup_inbrowser.sh platform {archlinux,debian,linux_simple,windows,macos}
    exit 1
fi

platform=$1

echo 'Setting up for' $platform

mkdir -p buildspace/downloads # Alternatively, buildspace/ can be a symbolic link
./buildkit-launcher.py genbun $platform
./buildkit-launcher.py getsrc
./buildkit-launcher.py subdom
./buildkit-launcher.py genpkg $platform