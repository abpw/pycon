#!/usr/bin/env bash

# create the destination directory and unzip into it
mkdir ~/.pycon
tar xfk pycon.tar.xz -C ~/.pycon/
if [ $? -ne 0 ] ; then
  echo "Extraction failed: exiting"
  exit 1
fi

# add the pycon command for the current user for future sessions
if [ -f ~/.bashrc ] ; then
  sed -i "/# add the pycon command to bash/d" ~/.bashrc
  sed -i "/source ~\/.pycon\/runscript.sh/d" ~/.bashrc
  echo "# add the pycon command to bash" >> ~/.bashrc
  echo "source ~/.pycon/runscript.sh" >> ~/.bashrc
else
  echo "No ~/.bashrc file found!"
  echo "Pycon installation won't persist between bash sessions."
  source ~/.pycon/runscript.sh
  exit 0
fi

# add the "pycon" command to the current bash session
source ~/.pycon/runscript.sh

rm pycon.tar.xz
rm $0
