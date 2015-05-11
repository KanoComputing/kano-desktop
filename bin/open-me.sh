#!/bin/bash

#
# Copyright (C) 2014,2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# Execute this file to receive the File Finder badge
#

clear
typewriter_echo "{{3 Nicely done $USER, you found me! }}" 0 2 0 0
clear
# Play rabbit animation
python /usr/lib/python2.7/dist-packages/kano_init/ascii_art/rabbit.py 1 left-to-right
# Unlock the easter egg badge
/usr/bin/kano-profile-cli increment_app_state_variable easter_egg starts 1
