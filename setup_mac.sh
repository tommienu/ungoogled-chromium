#!/bin/bash

echo 'Setting up for Mac'

mkdir -p buildspace/downloads # Alternatively, buildspace/ can be a symbolic link
./buildkit-launcher.py genbun macos
./buildkit-launcher.py getsrc
./buildkit-launcher.py subdom
./buildkit-launcher.py genpkg macos