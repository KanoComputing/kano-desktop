#!/bin/bash
#
# KDesk icon exits script - Dynamically update the desktops icons attributes.
#

icon_name="$1"
logfile=/tmp/iconexits.log

case $icon_name in

    "loginregister")
	# Ask kano-profile for the username, experience and level,
	# Then update the icon attributes accordingly.
	echo "Received exit for Desktop Kano Widget, updating status"
	IFS=$'\n'
	kano_statuses=`kano-profile-cli get_stats`
	echo "$kano_statuses"
	for item in $kano_statuses
	do
	    eval line_item=($item)

	    case ${line_item[0]} in
		"get_username:")
		    username=${line_item[1]^}
		    ;;
		"is_registered:")
		    is_registered=${line_item[1]}
		    ;;
		"get_xp:")
		    experience=${line_item[1]}
		    ;;
		"get_level:")
		    level=${line_item[1]}
		    ;;
		"get_avatar:")
		    avatar_folder=${line_item[1]}
		    avatar_file=${line_item[2]}.png
		    ;;
	    esac
	done

        # FIXME: The avatar needs to be decided upon experience, avatar folder and file
	#icon="/usr/share/kano-profile/media/images/avatars/230x180/$avatar_folder/$avatar_file"
	#printf "Icon: $icon\n"

	msg="$username|Level $level"
	printf "Message: $msg\n"
	;;

    *)
	echo "Received exit for icon name: $icon_name - ignoring"
	;;
esac
