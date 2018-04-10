#!/bin/bash

echo 'Applying patches'

cd buildspace/tree
set -eux
packaging_dir=$(dirname $(greadlink -f $0))
echo ${packaging_dir}
env QUILT_PATCHES="${packaging_dir}/patches" quilt push -a