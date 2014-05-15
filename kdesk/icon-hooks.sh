#!/bin/bash
#
# KDesk Icon Hooks script - Dynamically update the desktops icons attributes.
#
# You can debug this hook script manually like so:
#
#  $ icon-hooks "myiconname" debug
#

# We don't care about case sensitiveness for icon names
shopt -s nocasematch

# collect command-line parameters
icon_name="$1"
if [ "$2" == "debug" ]; then
    debug="true"
fi

case $icon_name in

    "profile")
    # Ask kano-profile for the username, experience and level,
    # Then update the icon attributes accordingly.
    echo "Received hook call for $icon_name, updating attributes.."
    IFS=$'\n'
    kano_statuses=`kano-profile-cli get_stats`

    # Uncomment me to debug kano profile API
    if [ "$debug" == "true" ]; then
	printf "Kano Profile API returns:\n$kano_statuses\n"
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
    printf "Message: $msg\n"

    # Update the icon with user's avatar and experience level icon
    printf "Icon: $progress_file\n"
    printf "IconStamp: $avatar_file\n"
    ;;

    *)
    echo "Received exit for icon name: $icon_name - ignoring"
    ;;
esac
