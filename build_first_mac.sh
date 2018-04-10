#!/bin/bash

echo 'First build for Mac'

cd buildspace/tree

BASE_DIR=$(pwd)
if [ ! -d "${BASE_DIR}/ungoogled_packaging" ]; then
    echo "Wrong base directory: ungoogled_packaging/ not found"
    exit 1;
fi

rm -rf ${BASE_DIR}/out || true
mkdir ${BASE_DIR}/out
mkdir ${BASE_DIR}/out/Default

${BASE_DIR}/tools/gn/bootstrap/bootstrap.py -o ${BASE_DIR}/out/Default/gn -s -j 2
${BASE_DIR}out/Default/gn gen ${BASE_DIR}/out/Default --args='enable_ac3_eac3_audio_demuxing=true enable_google_now=false enable_hangout_services_extension=false enable_hevc_demuxing=true enable_iterator_debugging=false enable_mdns=false enable_mse_mpeg2ts_stream_parser=true enable_nacl=false enable_nacl_nonsfi=false enable_one_click_signin=false enable_reading_list=false enable_remoting=false enable_reporting=false enable_service_discovery=false enable_swiftshader=false enable_widevine=true exclude_unwind_tables=true fatal_linker_warnings=false ffmpeg_branding="Chrome" fieldtrial_testing_like_official_build=true google_api_key="" google_default_client_id="" google_default_client_secret="" is_debug=false optimize_webui=false proprietary_codecs=true remove_webcore_debug_symbols=true rtc_libvpx_build_vp9=false safe_browsing_mode=0 symbol_level=0 treat_warnings_as_errors=false use_gnome_keyring=false use_official_google_api_keys=false use_ozone=false use_sysroot=false use_unofficial_version_number=false clang_use_chrome_plugins=false is_clang=true use_jumbo_build=true' ${BASE_DIR}/out/Default

ninja -j 12 -C ${BASE_DIR}/out/Default chrome