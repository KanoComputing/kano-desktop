#!/usr/bin/env bash

# Kano OS helper aliases

# ifconfig alias
alias ifconfig='/sbin/ifconfig'

# kanux-version alias
alias kanux-version='cat /etc/kanux_version'

# set time alias using rdate
alias set-time='sudo /usr/bin/rdate -cv $(cat /etc/timeserver.conf)'

# aliases for enabling/disabling the syslog daemon
alias syslog-enable='sudo update-rc.d inetutils-syslogd enable && sudo /etc/init.d/inetutils-syslogd start'
alias syslog-disable='sudo update-rc.d inetutils-syslogd disable && sudo /etc/init.d/inetutils-syslogd stop'

# aliases to enable / disable the root user from ssh logins
alias rootssh-disable='sudo sed -i '\''s/DROPBEAR_EXTRA_ARGS=.*/DROPBEAR_EXTRA_ARGS="-g -w"/g'\'' /etc/default/dropbear && sudo /etc/init.d/dropbear restart'
alias rootssh-enable='sudo sed -i '\''s/DROPBEAR_EXTRA_ARGS=.*/DROPBEAR_EXTRA_ARGS=/g'\'' /etc/default/dropbear && sudo /etc/init.d/dropbear restart'
