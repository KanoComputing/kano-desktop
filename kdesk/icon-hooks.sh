#!/bin/bash

# icon-hooks.sh
# 
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#
# KDesk Icon Hooks script - Dynamically update the desktops icons attributes.
#
# You can debug this hook script manually like so:
#
#  $ icon-hooks "myiconname" debug


# we capture errors so we return meaningul responses to kdesk
set +e

# We don't care about case sensitiveness for icon names
shopt -s nocasematch

# collect command-line parameters
icon_name="$1"
if [ "$2" == "debug" ]; then
    debug="true"
fi

# default return code
rc=0

case $icon_name in

    "profile")
    # Ask kano-profile for the username, experience and level,
    # Then update the icon attributes accordingly.
    echo "Received hook call for $icon_name, updating attributes.."
    IFS=$'\n'
    kano_statuses=`kano-profile-cli get_stats`
    apirc=$?

    # Uncomment me to debug kano profile API
    if [ "$debug" == "true" ]; then
	printf "Kano Profile API returns rc=$apirc, data=\n$kano_statuses\n"
    fi

    for item in $kano_statuses
    do
	eval line_item=($item)
	case ${line_item[0]} in
	    "mixed_username:")
		username=${line_item[1]^}
		;;
	    "level:")
		level=${line_item[1]}
		;;
	    "progress_image_path:")
		progress_file=${line_item[1]}
		;;
	    "avatar_image_path:")
		avatar_file=${line_item[1]}
		;;
	esac
    done

    if [ "$debug" == "true" ]; then
	echo -e "\nReturning attributes to Kdesk:\n"
    fi

    # Update the message area with username and current level
    msg="$username|Level $level"
    if [ "$username" != "" ] && [ "$level" != "" ]; then
	printf "Message: $msg\n"
    fi

    # Update the icon with user's avatar and experience level icon
    if [ "$progress_file" != "" ]; then
	printf "Icon: $progress_file\n"
    fi

    if [ "$avatar_file" != "" ]; then
	printf "IconStamp: $avatar_file\n"
    fi
    ;;

    "ScreenSaverStart")
	# Return rc different than zero to cancel the screen saver
        echo "Received exit for Screen Saver Start - starting kano-sync and check-for-updates"
        kano-sync --backup -s &
        sudo /usr/bin/check-for-updates &
	rc=0
	;;

    "ScreenSaverFinish")
        echo "Received exit for Screen Saver Finish"
        ;;

    *)
    echo "Received exit for icon name: $icon_name - ignoring"
    ;;
esac

exit $rc
