#!/bin/bash
#
# KDesk icon exits script - Dynamically update the desktops icons attributes.
#

icon_name="$1"
logfile=/tmp/iconexits.log

case $icon_name in

    "widget")
	# The Desktop Widget icon refreshes with the icon image for current points,
	# And the left-side message with: username and current Kano level.
	echo "Received exit for Desktop Kano Widget, updating status"

	username=`kano-profile-cli get_username`
	level=`kano-profile-cli get_level`
	avatar=(`kano-profile-cli get_avatar`)
	avatar_folder=${avatar[0]}
	avatar_image="${avatar[1]}.png"
	icon="/usr/share/kano-profile/media/images/avatars/230x180/$avatar_folder/$avatar_image"
	
        # TODO: call get_xp to decide which icon needs be rendered
	#printf "Icon: $icon\n"

	printf "Message: Hello ${username^} !|Level $level\n"
	;;

    *)
	echo "Received exit for icon name: $icon_name - ignoring"
	;;
esac
