#!/bin/bash

# Usage: chrome-rebuild <targets> (e.g. chrome chrome)

echo '(re)Building for Mac'

cd buildspace/tree

BASE_DIR=$(pwd)
if [ ! -d "${BASE_DIR}/out" ]; then
    echo "Wrong base directory: out/ not found"
    exit 1;
fi

if [ $# -lt 1 ]; then
    echo "Missing target"
    exit 1;
fi

# For Intel:
export CC=clang CXX=clang++
export GYP_DEFINES="branding=Chrome use_third_party_translations=0 release_extra_cflags='-g1' werror= sysroot= linux_use_bundled_binutils=0 linux_link_gsettings=1 disable_nacl=1 linux_use_gold_binary=0 linux_use_gold_flags=0 enable_webrtc=1 use_aura=1 enable_hidpi=1 enable_touch_ui=1 enable_hangout_services_extension=1 enable_widevine=1 enable_pepper_cdms=1 clang=1 clang_use_chrome_plugins=0 target_arch=ia32 use_allocator=none disable_sse2=1 remove_webcore_debug_symbols=1 linux_dump_symbols=1 logging_like_official_build=1 use_gnome_keyring=1 linux_link_gnome_keyring=1 use_gconf=0 use_gio=1 component=shared_library proprietary_codecs=1 enable_hangout_services_extension=1"

# For ARM:
# export GYP_CROSSCOMPILE=1
# export GYP_DEFINES="target_arch=arm arm_float_abi=hard component=shared_library linux_use_gold_flags=1 disable_nacl=1 enable_widevine=1 enable_pepper_cdms=1 use_gconf=0 linux_link_gsettings=1 proprietary_codecs=1 use_v4l2_codec=1 arm_neon=1 ffmpeg_branding=Chrome"
# ninja -j4 -C out/Release cdm_common cdm_renderer clearkeycdm clearkeycdmadapter_resources clearkeycdmadapter common plugin  plugins_renderer common chrome

#./build/gyp_chromium --depth=$(pwd)

# How to build chromium in place (after building the package)
rm build-stamp || true
mv "${BASE_DIR}/out/Release" "${BASE_DIR}/out/Release-chromium" > /dev/null || true
mv "${BASE_DIR}/out/Release-chromium" "${BASE_DIR}/out/Release" > /dev/null
ninja -j4 -C ${BASE_DIR}/out/Release $@
mv "${BASE_DIR}/out/Release" "${BASE_DIR}/out/Release-chromium"
touch build-stamp