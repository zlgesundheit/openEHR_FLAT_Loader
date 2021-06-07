#!/bin/bash
script="$(dirname $(dirname $(realpath $0)) )/Scripts/runMain.py"
python3 $script
read -rsp $'Press any key to continue...\n' -n 1 key
# echo $key