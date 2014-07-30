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
    IFS=$'\n'
    kano_statuses=`kano-profile-cli get_stats`
    apirc=$?

    # Uncomment me to debug kano profile API
    if [ "$debug" == "true" ]; then
        echo "Received hook call for $icon_name, updating attributes.."
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


    "world")
	IFS=$'\n'

	# FIXME: Replace below line when API is ready
	kano_statuses=`kano-profile-cli get_notifications`
	apirc=$?

	if [ "$debug" == "true" ]; then
	    printf "Kano Profile API returns rc=$apirc, data=\n$kano_statuses\n"
	fi

	msg="Kano World"
	icon="/usr/share/kano-desktop/icons/kano-world-launcher.png"

	for item in $kano_statuses
	do
	    eval line_item=($item)
	    case ${line_item[0]} in
		"notifications:")
		    notifications=${line_item[1]}
		    if [ "$notifications" != "0" ]; then
			icon="/usr/share/kano-desktop/icons/kano-world-launcher-alerts.png"
			msg="$msg|$notifications notifications!"
		    fi
		    ;;
	    esac
	done

	printf "Icon: $icon\n"
	printf "Message: $msg\n"
	;;


    "ScreenSaverStart")
        # By default we let the screen saver kick in
        if [ "$debug" == "true" ]; then
            echo "Received hook for Screen Saver Start"
        fi
        rc=0

        #
        # Search for any programs that should not play along with the screen saver
        # process names are pattern matched, so kano-updater will also find kano-updater-gui.
        non_ssaver_processes="kano-updater kano-xbmc xbmc-bin minecraft-pi omxplayer"
        for p in $non_ssaver_processes
        do
            isalive=`pgrep -f "$p"`
            if [ "$isalive" != "" ]; then
                if [ "$debug" == "true" ]; then
                    echo "cancelling screen saver because process '$p' is running"
                fi
		rc=1
		break
	    fi
	done

	if [ "$rc" == "0" ]; then
            if [ "$debug" == "true" ]; then
	        echo "starting kano-sync and check-for-updates"
            fi
	    kano-sync --backup -s &
	    sudo /usr/bin/check-for-updates -t 24 -d &
	fi
	;;

    "ScreenSaverFinish")
        if [ "$debug" == "true" ]; then
            echo "Received hook for Screen Saver Finish"
        fi

        # kanotracker collects how many times and for long the screen saver runs
        timerun=$2
        kano-profile-cli increment_app_runtime screen-saver $timerun
        ;;

    *)
    echo "Received hook for icon name: $icon_name - ignoring"
    ;;
esac

if [ "$debug" == "true" ]; then
    echo "Icon hooks returning rc=$rc"
fi

exit $rc
