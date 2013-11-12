#!/usr/bin/env python
#
# file: kanoconnect.py
# desc: This script attempts to find an open wireless network and connect to it.
#       Additionally it is capable of reconnecting to secure networks associated to by kwifiprompt.
# usage:
#
#   Case 1: Attempt connection to the strongest wireless non-secure network
#   $ sudo kanoconnect.py wlan0
#
#   Case 2: Attempt connection to a specified open network
#   $ sudo kanoconnect.py wlan0 essidname
#
#   Case 3: If the last cached network is found during scan, try to connect to it (secure / unsecure)
#   $ sudo kanoconnect.py -c wlan0
#
# It might take some time for this script to finalise, depending on the wireless networks
# in range, their signal strenght and response times to acquire a DHCP lease.
#
# Portions of this code are extracted from the project pywilist:
#
#   https://code.google.com/p/pywilist/
#
# The script needs root permissions. It is good to trigger it from
# /etc/network/interfaces post-up event.
#

import os, sys, syslog
import atexit

sys.path.append('/usr/sbin')
from kwififuncs import IWList, is_device, is_connected, connect, disconnect, remove_pid, KwifiCache

# filename to keep our process semaphore
pidfile = '/var/run/kanoconnect.py'

def attempt_connect(wiface, essid, encryption, enckey):    

    try:
        syslog.syslog("Attempting connection to ESSID '%s' through %s" % (essid, wiface))
        connect (wiface, essid, encryption, seckey=enckey)
        syslog.syslog("CONNECTED to ESSID '%s' through interface %s" % (network['essid'], wiface))
        return True
    except:
        syslog.syslog("could not connect to essid '%s'" % (essid))
        return False

if __name__  ==  '__main__':
    wcache = KwifiCache()
    essid = None
    fsilent = False
    cached_connect = False
    fconnected = False

    syslog.openlog(logoption=syslog.LOG_PID)
    syslog.syslog ('autoconnect is starting')

    if not os.getuid() == 0:
        syslog.syslog ('you need root privileges')
        print 'You need root privileges to start this app. Please try sudo'
        sys.exit (1)

    # kanoconnect cannot work while kanowifi is running.
    # Keep a pid file to semaphore our process
    if os.access('/var/run/kanowifi.py', os.R_OK):

        print 'Kanowifi.py is running, please close it before running kanoconnect.py'
        sys.exit(1)
    else:
        if os.access(pidfile, os.R_OK):
            syslog.syslog ('you need root privileges')
            print 'An instance of Kanoconnet.py is already running.'
            sys.exit(1)
        else:
            atexit.register(remove_pid, pidfile)
            frun = open (pidfile, 'w')
            frun.write (str(os.getpid()))
            frun.close()

    # TODO: Use getopt to collect parameters in a more clear way
    if len(sys.argv) < 2:
        print 'Syntax: kanoconnect.py [-c] <iface> [essid]'
        print '-c will try to connect to the latest cached network'
        sys.exit(1)
    else:
        if sys.argv[1] == '-c':
            if len(sys.argv) < 3:
                syslog.syslog ('need a wireless device name')
                print 'need wireless interface device'
                sys.exit(1)
            else:
                cached_connect = True
                wiface = sys.argv[2]
        else:
            wiface = sys.argv[1]
            if len(sys.argv) > 2:
                essid = sys.argv[2]

        # check if wireless dongle is plugged in
        if not is_device(wiface):
            syslog.syslog ('wireless device %s is not plugged in' % (wiface))
            sys.exit(2)

        # if cache connect mode, and there is no cached network, stop wasting time.
        if cached_connect:
            last_cached = wcache.get_latest()
            if not last_cached:
                syslog.syslog ('cache mode requested but no cached network found - exiting')
                sys.exit(2)

        # scan for wireless networks (twice to sanely fill the scan buffer completely)
        syslog.syslog('Scanning open hotspots through interface %s' % (wiface))
        iwl = IWList(wiface).getList(unsecure=False)
        iwl = IWList(wiface).getList(unsecure=False)
        iwl = IWList(wiface).getList(unsecure=False)
        if not iwl or len(iwl) == 0:
            syslog.syslog('No open networks found - exiting')
            sys.exit(1)

        # If cached mode, see if the cached network has been scanned, if so then try to connect.
        if last_cached:
            for network in iwl:
                if network['essid'] == last_cached['essid']:
                    fconnected = attempt_connect (wiface, network['essid'], network['encryption'],
                                                  last_cached['enckey'])
                    if fconnected:
                        sys.exit(0)
                    else:
                        sys.exit(1)

            # The last cached network is not in range.
            syslog.syslog('Cached network "%s" is not in range - exiting' % (last_cached['essid']))
            sys.exit (2)

        # attempt to connect to the specified wireless network name
        if not essid == None:
            iwl = IWList(wiface).getList(unsecure=True)
            for network in iwl:
                if essid == network['essid']:
                    fconnected = attempt_connect (wiface, essid, None, None)

            if fconnected:
                sys.exit(0)
            else:
                sys.exit(1)

        for scan_attempts in range(1, 3):
            disconnect(wiface)

            # Will only try to connect to strongest signal wireless network
            iwl = IWList(wiface).getList(unsecure=True, first=True)
            for network in iwl:
                essid = network['essid']
                fconnected = attempt_connect (wiface, essid, None, None)
                if fconnected:
                    sys.exit(0)

    syslog.syslog('Could not connect to any open wireless networks through iface %s - Exiting.' % (wiface))
    sys.exit(1)
