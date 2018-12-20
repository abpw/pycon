#!/usr/bin/env bash

function pycon() {
  if [ "$1" == "--uninstall" ] ; then
    sed -i "/# add the pycon command to bash/d" ~/.bashrc
    sed -i "/source ~\/.pycon\/runscript.sh/d" ~/.bashrc
    rm ~/.pycon/console_lib_tools.py
    rm ~/.pycon/default_functions.py
    rm ~/.pycon/python_console.py
    rm ~/.pycon/*.pyc
    rm ~/.pycon/runscript.sh
  elif [ "$1" == "--purge" ] ; then
    sed -i "/# add the pycon command to bash/d" ~/.bashrc
    sed -i "/source ~\/.pycon\/runscript.sh/d" ~/.bashrc
    rm -rf ~/.pycon
  else
    python ~/.pycon/python_console.py "$@"
  fi
}
