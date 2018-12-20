#!/usr/bin/env bash

tar cJf pycon.tar.xz python_console.py console_lib_tools.py default_functions.py custom_functions.py runscript.sh
rm python_console.py console_lib_tools.py default_functions.py custom_functions.py runscript.sh
rm $0
