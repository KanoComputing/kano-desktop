#
# kano-desktop Makefile
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#



all: kano-mount-trigger.target

kano-mount-trigger.target:
	cd kano-mount-trigger && make all
