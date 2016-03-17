#!/bin/bash

# icon-hooks.sh
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
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

# Name of pipe for Kano Notifications desktop widget
pipe_filename="$HOME/.kano-notifications.fifo"

# default return code
rc=0

case $icon_name in

    "world")
        IFS=$'\n'
        # Returns if online, prints notification count and stats activity
        info=`kano-profile-cli get_world_info`
        apirc=$?

        if [ "$debug" == "true" ]; then
            printf "Kano Profile API returns rc=$apirc, data=\n$info\n"
        fi

        msg1="Kano World"
        icon="/usr/share/kano-desktop/icons/kano-world-launcher.png"

        # Uncomment line below to test your own notifications
        #info="notifications_count: 18"

        # Online / Offline status message
        if [ "$apirc" == "0" ]; then
            notification_icon="/usr/share/kano-desktop/images/world-numbers/minus.png"
            msg2="SIGN UP"
        else
            # We are online, get how many notifications are on the queue and the activity stats
            notification_icon=""
            msg2="ONLINE"
            notifications=$(echo "$info" | awk '/notifications_count:/ {printf "%s", $2}')
            if [ -n "$notifications" ]; then
                # Extract numbers only - Any string will become 0 which means no notifications.
                if [ $notifications -lt 10 ] && [ $notifications -gt 0 ]; then
                    notification_icon="/usr/share/kano-desktop/images/world-numbers/${notifications}.png"
                elif [ $notifications -gt 9 ]; then
                    notification_icon="/usr/share/kano-desktop/images/world-numbers/9-plus.png"
                fi
            fi
            active_online=$(echo "$info" | awk '/total_active_today:/ {printf "%s", $2}')
            if [ -n "$active_online" ]; then
                msg2=$(printf "%d ONLINE" ${active_online})
            fi
        fi

        # Update the icon with the values
        printf "Icon: $icon\n"
        printf "Message: {75,38} $msg1|$msg2\n"
        printf "IconStatus: {30,53} $notification_icon\n"
        ;;


    "ScreenSaverStart")
        # By default we let the screen saver kick in
        if [ "$debug" == "true" ]; then
            echo "Received hook for Screen Saver Start"
        fi
        rc=0

        # disable Notifications Widget alerts momentarily until the screen saver stops
        if [ -p "$pipe_filename" ]; then
            echo "pause" >> $pipe_filename
        fi

        #
        # Search for any programs that should not play along with the screen saver
        # process names are pattern matched, so kano-updater will also find kano-updater-gui.
        IFS=" "
        non_ssaver_processes="kano-updater kano-xbmc xbmc.bin minecraft-pi omxplayer"
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
                echo "starting kano-sync and checking for updates"
            fi
            kano-sync --skip-kdesk --sync --backup --upload-tracking-data -s &
            sudo /usr/bin/kano-updater download --low-prio &
        fi
        ;;

    "ScreenSaverFinish")
        if [ "$debug" == "true" ]; then
            echo "Received hook for Screen Saver Finish"
        fi

        # re-enable notifications widget UI alerts so they popup on the now visible Kano Desktop
        if [ -p "$pipe_filename" ]; then
            echo "resume" >> $pipe_filename
        fi

        # kanotracker collects how many times and for long the screen saver runs
        length=$2
        now=$(date +%s)
        started=$(expr $now - $length)
        kano-tracker-ctl session log screen-saver $started $length
        ;;

    *)
    echo "Received hook for icon name: $icon_name - ignoring"
    ;;
esac

if [ "$debug" == "true" ]; then
    echo "Icon hooks returning rc=$rc"
fi

exit $rc
