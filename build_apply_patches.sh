#!/bin/bash

echo 'Applying patches'

cd buildspace/tree
set -eux
packaging_dir=buildspace/tree/ungoogled_packaging
echo ${packaging_dir}
env QUILT_PATCHES="${packaging_dir}/patches" quilt push -a