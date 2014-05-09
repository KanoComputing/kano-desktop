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

	# Update the message area with username and current level
	msg="$username|Level $level"
	printf "Message: $msg\n"

	# Update the icon with user's avatar and experience level icon
	# TODO : kano-profile-cli needs to provide paths to these files
	#experience_icon="/some/path/"
	#avatar_icone="/some/path/"
	#printf "Icon: $experience_icon\n"
	#printf "IconStamp: $avatar_icon\n"
	;;

    *)
	echo "Received exit for icon name: $icon_name - ignoring"
	;;
esac
