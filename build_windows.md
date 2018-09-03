# Building ungoogled-chromium from google sources for windows

Currently ungoogled-chromium uses tag 64.0.3282.186 of the main chromium repo

You should probably have Win10 and disaple MAX_PATH limitation

Steps:
1) Checkout ungoogled-chromium repo
2) Make folder ungoogled-chromium\buildspace\
3) Download and unpack depot_tools to ungoogled-chromium\buildspace\depot_tools ( see https://chromium.googlesource.com/chromium/src/+/master/docs/windows_build_instructions.md )
4) Add ungoogled-chromium\buildspace\depot_tools to windows PATH variable; it should be the first variable
5) In cmd window check "where python", "where ninja", it should point to ungoogled-chromium\buildspace\depot_tools
6) From command line (cmd) make ungoogled-chromium\buildspace\depot_tools current dir:
	cd ungoogled-chromium\buildspace\depot_tools 
7) $ fetch chromium
8) $ cd src
9) Now you have chromium master branch; switch to the tag and build it as described here: https://www.chromium.org/developers/how-tos/get-the-code/working-with-release-branches
 - $ gclient sync --with_branch_heads --with_tags
 - $ fetch --tags
 - $ git checkout -b your_local_tag_branch tags/64.0.3282.186
 - $ gclient sync --with_branch_heads --with_tags
10) Apply ungoogled patches if needed
11) build normally as described at https://chromium.googlesource.com/chromium/src/+/master/docs/windows_build_instructions.md
- $ gn gen out/Default
- $ autoninja -C out\Default chrome

