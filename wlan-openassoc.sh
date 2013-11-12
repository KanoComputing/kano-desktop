#!/bin/bash
#
# This script should be triggered using post-up and post-down hooks
# in /etc/network/interfaces for the wireless device (wlanX)
# using the following syntax:
#
#   post-up wlan-openassoc.sh up wlan0
#   post-down wlan-openassoc.sh down wlan0
#

if [ "$1" == "up" ]; then
	logger -i "wireless device $2 plugged in"
	python /usr/sbin/kanoconnect.py $2 &
else
	pkill -xf 'python /usr/sbin/kanoconnect.py $2'
	pkill -xf 'dhclient -1 $2'
	logger -i "wireless dongle $2 disconnected"
fi
